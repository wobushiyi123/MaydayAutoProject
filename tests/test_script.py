import os
import time
import allure
import pytest
from driver.driverUntil import DriverUtil
from page.publish import Publish
from untils.ExcileReader import ExcelReader
from page.login import LoginPage
from config.config import url
from log.logger import logger
from config.config import PROJECT_ROOT
from log.logger import logger, log_test_start, log_test_end


# 必须的 pytest 钩子（建议放在 conftest.py）
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)


def kill_windows_browsers():
    """关闭浏览器进程"""
    browsers = ["chrome.exe", "msedge.exe", "firefox.exe", "iexplore.exe"]
    for browser in browsers:
        os.system(f"taskkill /f /im {browser} 2>nul")


def clear_directory(dir_path):
    """安全清空目录"""
    if os.path.exists(dir_path):
        for file in os.listdir(dir_path):
            file_path = os.path.join(dir_path, file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                logger.warning(f"删除文件失败 {file_path}: {e}")


@pytest.fixture(scope="function")
def setup(request):
    # 初始化路径
    # 获取测试数据（从参数化数据）
    if hasattr(request, 'param'):
        data = request.param
        # 创建基于数据ID的文件夹
        data_id = data.get('id', str(hash(str(data))))[:8]  # 使用数据ID或哈希前8位
        screenshot_dir = os.path.join(
            PROJECT_ROOT,
            "screenshots",
            f"data_{data_id}"
        )
    else:
        # 默认文件夹（非参数化测试）
        screenshot_dir = os.path.join(PROJECT_ROOT, "screenshots", "default")

    # 创建文件夹（含存在检查）
    os.makedirs(screenshot_dir, exist_ok=True)
    logger.info(f"截图将保存到: {screenshot_dir}")

    # 存储到测试实例
    request.cls.screenshot_dir = screenshot_dir

    # kill_windows_browsers()  # 根据需要取消注释
    driver = DriverUtil.get_driver("chrome")
    request.cls.driver = driver

    yield

    # 截图处理
    if hasattr(request.node, "rep_call") and request.node.rep_call.failed:
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        screenshot_path = os.path.join(screenshot_dir, f"failure_{timestamp}.png")
        driver.save_screenshot(screenshot_path)
        logger.info(f"失败截图已保存到: {screenshot_path}")

        allure.attach(
            driver.get_screenshot_as_png(),
            name=f"failure_{timestamp}",
            attachment_type=allure.attachment_type.PNG
        )

    DriverUtil.quit_driver()


@pytest.mark.usefixtures("setup")
class TestMayday:
    TEST_DATA_PATH = os.path.join(PROJECT_ROOT, "test_data", "test.xlsx")

    @allure.title('数据处理测试')  # 使用固定标题
    @allure.feature("内容管理")
    @pytest.mark.parametrize("data", ExcelReader(TEST_DATA_PATH).get_data("TEST1"))
    def test_process(self, data):
        test_name = "文章发布测试"
        log_test_start(test_name)
        try:
            # 数据验证
            self._validate_test_data(data)

            logger.debug(f"测试数据详情: {data}")
            self.driver.maximize_window()
            self.driver.get(url)

            # 登录
            self._login()
            # 测试截图
            self.driver.save_screenshot("test.png")
            # 发布文章
            self._publish_article(data)
            log_test_end(test_name, "通过")
        except Exception as e:
            # self._handle_test_failure(e)
            logger.warning("SSL错误发生，尝试忽略证书继续...")
            self.driver.execute_script("window.open('about:blank')")
            self.driver.switch_to.window(self.driver.window_handles[-1])
            self.driver.get(url)
            raise

    def _validate_test_data(self, data):
        """验证测试数据格式"""
        required_fields = ['topic', 'content']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            error_msg = f"测试数据缺少必要字段: {missing_fields}"
            logger.error(error_msg)
            raise ValueError(error_msg)

        # 确保字段不为空
        for field in required_fields:
            if not data[field].strip():
                error_msg = f"字段'{field}'不能为空"
                logger.error(error_msg)
                raise ValueError(error_msg)

    def _login(self):
        """登录流程"""
        with allure.step("登录系统"):
            LoginPage(self.driver).login_process()
            logger.info("登录步骤完成")
            allure.attach(
                self.driver.get_screenshot_as_png(),
                name="登录完成截图",
                attachment_type=allure.attachment_type.PNG
            )

    def _publish_article(self, data):
        """发布文章流程"""
        with allure.step("发布文章"):
            Publish(self.driver).click_write_article(data)
            logger.info("文章发布步骤完成")
            allure.attach(
                self.driver.get_screenshot_as_png(),
                name="发布结果截图",
                attachment_type=allure.attachment_type.PNG
            )

    def _handle_test_failure(self, exception):
        """增强的错误处理方法"""
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        try:
            # 确保截图目录存在
            screenshots_dir = os.path.join(PROJECT_ROOT, "screenshots")
            os.makedirs(screenshots_dir, exist_ok=True)

            # 保存截图
            screenshot_path = os.path.join(screenshots_dir, f"error_{timestamp}.png")
            self.driver.save_screenshot(screenshot_path)
            logger.info(f"错误截图已保存: {screenshot_path}")

            # 获取页面源代码
            page_source = self.driver.page_source
            source_path = os.path.join(screenshots_dir, f"source_{timestamp}.html")
            with open(source_path, "w", encoding="utf-8") as f:
                f.write(page_source)

            # 添加到Allure
            allure.attach(
                self.driver.get_screenshot_as_png(),
                name=f"error_{timestamp}",
                attachment_type=allure.attachment_type.PNG
            )
            allure.attach(
                page_source,
                name=f"page_source_{timestamp}",
                attachment_type=allure.attachment_type.HTML
            )

        except Exception as e:
            logger.error(f"保存错误信息失败: {str(e)}")
        finally:
            raise exception  # 重新抛出原始异常


def _verify_directory_permissions():
    test_dirs = ["screenshots", "allure-results", "logs"]
    for dir_name in test_dirs:
        dir_path = os.path.join(PROJECT_ROOT, dir_name)
        try:
            os.makedirs(dir_path, exist_ok=True)
            test_file = os.path.join(dir_path, "test.txt")
            with open(test_file, "w") as f:
                f.write("test")
            os.remove(test_file)
            logger.info(f"目录验证通过: {dir_path}")
        except Exception as e:
            logger.error(f"目录验证失败 {dir_path}: {str(e)}")
            raise


if __name__ == "__main__":
    _verify_directory_permissions()
    # 初始化环境
    for folder in ["allure-results", "screenshots", "logs"]:
        dir_path = os.path.join(PROJECT_ROOT, folder)
        os.makedirs(dir_path, exist_ok=True)
        if folder != "logs":  # 不清空日志目录
            clear_directory(dir_path)
        logger.info(f"初始化目录: {dir_path}")

    # 执行测试
    exit_code = pytest.main([
        os.path.join(os.path.dirname(__file__), "test_script.py"),
        "--alluredir", os.path.join(PROJECT_ROOT, "allure-results"),
        "-v",
        "--clean-alluredir",
        "--log-level=INFO"
    ])

    # 生成报告
    if exit_code in (0, 1):  # 0=成功, 1=测试失败但执行完成
        report_cmd = f"allure serve {os.path.join(PROJECT_ROOT, 'allure-results')}"
        logger.info(f"生成报告: {report_cmd}")
        os.system(report_cmd)
    else:
        logger.error(f"测试执行异常，退出码: {exit_code}")
