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


class KakaoCrawler:
    def __init__(self):
        self.restaurant_list_kakao = []
        self.result_dict = dict()
        self.kakao = 'https://map.kakao.com/'
        self.driver = getDriver()
        self.queryInput = ''

    def test(self):
        self.queryInput = str(input().strip())
        print(check_tmp_result(self.driver, self.kakao, self.queryInput))
        restaurant_check = str(input().strip())
        self.init(restaurant_check)

    def init(self, restaurant_check):

        action = ActionChains(self.driver)

        tmp_result = check_tmp_result(self.driver, self.kakao, self.queryInput)
        my_index = tmp_result.index(restaurant_check)
        # 4번째 자리(3번째 인덱스)에 항상 광고가 들어와 있음 -> 따라서 이 때부터 index를 변경해 줘야 함
        if my_index >= 3:
            my_index += 1

        # 해당 음식점 페이지로 이동 : '리뷰' 글씨 클릭해야 함
        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(
            (By.XPATH, '//*[@id = "info.search.place.list"]/li[' + str(my_index+1) + ']/div[4]/a')))
        time.sleep(2)

        review = self.driver.find_element_by_xpath(
            '//*[@id = "info.search.place.list"]/li[' + str(my_index+1) + ']/div[4]/a')
        action.double_click(review).perform()

        self.driver.switch_to.window(
            self.driver.window_handles[-1])
        time.sleep(2)

        # 총 평균 별점
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')

        # ratings='\n3.7점\n\n'
        # TODO 데이터가 없으면 IndexError가 생긴다.
        ratings = soup.select('.grade_star em.num_rate')
        final_rating = float(ratings[1].text.split('점')[0])

        if final_rating == '':
            final_rating = 0

        # 다음 페이지 클릭
        pageNum = 1
        is_firstWindow = True
        is_twoPaged = False

        count = 0
        review_info = []
        end_point = False

        while True:
            # 별점, 리뷰, 날짜 출력
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')

            try:
                is_endPoint, count = self._init(
                    count, review_info, soup, end_point)

                # 100개까지만 크롤링(최신순)
                if is_endPoint:
                    break
                if is_twoPaged:
                    break

                # 페이지 이동
                # TODO numDiv 값만 특정지으면 반복문 돌지 않아도 됨 -> 앞쪽에서 실행하는게 좋을듯!
                # numDiv_list = [4, 5, 6]
                numDiv = 4
                for _ in range(3):
                    is_element_exist, element = self._is_element_exist(
                        numDiv, pageNum)
                    if is_element_exist:
                        pageNum, is_firstWindow = self.check_numDiv_kakao(
                            numDiv, pageNum, is_firstWindow, element)
                        break
                    else:
                        numDiv += 1

                # 페이지 두 개일때
                if not is_element_exist:
                    numDiv = 4
                    for _ in range(3):
                        is_twoPaged_element_exist, element = self._is_twoPaged_element_exist(
                            numDiv, pageNum)
                        if is_twoPaged_element_exist:
                            is_twoPaged = self.check_numDiv_for_twoPaged_kakao(
                                numDiv, is_twoPaged, element)
                            break
                        else:
                            numDiv += 1

                    if not is_twoPaged_element_exist:
                        break

            except NoSuchElementException:
                break

        self.driver.quit()

        self.result_dict["final_rating_kakao"] = final_rating  # int
        self.result_dict["reviews_kakao"] = review_info  # list

    def _init(self, count, review_info, soup, is_endPoint):
        # 별점, 리뷰, 날짜 출력
        # soup = BeautifulSoup(self.driver_kakao.page_source, 'html.parser')
        all_reviews = soup.select(
            '#mArticle > div.cont_evaluation > div.evaluation_review > ul > li')

        for review in all_reviews:
            temp = dict()
            rating = review.select_one(
                '#mArticle > div.cont_evaluation > div.evaluation_review > ul > li > div > div > em').text
            # rating 정보가 없을 경우 임의로 0점 부여
            try:
                rating = int(rating[0])
            except:
                rating = 0
            txt_comment = review.select_one(
                '#mArticle > div.cont_evaluation > div.evaluation_review > ul > li > div.comment_info > p > span').text
            date = review.select_one(
                '#mArticle > div.cont_evaluation > div.evaluation_review > ul > li > div.comment_info > div > span.time_write').text
            temp['rating'] = rating
            temp['comment'] = txt_comment
            temp['date'] = date
            review_info.append(temp)
            count += 1

        if count >= 100:
            is_endPoint = True

        return is_endPoint, count

    def _is_element_exist(self, numDiv, pageNum):
        flag = True
        try:
            element = self.driver.find_element_by_xpath(
                '//*[@id = "mArticle"]/div[' +
                str(numDiv)+']/div[4]/div/a['+str(pageNum)+']')
            return flag, element
        except:
            flag = False
            return flag, ''

    def _is_twoPaged_element_exist(self, numDiv, pageNum):
        flag = True
        try:
            element = self.driver.find_element_by_xpath(
                '//*[@id = "mArticle"]/div['+str(
                    numDiv)+']/div[4]/div/a')
            return flag, element
        except:
            flag = False
            return flag, ''

    def check_numDiv_kakao(self, numDiv, pageNum, is_firstWindow, element):
        self.driver.execute_script(
            "arguments[0].click();", element)
        pageNum += 1
        if is_firstWindow and pageNum == 6:
            is_firstWindow = False
            pageNum = 2
        elif not is_firstWindow and pageNum == 7:
            pageNum = 2
        time.sleep(1)
        return pageNum, is_firstWindow

    def check_numDiv_for_twoPaged_kakao(self, numDiv, is_twoPaged, element):
        self.driver.execute_script(
            "arguments[0].click();", element)
        is_twoPaged = True
        return is_twoPaged


c = KakaoCrawler()
c.test()
print(c.result_dict)
