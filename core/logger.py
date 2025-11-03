import logging
from datetime import datetime
import os

# log fayl yo‘lini yaratamiz
os.makedirs("logs", exist_ok=True)
log_file = f"logs/{datetime.now().strftime('%Y-%m-%d')}.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler()  # terminalda ham ko‘rsatadi
    ]
)

logger = logging.getLogger(__name__)
