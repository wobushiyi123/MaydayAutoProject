# config/logging_config.py
import logging
import logging.config
from pathlib import Path
from config.config import PROJECT_ROOT

def configure_logging():
    """配置日志系统"""
    # 创建日志目录
    log_dir = Path(PROJECT_ROOT) / "logs"
    log_dir.mkdir(exist_ok=True)

    logging.config.dictConfig({
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                'format': '[%(asctime)s] %(levelname)-8s [%(name)s:%(lineno)d] %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            },
        },
        'handlers': {
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
                'formatter': 'standard',
                'stream': 'ext://sys.stdout'
            },
            'file': {
                'level': 'INFO',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': str(log_dir / 'automation.log'),
                'maxBytes': 10*1024*1024,  # 10MB
                'backupCount': 5,
                'formatter': 'standard',
                'encoding': 'utf-8'
            }
        },
        'loggers': {
            '': {  # root logger
                'handlers': ['console', 'file'],
                'level': 'DEBUG'
            },
            'selenium': {
                'level': 'WARNING',
                'propagate': False
            },
            'urllib3': {
                'level': 'WARNING',
                'propagate': False
            }
        }
    })