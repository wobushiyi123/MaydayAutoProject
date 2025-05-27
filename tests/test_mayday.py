import os
import subprocess
import time
import webbrowser

import allure
import pytest
from driver.driverUntil import DriverUtil
from page.publish import Publish
from untils.ExcileReader import ExcelReader
from page.login import LoginPage
from config.config import url
from log.logger import logger, log_test_start, log_test_end
from config.config import PROJECT_ROOT
from pathlib import Path


# 必须的 pytest 钩子
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)


@pytest.fixture
def test_data(request):
    """专门用于接收参数化数据的fixture"""
    return request.param  # 直接返回参数化数据


@pytest.fixture(scope="function")
def setup(request):
    """为每条测试数据创建独立的截图文件夹"""
    # 初始化截图目录
    test_data = getattr(request, "param", None)
    if test_data:
        # 使用数据中的唯一标识或创建哈希值
        data_id = test_data.get('id', str(abs(hash(str(test_data)))))
        screenshot_dir = Path(PROJECT_ROOT) / "screenshots" / f"data_{data_id}"
    else:
        screenshot_dir = Path(PROJECT_ROOT) / "screenshots" / "default"

    # 创建目录（如果不存在）
    screenshot_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"截图将保存到: {screenshot_dir}")

    # 存储到测试类实例
    request.cls.screenshot_dir = screenshot_dir
    request.cls.current_data = test_data  # 存储测试数据
    # 初始化浏览器
    driver = DriverUtil.get_driver("chrome")
    request.cls.driver = driver

    yield

    # 测试后清理
    driver.quit()


@pytest.mark.usefixtures("setup")
class TestMayday:
    TEST_DATA_PATH = Path(PROJECT_ROOT) / "test_data" / "test.xlsx"

    @allure.title('文章发布测试 - {data.get("topic", "默认标题")}')
    @allure.feature("内容管理")
    @pytest.mark.parametrize("setup", ExcelReader(TEST_DATA_PATH).get_data("TEST1"))
    def test_process(self, request):
        """处理单条测试数据"""
        # 从fixture获取数据
        data = request.cls.current_data
        test_name = f"文章发布测试[{data.get('topic', '未命名')}]"

        log_test_start(test_name)
        try:
            # 数据验证
            self._validate_test_data(data)
            logger.debug(f"测试数据详情: {data}")

            # 浏览器操作
            self.driver.maximize_window()
            self.driver.get(url)

            # 登录流程
            self._login()

            # 发布文章
            self._publish_article(data)

            log_test_end(test_name, "通过")

        except Exception as e:
            # 失败处理
            self._handle_test_failure(e, test_name)
            raise

    def _validate_test_data(self, data):
        """验证测试数据格式"""
        required_fields = ['topic', 'content']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            error_msg = f"测试数据缺少必要字段: {missing_fields}"
            logger.error(error_msg)
            raise ValueError(error_msg)

        for field in required_fields:
            if not str(data[field]).strip():
                error_msg = f"字段'{field}'不能为空"
                logger.error(error_msg)
                raise ValueError(error_msg)

    def _login(self):
        """登录流程"""
        with allure.step("登录系统"):
            LoginPage(self.driver).login_process()
            self._take_screenshot("登录完成")
            logger.info("登录步骤完成")

    def _publish_article(self, data):
        """发布文章流程"""
        with allure.step("发布文章"):
            Publish(self.driver).click_write_article(data)
            self._take_screenshot("发布完成")
            logger.info("文章发布步骤完成")

    def _take_screenshot(self, step_name):
        """通用截图方法"""
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        screenshot_path = self.screenshot_dir / f"{timestamp}_{step_name}.png"
        self.driver.save_screenshot(str(screenshot_path))
        allure.attach.file(
            str(screenshot_path),
            name=step_name,
            attachment_type=allure.attachment_type.PNG
        )
        return screenshot_path

    def _handle_test_failure(self, exception, test_name):
        """处理测试失败"""
        # 截图
        screenshot_path = self._take_screenshot("测试失败")

        # 保存页面源码
        source_path = self.screenshot_dir / f"{time.strftime('%Y%m%d_%H%M%S')}_page_source.html"
        with open(source_path, "w", encoding="utf-8") as f:
            f.write(self.driver.page_source)

        # 记录日志
        logger.error(f"测试失败: {str(exception)}")
        logger.error(f"截图路径: {screenshot_path}")
        logger.error(f"页面源码: {source_path}")

        # 附加到Allure
        allure.attach(
            self.driver.page_source,
            name="失败时页面源码",
            attachment_type=allure.attachment_type.HTML
        )

        log_test_end(test_name, "失败")


def run_tests():
    # 1. 清理旧的 Allure 数据
    allure_results_dir = os.path.join(PROJECT_ROOT, "allure-results")
    if os.path.exists(allure_results_dir):
        for file in os.listdir(allure_results_dir):
            os.remove(os.path.join(allure_results_dir, file))

    # 2. 执行 pytest 测试
    exit_code = subprocess.call([
        "pytest",
        os.path.join(PROJECT_ROOT, "test_script.py"),
        "--alluredir", allure_results_dir,
        "-v",
        "--clean-alluredir"
    ])

    # 3. 生成并打开 Allure 报告
    if exit_code in (0, 1):  # 0=成功, 1=部分失败
        # 生成报告
        subprocess.call(["allure", "generate", allure_results_dir, "--output", "./allure-report", "--clean"])

        # 自动打开浏览器
        report_path = os.path.join(PROJECT_ROOT, "allure-report", "index.html")
        webbrowser.open(f"file://{report_path}")
    else:
        print("❌ 测试执行异常！")


if __name__ == "__main__":
    run_tests()
