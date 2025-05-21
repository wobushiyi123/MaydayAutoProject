from page import basePage
from location import page_location
from config.config import username, password
from page.basePage import BasePage
from log.logger import logger

class LoginPage(BasePage):
    def login_process(self):
        if self.is_element_visible(page_location.LOGIN_BUTTON,5):
            logger.info("login account and passwd")
            self.login(username, password)
        else:
            logger.info("点击管理")
            self.click(*page_location.MENU_MANAGE)
            if self.is_element_visible(page_location.LOGIN_BUTTON,8):
                logger.info("login account and passwd")
                self.login(username, password)
            else:
                logger.info("点击管理")
                self.click(*page_location.MENU_MANAGE)

    def enter_username(self, username):
        self.send_keys(*page_location.USERNAME_INPUT, text=username)

    def enter_password(self, password):
        self.send_keys(*page_location.PASSWORD_INPUT, text=password)

    def click_login_button(self):
        self.click(*page_location.LOGIN_BUTTON)

    def get_error_message(self):
        return self.get_text(*page_location.ERROR_MESSAGE)

    def login(self, username, password):
        self.enter_username(username)
        self.enter_password(password)
        self.click_login_button()
