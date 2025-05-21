from selenium.webdriver import ActionChains

from page import basePage
from location import page_location
from page.basePage import BasePage
from log.logger import logger


class Publish(BasePage):

    def click_write_article(self, data):
        try:
            logger.info("点击文章")
            self.click(*page_location.ARTICLE_CLICK)
            logger.info("点击写文章")
            self.click(*page_location.ARTICLE_CLICK_WRITE)
            logger.info("写标题")
            self.click(*page_location.ARTICLE_CLICK_WRITE_TITLE)
            self.send_keys(*page_location.ARTICLE_CLICK_WRITE_TITLE, text=data['topic'])
            logger.info("写内容")
            # self.scroll_to_element(*page_location.ARTICLE_CLICK_WRITE_CONTENT)
            self.click(*page_location.ARTICLE_CLICK_WRITE_CONTENT)
            actions = ActionChains(self.driver)
            actions.send_keys(data['content']).perform()
            # self.send_keys(*page_location.ARTICLE_CLICK_WRITE_CONTENT,text="test")
            logger.info("发布")
            self.click(*page_location.ARTICLE_PUBLISH)
            logger.info("返回文章浏览列表")
            self.click(*page_location.ARTICLE_BACK)
        except Exception as e:
            print(e)
