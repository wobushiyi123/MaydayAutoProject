import time
from telnetlib import EC

import allure
import pytest
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from driver.driverUntil import DriverUtil
from page.publish import Publish
from untils.ExcileReader import ExcelReader
from page.login import LoginPage
from config.config import url
from log.logger import logger


@pytest.fixture(scope="class")
def setup(request):
    driver = DriverUtil.get_driver("chrome")
    request.cls.driver = driver
    yield
    # driver.quit()
    DriverUtil.quit_driver()


@pytest.mark.usefixtures("setup")
class TestMayday:
    @allure.title("文章发布流程测试 - {data['title']}")
    @allure.feature("内容管理")
    @pytest.mark.parametrize("data", ExcelReader("D:\\MaydayAutoProject\\test_data\\test.xlsx").get_data("TEST1"))
    def test_process(self, data):
        try:
            # 方法1：直接最大化窗口
            logger.info("打开url")
            logger.info(f"开始测试用例，数据: {data}")
            self.driver.maximize_window()
            self.driver.get(url)
            # # 使用显式等待代替time.sleep
            # current_url = url.decode('utf-8') if isinstance(url, bytes) else str(url)
            # WebDriverWait(self.driver, 10).until(
            #     EC.url_contains(current_url)
            # )
            logger.info("login")
            with allure.step("登录系统"):
                login_page = LoginPage(self.driver)
                login_page.login_process()
                logger.info("登录完成")
            with allure.step("发布文章"):
                publish_page = Publish(self.driver)
                publish_page.click_write_article(data)
                logger.info("文章发布完成")
                allure.attach(
                    self.driver.get_screenshot_as_png(),
                    name="发布结果截图",
                    attachment_type=allure.attachment_type.PNG
                )
            self.driver.quit()
        except Exception as e:
            logger.error(f"测试失败: {str(e)}")
            allure.attach(
                self.driver.get_screenshot_as_png(),
                name="失败截图",
                attachment_type=allure.attachment_type.PNG
            )
            raise
