import logging
import sys

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler("launcher.log"),  # Логирование в файл
                        logging.StreamHandler(sys.stdout)           # Логирование в консоль
                    ])

logger = logging.getLogger(__name__)
