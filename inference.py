from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import onnxruntime as ort
from PIL import Image


MODEL = Path(__file__).with_name("stars-speck-character-skin-v1-pro-b2-fp32-dynamic.onnx")
MEAN = np.asarray((0.485, 0.456, 0.406), dtype=np.float32)
STD = np.asarray((0.229, 0.224, 0.225), dtype=np.float32)


def prepare(image: Image.Image, long_edge: int) -> tuple[np.ndarray, tuple[int, int], tuple[int, int]]:
    scale = long_edge / max(image.size)
    resized_size = tuple(max(1, round(value * scale)) for value in image.size)
    resized = image.resize(resized_size, Image.Resampling.BILINEAR)
    padded_size = tuple(((value + 31) // 32) * 32 for value in resized_size)
    canvas = Image.new("RGB", padded_size)
    canvas.paste(resized, (0, 0))
    tensor = np.asarray(canvas, dtype=np.float32) / 255.0
    tensor = ((tensor - MEAN) / STD).transpose(2, 0, 1)[None]
    return tensor, resized_size, padded_size


def main() -> None:
    parser = argparse.ArgumentParser(description="Stars Speck Character Skin V1 Pro inference")
    parser.add_argument("image", type=Path)
    parser.add_argument("--model", type=Path, default=MODEL)
    parser.add_argument("--output", type=Path, default=Path("skin_probability.png"))
    parser.add_argument("--overlay", type=Path)
    parser.add_argument("--long-edge", type=int, choices=(512, 1024), default=1024)
    args = parser.parse_args()

    with Image.open(args.image) as source:
        image = source.convert("RGB")
    tensor, resized_size, _ = prepare(image, args.long_edge)
    session = ort.InferenceSession(str(args.model), providers=["CPUExecutionProvider"])
    probability = session.run(["skin_probability"], {"image": tensor})[0][0, 0]
    probability = probability[: resized_size[1], : resized_size[0]]
    probability = np.asarray(
        Image.fromarray(probability, mode="F").resize(image.size, Image.Resampling.BILINEAR),
        dtype=np.float32,
    )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    mask = Image.fromarray(np.uint8(np.clip(probability, 0, 1) * 255), mode="L")
    mask.save(args.output)
    if args.overlay:
        args.overlay.parent.mkdir(parents=True, exist_ok=True)
        red = Image.new("RGB", image.size, (255, 24, 24))
        overlay_alpha = mask.point(lambda value: round(value * 0.62))
        Image.composite(red, image, overlay_alpha).save(args.overlay, quality=95)
    print(f"saved probability map: {args.output}")


if __name__ == "__main__":
    main()
