# Stars Speck Character Skin V1 Pro — Test Report

## Scope

The release candidate was checked with the exported ONNX graph at 1024-pixel inference resolution. The qualitative suite covers clear portraits, full-body subjects, multiple people, dark skin, outdoor lighting, monochrome images, elderly people, children, complex clothing and distant subjects.

The four bundled examples were selected for clarity and reproducibility. They retain their original licenses and are not pixel-annotated accuracy benchmarks.

## Export verification

PyTorch-to-ONNX numerical comparison passed for all tested shapes:

| Shape | Maximum absolute error |
|---|---:|
| 512×512 | 0.00000000 |
| 512×1024 | 0.00000000 |
| 1024×512 | 0.00000000 |
| 1024×1024 | 0.00000000 |

## Qualitative findings

- Clear portraits: face, neck, shoulders and arms are continuous; dark clothing is rejected.
- Full-body scenes: small faces, hands and legs remain detectable at wide framing.
- Multi-person scenes: exposed regions across several people are recovered without requiring a single dominant face.
- Dark-skin scenes: exposed skin remains separable under monochrome conversion and outdoor contrast.
- Complex character clothing: gloves, opaque clothing and props are generally excluded.

## Known limitations

- Facial features are contained within the face-skin region and require additional facial-feature protection masks.
- Historical photos, low-contrast images and extremely distant people may lose small hand regions.

## Interpretation

V1 Pro is suitable as the skin-semantic stage of a larger portrait pipeline. Production quality is highest when inference runs per person ROI and the result is constrained by subject alpha, then subtracts dedicated hair, clothing, glove and face-detail protection masks.
