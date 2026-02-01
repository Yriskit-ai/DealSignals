from pathlib import Path


def test_layer_03_readme_mentions_ocr_service():
    repo_root = Path(__file__).resolve().parents[1]
    readme_path = repo_root / "experiments/wework-bowx/layers/03-parsing/README.md"
    content = readme_path.read_text(encoding="utf-8")
    lowered = content.lower()

    assert "ocr" in lowered
    assert "prep_layer_03.py" in content


def test_layer_03_readme_includes_run_commands():
    repo_root = Path(__file__).resolve().parents[1]
    readme_path = repo_root / "experiments/wework-bowx/layers/03-parsing/README.md"
    content = readme_path.read_text(encoding="utf-8")

    required_snippets = [
        "scripts/prep_layer_03.py",
        "scripts/run.py",
        "--config experiments/wework-bowx/layers/03-parsing/config_ocr.yaml",
        "LAYER_03_BASE_URL=",
        "LAYER_03_S4_PDF_PATH=",
        "LAYER_03_INVESTOR_PDF_PATH=",
        "LAYER_03_SKIP_TEXT",
        "LAYER_03_FORCE_OCR",
    ]

    for snippet in required_snippets:
        assert snippet in content
