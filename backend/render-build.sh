#!/usr/bin/env bash
set -euo pipefail

echo "===== python & pip versions ====="
python --version
pip --version

echo "===== upgrade pip setuptools wheel ====="
pip install -U pip setuptools wheel
pip --version

echo "===== install requirements (no cache) ====="
# Use the top-level requirements.txt (this repo previously used root requirements.txt)
pip install --no-cache-dir --upgrade -r requirements.txt

echo "===== show key package versions ====="
pip show fastapi pydantic pydantic-core || true

echo "===== verify by importing ====="
python - <<'PY'
import sys
try:
    import pydantic, fastapi
    print("python", sys.version.splitlines()[0])
    print("fastapi", getattr(fastapi, "__version__", None))
    print("pydantic", getattr(pydantic, "__version__", None))
except Exception as e:
    print("import-check-failed:", type(e).__name__, e)
    raise
PY

echo "===== build complete ====="
# (Optional) Any post-install commands you normally run can be appended here,
# e.g. alembic migrations, collecting static files, etc.
