import logging
import sys
from pathlib import Path


class ProjectLogger:
    def __init__(self, name='mayday'):
        self.logger = logging.getLogger(name)
        self._setup_logger()

    def _setup_logger(self):
        # 清除现有处理器（避免重复添加）
        self.logger.handlers.clear()

        # 设置日志级别
        self.logger.setLevel(logging.DEBUG)

        # 创建格式化器
        formatter = logging.Formatter(
            '[%(asctime)s] %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # 控制台处理器（立即输出）
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        console_handler.setLevel(logging.DEBUG)
        self.logger.addHandler(console_handler)

        # 文件处理器（带自动刷新）
        log_dir = Path(__file__).parent.parent / 'log'
        log_dir.mkdir(exist_ok=True)

        file_handler = logging.FileHandler(
            filename=log_dir / 'mayday.log',
            mode='a',
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.INFO)
        self.logger.addHandler(file_handler)

        # 启用实时刷新
        logging.root.handlers[0].flush()  # 强制刷新根日志

    def get_logger(self):
        return self.logger


# 单例日志实例
logger = ProjectLogger().get_logger()