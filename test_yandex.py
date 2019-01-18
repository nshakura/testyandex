import re
import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
import selenium.webdriver.support.ui as ui
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


class YandexClient:
    def __init__(self, url):
        self.driver = webdriver.Chrome()
        self.page = self.driver.get(url)

    def quit(self):
        self.driver.quit()

    def is_visible(self, locator, by=By.XPATH, timeout=10):
        try:
            ui.WebDriverWait(self.driver, timeout).until(EC.visibility_of_element_located((by, locator)))
            return True
        except TimeoutException:
            return False

    def handle_error(self, err):
        raise Exception(err)

    def wait_for_element(self, locator, by, timeout=60):
        if self.is_visible(locator, by=by, timeout=timeout):
            return self.driver.find_element(by=by, value=locator)
        else:
            self.handle_error(f'Element {by} {locator} not found in {timeout}')

    def wait_for_elements(self, locator, by, timeout=60):
        if self.is_visible(locator, by=by, timeout=timeout):
            return self.driver.find_elements(by=by, value=locator)
        else:
            self.handle_error(f'Element {by} {locator} not found in {timeout}')

    def wait_for_element_by_xpath(self, locator, timeout=60):
        return self.wait_for_element(locator, By.XPATH, timeout=timeout)

    def wait_for_elements_by_xpath(self, locator, timeout=60):
        return self.wait_for_elements(locator, By.XPATH, timeout=timeout)

    def find_element(self):
        self.wait_for_element_by_xpath("//a[contains(text(),'Маркет')]").click()
        self.wait_for_element_by_xpath("//span[contains(text(),'Электроника')]").click()
        self.wait_for_element_by_xpath("//a[contains(text(),'Мобильные телефоны')]").click()
        self.wait_for_element_by_xpath("//input[@id='glpricefrom']").send_keys("100")
        self.driver.execute_script("window.scrollTo(0, 1000);")
        elements = self.driver.find_elements_by_xpath("//input[contains(@name, 'Диагональ экрана')]")
        self.driver.execute_script("arguments[0].click();", elements[1])
        items = WebDriverWait(self.driver, 10).until(lambda x: x.find_elements_by_xpath("//input[contains(@name, 'Производитель')]"))
        for el in items:
            if el.is_enabled():
                self.driver.execute_script("arguments[0].click();", el)
        imgs = self.wait_for_elements_by_xpath("//div[contains(@data-id,'model')]/a")
        return imgs

    def check_elements(self, list_imgs):
        if len(list_imgs) > 10:
            return True
        else:
            print('Количество отфильтрованных элементов меньше 10')

    def open_needed_el(self, list_imgs):
        needed_el = list_imgs[1].get_attribute('title')
        self.wait_for_element_by_xpath("//a[contains(text(),'по отзывам')]").click()
        new_list = WebDriverWait(self.driver, 10).until(lambda x: x.find_elements_by_xpath("//div[contains(@data-id,'model')]/a"))
        for i in new_list:
            if i.get_attribute('title') == needed_el:
                self.driver.execute_script("arguments[0].click();", i)
                break
        element = WebDriverWait(self.driver, 10).until(lambda x: x.find_element_by_xpath("//div[@class='n-product-price-cpa2']//span[@class='price']"))
        result = re.findall(r'\d+', element.text)
        if len(result) > 1:
            print('Цена телефона {} рублей {} копеек'.format(result[0], result[1]))
        else:
            print('Цена телефона {} рублей'.format(result[0]))


class TestYandex(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.client = YandexClient('https://yandex.by/')
        # cls.client.find_element()

    @classmethod
    def tearDownClass(cls):
        cls.client.quit()

    def test_find_element(self):
        ls = self.client.find_element()
        rez = self.client.check_elements(ls)
        self.assertTrue(rez)
        self.client.open_needed_el(ls)
