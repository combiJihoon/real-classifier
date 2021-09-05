import time

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver import ChromeOptions


class Utils:
    def __init__(self):
        self.result_kakao_naver = dict()

    def getDriver(self):
        options = ChromeOptions()
        options.add_argument('headless')
        options.add_argument("disable-gpu")

        driver = webdriver.Chrome(
            r"/Users/jihun/Mywork/django-project/revclassifier/chromedriver")

        return driver

    def check_tmp_result(self, driver, url, queryInput):
        driver.get(url)

        if 'kakao' in url:
            # kakaomap review 찾기
            driver.find_element_by_css_selector(
                '.query.tf_keyword').send_keys(queryInput)
            time.sleep(2)
            driver.find_element_by_css_selector(
                '.query.tf_keyword').send_keys(Keys.ENTER)
            time.sleep(2)

            # 원하는 음식점이 맞는지 확인 : 음식점 리스트 출력 및 선택
            WebDriverWait(driver, 3).until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, 'strong.tit_name > a')))
            res_to_be_list = driver.find_elements_by_css_selector(
                'strong.tit_name > a.link_name')
        else:
            # 원하는 음식점이 맞는지 확인 : 음식점 리스트 출력 및 선택
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, 'a.a_item.a_item_distance._linkSiteview > div._title > strong')))
            res_to_be_list = driver.find_elements_by_css_selector(
                'a.a_item.a_item_distance._linkSiteview > div._title > strong')

        tmp_result = [res.text for res in res_to_be_list]

        return tmp_result
