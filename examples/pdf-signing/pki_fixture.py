"""Load the PKI exercise explicitly for PDF integration tests."""

import importlib.util
from pathlib import Path

source = Path(__file__).resolve().parents[1] / "certificate-generation/generate.py"
spec = importlib.util.spec_from_file_location("dz_test_pki_generator", source)
if spec is None or spec.loader is None:
    raise ImportError(f"Cannot load PKI fixture from {source}")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
generate = module.generate
