import logging

logger = logging.getLogger("flow")
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.WARNING)
ch.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(filename)s:%(lineno)d -- FLOW: %(message)s"))
logger.addHandler(ch)

