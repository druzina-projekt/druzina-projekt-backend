import logging
import colorlog

log_format = (
    "%(log_color)s%(levelname)s:%(reset)s "
    "%(blue)s%(message)s"
)

colorlog.basicConfig(level=logging.INFO, format=log_format)
log = colorlog.getLogger()
