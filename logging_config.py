import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

logger = logging.getLogger("erpconnect")
logger.setLevel(logging.INFO)

handler = RotatingFileHandler(LOG_DIR / "erp_ai.log", maxBytes=5_000_000, backupCount=3, encoding="utf-8")
formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s")
handler.setFormatter(formatter)

if not logger.hasHandlers():
    logger.addHandler(handler)
    # also print to console for dev
    console = logging.StreamHandler()
    console.setFormatter(formatter)
    logger.addHandler(console)
