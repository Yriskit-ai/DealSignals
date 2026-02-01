# How to Run Layer 03 (OCR Parsing)

## 1. Prepare OCR Outputs

Layer 03 uses a local OCR service (OCRmyPDF/Tesseract) to parse the PDFs before
analysis. Run the prep script to submit the PDFs and materialize the page-aware
text files:

```bash
.venv/bin/python scripts/prep_layer_03.py
```

Required environment variables:
- `LAYER_03_S4_PDF_PATH`
- `LAYER_03_INVESTOR_PDF_PATH`

Example:

```bash
LAYER_03_BASE_URL=http://localhost:8000 \
LAYER_03_S4_PDF_PATH=experiments/wework-bowx/data/source/s4.pdf \
LAYER_03_INVESTOR_PDF_PATH=experiments/wework-bowx/data/source/investor.pdf \
.venv/bin/python scripts/prep_layer_03.py
```

Optional overrides:
- `LAYER_03_BASE_URL` (default: `http://localhost:8000`)
- `LAYER_03_OUTPUT_DIR`
- `LAYER_03_POLL_INTERVAL_S`
- `LAYER_03_POLL_TIMEOUT_S`
- `LAYER_03_SKIP_TEXT` (default: false)
- `LAYER_03_FORCE_OCR` (default: false)

The prep step writes outputs under
`experiments/wework-bowx/data/layer-03/ocrmypdf_tesseract_v1/`.

## 2. Run Experiment

```bash
.venv/bin/python scripts/run.py \
  --config experiments/wework-bowx/layers/03-parsing/config_ocr.yaml
```

## 3. Monitor Status

```bash
.venv/bin/python scripts/run.py \
  --config experiments/wework-bowx/layers/03-parsing/config_ocr.yaml \
  --status
```
