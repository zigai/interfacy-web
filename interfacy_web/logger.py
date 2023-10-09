from loguru import logger
import sys
from stdl.log import loguru_formater

logger.remove()
LOGGER_ID = logger.add(sys.stdout, level="DEBUG", format=loguru_formater)  # type:ignore
