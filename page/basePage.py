from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config.config import url, IMPLICIT_WAIT, EXPLICIT_WAIT


class BasePage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, IMPLICIT_WAIT)

    def open(self):
        self.driver.get(self.base_url)

    def find_element(self, *locator):
        return self.wait.until(EC.presence_of_element_located(locator))

    def find_elements(self, *locator):
        return self.wait.until(EC.presence_of_all_elements_located(locator))

    def click(self, *locator):
        self.find_element(*locator).click()

    def send_keys(self, *locator, text):
        self.find_element(*locator).send_keys(text)

    def get_text(self, *locator):
        return self.find_element(*locator).text

    # def is_element_exist(self, *locator):
    #     """判断元素是否存在"""
    #     try:
    #         elements = self.find_elements(*locator)
    #         return len(elements) > 0  # 返回 True/False
    #     except Exception as e:
    #         print(f"完整错误信息: {e.msg}")

    def is_element_visible(self, locator, timeout=10):
        """检查元素是否可见"""
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located(locator)
            )
            return True
        except TimeoutException:
            return False

    def is_element_clickable(self, locator, timeout=10):
        """检查元素是否可见"""
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable(locator)
            )
            return True
        except TimeoutException:
            return False

    def scroll_to_element(self, selector, timeout=10):
        try:
            # 等待元素存在于 DOM
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(selector)
            )

            # 记录初始位置（调试用）
            initial_y = self.execute_script("return window.pageYOffset;")

            # 执行滚动操作
            self.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)

            # 验证滚动效果（可选）
            final_y = self.execute_script("return window.pageYOffset;")
            print(f"滚动距离: {final_y - initial_y} 像素")

            # 二次等待确保元素可交互
            WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable(selector)
            )
            return element
        except Exception as e:
            print(f"滚动失败: {str(e)}")
            raise
