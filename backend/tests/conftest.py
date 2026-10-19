import os
from pathlib import Path

from dotenv import load_dotenv

# Charge la configuration dédiée aux tests avant les modules de test.
BACKEND_DIR = Path(__file__).resolve().parents[1]
TEST_ENV_FILE = BACKEND_DIR / ".env.test"

load_dotenv(TEST_ENV_FILE, override=True)

if not os.environ.get("DATABASE_URL"):
    raise RuntimeError(
        "DATABASE_URL est absente. Vérifiez le fichier backend/.env.test."
    )
