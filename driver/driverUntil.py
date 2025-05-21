import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.edge.service import Service as EdgeService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from config.config import DRIVER_DIR, HEADLESS_MODE, BROWSER_TYPE
from log.logger import logger


class DriverUtil:
    _driver = None
    @classmethod
    def get_driver(cls, browser_type=BROWSER_TYPE):
        """获取指定浏览器的driver（支持自动下载驱动）"""
        if cls._driver is None:
            cls._create_driver(browser_type)
        return cls._driver

    @classmethod
    def _create_driver(cls, browser_type):
        browser = browser_type.lower()
        if HEADLESS_MODE == 'False':
            HEADLESS_MODE_BOOLEAN = False
        else:
            HEADLESS_MODE_BOOLEAN = True
        try:
            # 创建驱动目录（如果不存在）
            # os.makedirs(DRIVER_DIR, exist_ok=True)

            if browser == "chrome":
                options = webdriver.ChromeOptions()
                if HEADLESS_MODE_BOOLEAN:
                    options.add_argument("--headless=new")
                    options.add_argument("--start-maximized")
                    options.add_argument("--disable-infobars")
                    options.add_argument("--disable-dev-shm-usage")  # 解决Docker中的问题
                    options.add_argument("--no-sandbox")  # 解决Linux权限问题

                # driver_path = os.path.join(DRIVER_DIR, "chromedriver.exe" if os.name == 'nt' else "chromedriver")
                driver_path = DRIVER_DIR
                if os.path.exists(driver_path):
                    logger.info(f"使用本地Chrome驱动: {driver_path}")
                    cls._driver = webdriver.Chrome(
                        service=ChromeService(executable_path=driver_path),
                        options=options
                    )
                else:
                    logger.info("自动下载ChromeDriver...")
                    cls._driver = webdriver.Chrome(
                        service=ChromeService(ChromeDriverManager(path=DRIVER_DIR).install()),
                        options=options
                    )

            elif browser == "firefox":
                options = webdriver.FirefoxOptions()
                if HEADLESS_MODE:
                    options.add_argument("--headless")

                driver_path = os.path.join(DRIVER_DIR, "geckodriver.exe" if os.name == 'nt' else "geckodriver")
                if os.path.exists(driver_path):
                    logger.info(f"使用本地Firefox驱动: {driver_path}")
                    cls._driver = webdriver.Firefox(
                        service=FirefoxService(executable_path=driver_path),
                        options=options
                    )
                else:
                    logger.info("自动下载GeckoDriver...")
                    cls._driver = webdriver.Firefox(
                        service=FirefoxService(GeckoDriverManager(path=DRIVER_DIR).install()),
                        options=options
                    )

            elif browser == "edge":
                options = webdriver.EdgeOptions()
                if HEADLESS_MODE:
                    options.add_argument("--headless=new")
                options.add_argument("--start-maximized")

                driver_path = os.path.join(DRIVER_DIR, "msedgedriver.exe" if os.name == 'nt' else "msedgedriver")
                if os.path.exists(driver_path):
                    logger.info(f"使用本地Edge驱动: {driver_path}")
                    cls._driver = webdriver.Edge(
                        service=EdgeService(executable_path=driver_path),
                        options=options
                    )
                else:
                    logger.info("自动下载EdgeDriver...")
                    cls._driver = webdriver.Edge(
                        service=EdgeService(EdgeChromiumDriverManager(path=DRIVER_DIR).install()),
                        options=options
                    )

            else:
                raise ValueError(f"Unsupported browser type: {browser}")

            # 通用配置
            cls._driver.implicitly_wait(10)
            cls._driver.set_page_load_timeout(30)
            logger.info(f"成功启动 {browser} 浏览器")

        except Exception as e:
            logger.error(f"浏览器启动失败: {str(e)}")
            raise RuntimeError(f"浏览器启动失败: {str(e)}")

    @classmethod
    def quit_driver(cls):
        if cls._driver:
            try:
                cls._driver.quit()
                cls._driver = None
                logger.info("浏览器已成功关闭")
            except Exception as e:
                logger.error(f"浏览器关闭异常: {str(e)}")
                raise


if __name__ == "__main__":
    # 测试用例
    try:
        driver = DriverUtil.get_driver()
        driver.get("https://www.baidu.com")
        search_box = driver.find_element("id", "kw")
        search_box.send_keys("自动化测试")
        logger.info("测试执行成功")
    finally:
        DriverUtil.quit_driver()