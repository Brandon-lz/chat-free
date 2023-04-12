from logging import handlers
import logging
from pathlib import Path

logger = logging.getLogger('chat_worker_log')
logger.setLevel(logging.DEBUG)



logpath = Path('.') / 'logs'
logpath.mkdir(parents = True, exist_ok = True)


# create logger

# 如果是根logger设置这个
# logger.propagate = False


ch = handlers.TimedRotatingFileHandler(
    str(logpath/'chat_worker_log.log'), when='midnight', backupCount=30, encoding='utf-8')
# ch.setLevel(logging.INFO)       # 要记录的级别
# formatter = logging.Formatter(
#     '%(asctime)s - %(name)s - process%(process)d - thread-%(threadName)s -  %(levelname)s - %(message)s')
formatter = logging.Formatter(
    # '进程ID:%(process)d - '
    # '线程ID:%(thread)d- '
    '日志时间:%(asctime)s - '
    '代码位置:%(pathname)s:%(lineno)d - '
    '日志等级:%(levelname)s - '
    '日志信息:%(message)s'
)
ch.setFormatter(formatter)
logger.addHandler(ch)

# 黑窗输出
import sys

handler = logging.StreamHandler(stream=sys.stdout)
# handler.setLevel(logging.DEBUG)
logger.addHandler(handler)

# 捕获异常
def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    logger.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))

sys.excepthook = handle_exception

# # 如果使用uvicorn请把日志传递打开，否则不记录接口访问日志
# from uvicorn.config import LOGGING_CONFIG
# LOGGING_CONFIG['loggers']['uvicorn.access']['propagate'] = True