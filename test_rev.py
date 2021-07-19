# TODO 크롤링 속도 높이기 : 리뷰 수가 100개 이상이면 100개까지면 살피기
# TODO 병렬적으로 이루어지는 것이라면 큐를 써보는 것은 어떨런지?
import os
import time
import requests

from urllib.parse import quote_plus
from bs4 import BeautifulSoup

# from pyvirtualdisplay import Display

from selenium import webdriver
from selenium.webdriver import ChromeOptions
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

import multiprocessing
from multiprocessing import freeze_support, Process


# 해야하는 것
# 가게가 없을 경우, 리뷰가 없을 경우 예외처리
# 사용자 input 받고 checker 실행한 뒤 'driver'도 리턴해 줘야 함


class Crawler:
    def __init__(self, queryInput=None, restaruant_check=None):
        # 받은 리스트의 순서가 다르기 때문에 'kakao'에서 'restaurant_check' 얻은 것만 동일하게 사용할
        self.restaurant_list_kakao = []
        self.restaurant_list_naver = []
        # self.restaurant_check = ''
        self.driver_kakao = webdriver.Chrome(
            r"/Users/jihun/Mywork/django-project/revclassifier/chromedriver")
        self.driver_naver = webdriver.Chrome(
            r"/Users/jihun/Mywork/django-project/revclassifier/chromedriver")

        self.test = []
        # self.q = multiprocessing.Queue()
        self.result_dict = dict()

        self.kakao = 'https://map.kakao.com/'
        # naver url은 query 부분까지 나옴
        self.naver = 'https://m.map.naver.com/search2/search.naver?query='

        options = ChromeOptions()
        options.add_argument('headless')
        options.add_argument("disable-gpu")

    # 음식점 리스트 리턴
    def kakao_checker(self, queryInput):
        driver = self.driver_kakao

        driver.get(self.kakao)
        # kakaomap review 찾기
        driver.find_element_by_css_selector(
            '.query.tf_keyword').send_keys(queryInput)
        time.sleep(2)
        driver.find_element_by_css_selector(
            '.query.tf_keyword').send_keys(Keys.ENTER)
        time.sleep(2)

        # 원하는 음식점이 맞는지 확인 : 음식점 리스트 출력 및 선택
        # html로 옮기면 사용자가 클릭하도록 바꾸어야 할 듯
        WebDriverWait(driver, 5).until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, 'strong.tit_name > a')))
        restaurants_to_be_list = driver.find_elements_by_css_selector(
            'strong.tit_name > a.link_name')
        for restaurant in restaurants_to_be_list:
            self.restaurant_list_kakao.append(restaurant.text)

    def kakao_crawler(self, restaurant_check):

        action = ActionChains(self.driver_kakao)

        my_index = self.restaurant_list_kakao.index(restaurant_check)
        # 4번째 자리(3번째 인덱스)에 항상 광고가 들어와 있음 -> 따라서 이 때부터 index를 변경해 줘야 함
        if my_index >= 3:
            my_index += 1

        # 해당 음식점 페이지로 이동 : '리뷰' 글씨 클릭해야 함
        WebDriverWait(self.driver_kakao, 10).until(EC.element_to_be_clickable(
            (By.XPATH, '//*[@id = "info.search.place.list"]/li[' + str(my_index+1) + ']/div[4]/a')))
        time.sleep(2)

        review = self.driver_kakao.find_element_by_xpath(
            '//*[@id = "info.search.place.list"]/li[' + str(my_index+1) + ']/div[4]/a')
        action.double_click(review).perform()

        self.driver_kakao.switch_to.window(
            self.driver_kakao.window_handles[-1])
        time.sleep(2)

        # 총 평균 별점
        soup = BeautifulSoup(self.driver_kakao.page_source, 'html.parser')

        # ratings='\n3.7점\n\n'
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
            soup = BeautifulSoup(self.driver_kakao.page_source, 'html.parser')

            try:
                is_endPoint, count = self._crawler_kakao(
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

        self.driver_kakao.quit()

        self.result_dict["final_rating_kakao"] = final_rating
        self.result_dict["reviews_kakao"] = review_info

    def naver_checker(self, queryInput):
        # plusUrl = '마북동 전주콩나물해장국'
        url = self.naver + queryInput
        self.driver_naver.get(url)

        # 원하는 음식점이 맞는지 확인 : 음식점 리스트 출력 및 선택
        # html로 옮기면 사용자가 클릭하도록 바꾸어야 할 듯
        WebDriverWait(self.driver_naver, 3).until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, 'div.item_tit._title > strong')))
        restaurants_to_be_list = self.driver_naver.find_elements_by_css_selector(
            'div.item_tit._title > strong')

        for restaurant in restaurants_to_be_list:
            self.restaurant_list_naver.append(restaurant.text)

    def naver_crawler(self, restaurant_check):
        my_xpath = restaurant_check

        # TODO NoSuchElementException 구체적으로 어떻게 처리할 지 생각하기
        if not self.restaurant_list_kakao:
            raise NoSuchElementException

        if self.restaurant_list_naver.count(restaurant_check) >= 2:
            for i in range(len(self.restaurant_list_naver)):
                if self.restaurant_list_naver[i] == restaurant_check:
                    my_index = i
                    break
        else:
            my_index = self.restaurant_list_naver.index(my_xpath)

        # 해당 음식점 페이지로 이동
        WebDriverWait(self.driver_naver, 10).until(EC.element_to_be_clickable(
            (By.XPATH, '//*[@id="ct"]/div[2]/ul/li[' + str(my_index+1) + ']/div[1]/a/div'))).click()
        time.sleep(2)

        soup = BeautifulSoup(self.driver_naver.page_source, 'html.parser')
        # 총 평점 구하기 : 없을 경우 리뷰도 없으므로 빈 문자열 리턴
        try:
            ratings = soup.select(
                '._1kUrA')
            final_rating = float(ratings[0].text[2:6])
        except:
            final_rating = 0

        # '스타벅스' 같은 경우 메뉴 바에 '선물하기'가 있어 '리뷰' 메뉴의 위치가 달라지게 된다.
        # 따라서, 아래와 같이 try & except로 예외처리를 한다.
        try:
            WebDriverWait(self.driver_naver, 10).until(EC.element_to_be_clickable(
                (By.XPATH, '//*[@id="app-root"]/div/div[2]/div[3]/div/div/div/div/a[7]')))

            review_page = self.driver_naver.find_element_by_xpath(
                '//*[@id="app-root"]/div/div[2]/div[3]/div/div/div/div/a[4]')
            self.driver_naver.execute_script(
                "arguments[0].click();", review_page)
            time.sleep(1)
        except:
            review_page = self.driver_naver.find_element_by_xpath(
                '//*[@id="app-root"]/div/div[2]/div[3]/div/div/div/div/a[3]')
            self.driver_naver.execute_script(
                "arguments[0].click();", review_page)
            time.sleep(1)

        # TODO 더보기 클릭 횟수 제한하기(더보기 클릭하면 10개씩 나오나...?)10회까지로 제한!
        # 더보기 계속 클릭하기
        while True:
            try:
                more_page = self.driver_naver.find_element_by_css_selector(
                    '._3iTUo')
                self.driver_naver.execute_script(
                    "arguments[0].click();", more_page)
                time.sleep(1)
            except:
                break

        # 더보기 클릭이 다 끝난 후 전체적으로 크롤링
        li_tags = self.driver_naver.find_elements_by_css_selector('._2Cv-r')
        rating_tags = self.driver_naver.find_elements_by_css_selector(
            '._2tObC')
        txt_comment_tags = self.driver_naver.find_elements_by_css_selector(
            '.WoYOw')
        date_tags = self.driver_naver.find_elements_by_css_selector(
            'div.ZvQ8X > span:nth-of-type(1)')

        count = 0
        review_info = []
        for i in range(len(li_tags)):
            rating = rating_tags[i].text
            rating = float(rating)
            txt_comment = txt_comment_tags[i].text
            date = date_tags[i].text

            review_info.append([rating, txt_comment, date])
            count += 1
            if count >= 100:
                break

        self.driver_naver.quit()

        self.result_dict["final_rating_naver"] = final_rating
        self.result_dict["reviews_naver"] = review_info

        self.driver_naver.quit()

    def _crawler_kakao(self, count, review_info, soup, is_endPoint):
        # 별점, 리뷰, 날짜 출력
        # soup = BeautifulSoup(self.driver_kakao.page_source, 'html.parser')
        all_reviews = soup.select(
            '#mArticle > div.cont_evaluation > div.evaluation_review > ul > li')

        for review in all_reviews:
            temp = []
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
            temp.append(rating)
            temp.append(txt_comment)
            temp.append(date)
            review_info.append(temp)
            count += 1

        if count >= 100:
            is_endPoint = True

        return is_endPoint, count

    def _is_element_exist(self, numDiv, pageNum):
        flag = True
        try:
            element = self.driver_kakao.find_element_by_xpath(
                '//*[@id = "mArticle"]/div[' +
                str(numDiv)+']/div[4]/div/a['+str(pageNum)+']')
            return flag, element
        except:
            flag = False
            return flag, ''

    def _is_twoPaged_element_exist(self, numDiv, pageNum):
        flag = True
        try:
            element = self.driver_kakao.find_element_by_xpath(
                '//*[@id = "mArticle"]/div['+str(
                    numDiv)+']/div[4]/div/a')
            return flag, element
        except:
            flag = False
            return flag, ''

    def check_numDiv_kakao(self, numDiv, pageNum, is_firstWindow, element):
        self.driver_kakao.execute_script(
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
        self.driver_kakao.execute_script(
            "arguments[0].click();", element)
        is_twoPaged = True
        return is_twoPaged

    def print_kakao(self):
        my_query = input('원하는 음식점(지역 + 이름) : ')
        # my_query = '여수 거북이식당'

        self.kakao_checker(my_query)
        print(self.restaurant_list_kakao)
        time.sleep(2)
        temp = input('원하는 음식점 고르시오 : ')
        # temp = '거북이식당'

        self.kakao_crawler(temp)
        return self.result_dict["final_rating_kakao"], self.result_dict["reviews_kakao"]

    def print_naver(self):
        my_query = input('원하는 음식점(지역 + 이름) : ')
        self.kakao_checker(my_query)
        self.naver_checker(my_query)
        print(self.restaurant_list_kakao)
        temp = input('원하는 음식점 고르시오 : ')
        self.naver_crawler(temp)
        return self.result_dict["final_rating_naver"], self.result_dict["reviews_naver"]


start = time.time()
cr = Crawler()
'''카카오 테스트'''
print(cr.print_kakao())

'''네이버 테스트'''
# print(cr.print_naver())
end = time.time()

print(f'총 시간 : {int(end-start)}초')
