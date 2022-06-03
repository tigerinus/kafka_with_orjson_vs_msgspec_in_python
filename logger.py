'''
logging
'''
import logging

logging.basicConfig(
    level=logging.INFO, format='%(asctime)s %(processName)s(%(process)d) %(levelname)s %(module)s::%(funcName)s - %(message)s'
)

log = logging.getLogger("ml-round-trip-price")
