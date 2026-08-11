V3 GENERATED ATTACK IMAGES

These files are reproducible outputs and are not tracked by Git.
Generate them with:
  python -m src.v3_pipeline generate --split <split>

V3 corrects the V2 experimental confounds:
- image and joint conditions reuse the exact same attacked image;
- payload families are length/area matched;
- size ablation keeps placement and all non-size parameters fixed;
- camouflage metadata records contrast after alpha compositing;
- lossless WebP reduces storage without adding JPEG artifacts.
