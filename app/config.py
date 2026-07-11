import os
import pathlib

from dotenv import load_dotenv

load_dotenv()

GRADIENT_API_KEY = os.environ.get("GRADIENT_API_KEY", "")
GRADIENT_MODEL = os.environ.get("GRADIENT_MODEL", "llama-4-maverick")
GRADIENT_BASE_URL = os.environ.get("GRADIENT_BASE_URL", "https://inference.do-ai.run/v1")

SOCRATA_BASE_URL = os.environ.get(
    "SOCRATA_BASE_URL", "https://data.sfgov.org/resource/vw6y-z8j6.json"
)
NEEDS_CACHE_TTL_SECONDS = int(os.environ.get("NEEDS_CACHE_TTL_SECONDS", "600"))

BASE_DIR = pathlib.Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
OPPORTUNITIES_PATH = DATA_DIR / "opportunities.json"
NEEDS_SNAPSHOT_PATH = DATA_DIR / "needs_snapshot.json"

PORT = int(os.environ.get("PORT", "8080"))
