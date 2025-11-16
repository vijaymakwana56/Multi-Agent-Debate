import logging, os
from datetime import datetime

LOG_DIR = 'logs'
os.makedirs(LOG_DIR,exist_ok=True)
TS = datetime.now().strftime("%Y%m%d_%H%M%S")
LOGFILE = os.path.join(LOG_DIR,f'debate_log_{TS}.txt')

def setup_logger():
    logger = logging.getLogger("debate")
    logger.setLevel(logging.DEBUG)
    #filehandler
    fh = logging.FileHandler(LOGFILE, encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fmt = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
    fh.setFormatter(fmt)

    #console handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(logging.Formatter("%(message)s"))
    if not logger.handlers:
        logger.addHandler(fh)
        # logger.addHandler(ch)
    return logger