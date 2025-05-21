from selenium import webdriver
from selenium.webdriver.common.by import By
#login
USERNAME_INPUT = (By.ID, "userName")  # 替换为实际的定位器和值
PASSWORD_INPUT = (By.ID, "userPwd")
LOGIN_BUTTON = (By.ID, "btn_login")
ERROR_MESSAGE = (By.ID, "errorMessage")
#publish
ARTICLE_CLICK = (By.XPATH,"//span[text()='文章']")
ARTICLE_CLICK_WRITE = (By.XPATH,"//a[text()='写文章']")
ARTICLE_CLICK_WRITE_TITLE = (By.ID,"articleTitle")
# ARTICLE_CLICK_WRITE_CONTENT = (By.CSS_SELECTOR,"div.CodeMirror textarea")
ARTICLE_CLICK_WRITE_CONTENT = (By.XPATH,"//div[contains(@class, 'CodeMirror') and contains(@class, 'cm-s-paper')]")
ARTICLE_PUBLISH = (By.XPATH,"//button[contains(text(),'发布文章')]")
# ARTICLE_BACK = (By.CLASS_NAME,"fa fa-paper-plane fa-lg")
ARTICLE_BACK = (By.XPATH,"//a[@aria-label='Hide Sidebar']")

# menu
MENU_MANAGE=(By.XPATH,"//a[text()='管理']")
