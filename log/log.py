import logging
import time,sys
from logging.handlers import TimedRotatingFileHandler


log = logging.getLogger('recommend_api')
log.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
log_file_handler = TimedRotatingFileHandler(filename="../log/app.log", when="D", interval=1, backupCount=30)
log_file_handler.setFormatter(formatter)
log_file_handler.setLevel(logging.DEBUG)
log.addHandler(log_file_handler)
