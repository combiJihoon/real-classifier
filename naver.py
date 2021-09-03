import time
import requests

from urllib.parse import quote_plus
from bs4 import BeautifulSoup

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

from utils import getDriver, check_tmp_result


class NaverCrawler:
    def __init__(self):
        self.restaurant_list_naver = []
        self.result_dict = dict()
        self.naver = 'https://m.map.naver.com/search2/search.naver?query='
        self.driver = getDriver()
        self.queryInput = ''

    def test(self):
        self.queryInput = str(input().strip())
        self.naver += self.queryInput
        print(check_tmp_result(self.driver, self.naver, self.queryInput))
        restaurant_check = str(input().strip())
        self.init(restaurant_check)

    def init(self, restaurant_check):
        tmp_result = check_tmp_result(self.driver, self.naver, self.queryInput)

        # TODO NoSuchElementException 구체적으로 어떻게 처리할 지 생각하기
        if not tmp_result:
            raise NoSuchElementException

        else:
            my_index = tmp_result.index(restaurant_check)

        # 해당 음식점 페이지로 이동
        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, '#ct > div.search_listview._content._ctList > ul > li:nth-child(' + str(my_index+1) + ') > div.item_info > a.a_item.a_item_distance._linkSiteview > div > strong'))).click()
        time.sleep(2)

        # 알아낸 restaurant code 이용해 다른 url로 이동
        # https://m.place.naver.com/restaurant/19862126/home
        current_url = self.driver.current_url
        current_url = current_url.replace('home', 'review/visitor')
        self.driver.get(current_url)

        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        # 총 평점 구하기 : 없을 경우 리뷰도 없으므로 빈 문자열 리턴
        try:
            ratings = soup.select(
                '._1kUrA')
            final_rating = float(ratings[0].text[2:6])
        except:
            final_rating = 0

        # TODO 더보기 클릭 횟수 제한하기(더보기 클릭하면 10개씩 나오나...?)10회까지로 제한!
        # 더보기 계속 클릭하기
        while True:
            try:
                more_page = self.driver.find_element_by_css_selector(
                    '._3iTUo')
                self.driver.execute_script(
                    "arguments[0].click();", more_page)
                time.sleep(1)
            except:
                break

        # 더보기 클릭이 다 끝난 후 전체적으로 크롤링
        li_tags = self.driver.find_elements_by_css_selector('._2Cv-r')
        rating_tags = self.driver.find_elements_by_css_selector(
            '._2tObC')
        txt_comment_tags = self.driver.find_elements_by_css_selector(
            '.WoYOw')
        date_tags = self.driver.find_elements_by_css_selector(
            'div.ZvQ8X > span:nth-of-type(1)')

        count = 0
        review_info = []
        for i in range(len(li_tags)):
            temp = dict()
            temp['rating'] = float(rating_tags[i].text)
            temp['comment'] = txt_comment_tags[i].text
            temp['date'] = date_tags[i].text

            review_info.append(temp)
            count += 1
            if count >= 100:
                break

        self.driver.quit()

        self.result_dict["final_rating_naver"] = final_rating
        self.result_dict["reviews_naver"] = review_info


c = NaverCrawler()
c.test()
print(c.result_dict)
