import json
import pytest
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options as ChromeOptions

@pytest.fixture
def driver():
    """Create and manage WebDriver instance for tests"""
    options = ChromeOptions()
    driver = webdriver.Chrome(options=options)
    yield driver
    driver.quit()

class BasePage:
    """ Wrapper for selenium operations """

    def __init__(self, driver):
        self._driver = driver
        self._wait = WebDriverWait(self._driver, 10)

    def click(self, webelement):
        el = self._wait.until(EC.element_to_be_clickable(webelement))
        self._highlight_element(el, "green")
        el.click()

    def fill_text(self, webelement, txt):
        el = self._wait.until(EC.element_to_be_clickable(webelement))
        el.clear()
        self._highlight_element(el, "green")
        el.send_keys(txt)

    def clear_text(self, webelement):
        el = self._wait.until(EC.element_to_be_clickable(webelement))
        el.clear()

    def scroll_to_bottom(self):
        self._driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    def get_text(self, webelement):
        el = self._wait.until(EC.visibility_of_element_located(webelement))
        self._highlight_element(el, "green")
        return el.text

    def wait_until_page_loaded(self):
        old_page = self._driver.find_element(By.TAG_NAME, 'html')
        yield
        self._wait.until(EC.staleness_of(old_page))

    def _highlight_element(self, webelement, color):
        original_style = webelement.get_attribute("style")
        new_style = "background-color:yellow;border: 1px solid " + color + original_style
        self._driver.execute_script(
            "var tmpArguments = arguments;setTimeout(function () {tmpArguments[0].setAttribute('style', '"
            + new_style + "');},0);", webelement)
        self._driver.execute_script(
            "var tmpArguments = arguments;setTimeout(function () {tmpArguments[0].setAttribute('style', '"
            + original_style + "');},400);", webelement)
    
    def save_confirmation_model(self, webelement):
        self._driver.find_element(By.CSS_SELECTOR, webelement).screenshot("screen_shot.png")


class SignPage(BasePage):
    """ Scrive Sign Page """

    ARROW_LINK = (By.XPATH, "//span[text()='ARROW']")
    ARROW_ICON_IMAGE = (By.CSS_SELECTOR, "path.actioncolor")
    USERNAME_FIELD = (By.CSS_SELECTOR, "#name")
    NEXT_BUTTON = (By.XPATH, "//div/span[contains(text(), 'Next')]")
    SIGN_BUTTON = (By.XPATH, "//div/span[text()='Sign']")
    SUCCESS_MESSAGE = (By.XPATH, "//h1/span[text()='Document signed!']")
    CONFIRMATION_MODEL = "div.section.sign.above-overlay"

    def __init__(self, driver):
        super().__init__(driver)

    def enter_fullname(self, username):
        self.click(self.ARROW_LINK)
        self.fill_text(self.USERNAME_FIELD, username)

    def click_next(self):
        self.scroll_to_bottom()
        self.click(self.NEXT_BUTTON)

    def capture_confirmation_model(self):
        self.save_confirmation_model(self.CONFIRMATION_MODEL)

    def click_save(self):
        self.click(self.SIGN_BUTTON)

    def get_success_message(self):
        self.wait_until_page_loaded()
        return self.get_text(self.SUCCESS_MESSAGE)

    def get_page_title(self):
        return self.get_text(self.PAGE_TITLE)

def get_test_data():
    return {
        "base_url": "https://staging.scrive.com/t/9221714692410699950/7348c782641060a9",
        "username": "test@gmail.com",
        "success_message": "Document signed!",
    }


def test_valid_sign(driver):
    data = get_test_data()
    driver.get(data["base_url"])
    sign_page = SignPage(driver)
    sign_page.enter_fullname(data["username"])
    sign_page.click_next()
    sign_page.capture_confirmation_model()
    sign_page.click_save()
    assert data["success_message"] == sign_page.get_success_message()
