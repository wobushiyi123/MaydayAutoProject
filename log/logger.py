import logging
import sys
from pathlib import Path
from config.config import PROJECT_ROOT


class ProjectLogger:
    def __init__(self, name='mayday_auto'):
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
        log_dir = Path(PROJECT_ROOT) / 'logs'
        log_dir.mkdir(exist_ok=True)

        file_handler = logging.FileHandler(
            filename=log_dir / 'mayday_automation.log',
            mode='a',
            encoding='utf-8',
            delay=False  # 禁用延迟写入
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.INFO)
        self.logger.addHandler(file_handler)

    def get_logger(self):
        return self.logger


# 单例日志实例
logger = ProjectLogger().get_logger()


# 添加快捷方法
def log_test_start(test_name):
    logger.info(f"🚀 开始测试: {test_name}")
    logger.info("-" * 60)


def log_test_end(test_name, status="通过"):
    status_icon = "✅" if status == "通过" else "❌"
    logger.info(f"{status_icon} 测试结束: {test_name} - 状态: {status}")
    logger.info("=" * 60 + "\n")