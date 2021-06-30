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
        self.q = multiprocessing.Queue()
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
        # self.driver_kakao.quit()

    def kakao_crawler(self, restaurant_check):

        action = ActionChains(self.driver_kakao)
        my_xpath = restaurant_check

        if self.restaurant_list_kakao.count(restaurant_check) >= 2:
            for i in range(len(self.restaurant_list_kakao)):
                if self.restaurant_list_kakao[i] == restaurant_check:
                    my_index = i
                    break
        else:
            my_index = self.restaurant_list_kakao.index(my_xpath)
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
        # 총 평점 출력
        try:
            ratings = soup.select('.grade_star')
            final_rating = int(ratings[1].text.strip())
        except:
            return None

        count = 0

        # 다음 페이지 클릭
        # i는 1~ , j는 1~5 단위의 페이지
        i = j = 1
        pageNum = 1
        count = 0
        review_info = []

        while True:
            try:
                self.reviewCrawler_kakao(count, review_info)
                # review_by_page.append(review_info)

                if count >= 100:
                    break
                try:
                    element = self.driver_kakao.find_element_by_xpath(
                        '//*[@id = "mArticle"]/div[5]/div[4]/div/a['+str(i)+']')
                    self.driver_kakao.execute_script(
                        "arguments[0].click();", element)
                # 2페이지까지 밖에 없을 경우 예외처리 후 크롤링
                except:
                    element = self.driver_kakao.find_element_by_xpath(
                        '//*[@id = "mArticle"]/div[4]/div[4]/div/a')
                    self.driver_kakao.execute_script(
                        "arguments[0].click();", element)
                    time.sleep(2)
                    self.reviewCrawler_kakao(
                        count, review_info)
                    break
                # break
                # 페이지 이동
                if i == 5 and j == 1:
                    i = 2
                    j += 1
                elif i == 6 and j >= 2:
                    i = 2
                    j += 1
                else:
                    i += 1
                pageNum += 1
                time.sleep(1)
            except NoSuchElementException:
                break

        review_info.sort()

        # low
        if len(review_info) > 10:
            low_review_info = review_info[:6]
        elif 0 < len(review_info) <= 10:
            low_review_info = review_info[0]
        elif len(review_info) == 0:
            low_review_info = ''

        # high
        if len(review_info) > 10:
            high_review_info = review_info[-6:]
        elif 0 < len(review_info) <= 10:
            high_review_info = review_info[-1]
        elif len(review_info) == 0:
            high_review_info = ''

        self.driver_kakao.quit()

        self.result_dict["final_rating_kakao"] = final_rating
        self.result_dict["low_review_info_kakao"] = low_review_info
        self.result_dict["high_review_info_kakao"] = high_review_info

        '''테스트용'''
        # self.result_dict["review_info_kakao"] = review_info
        # self.test.append(self.result_dict)

        '''배포용'''
        self.q.put(self.result_dict)

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
            final_rating = int(ratings[0].text[2:6])
        except:
            return None

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

            review_info.append((rating, txt_comment, date))
            count += 1
            if count >= 100:
                break

        review_info.sort()

        # low
        if len(review_info) > 10:
            low_review_info = review_info[-6:]
        elif 0 < len(review_info) <= 10:
            low_review_info = review_info[-1]
        elif len(review_info) == 0:
            low_review_info = ''

        # high
        if len(review_info) > 10:
            high_review_info = review_info[-6:]
        elif 0 < len(review_info) <= 10:
            high_review_info = review_info[-1]
        elif len(review_info) == 0:
            high_review_info = ''

        self.driver_naver.quit()

        result_dict = dict()
        result_dict["final_rating_naver"] = final_rating
        result_dict["low_review_info_naver"] = low_review_info
        result_dict["high_review_info_naver"] = high_review_info

        self.q.put(result_dict)

    def reviewCrawler_kakao(self, count, review_info):
        # 별점, 리뷰, 날짜 출력
        soup = BeautifulSoup(self.driver_kakao.page_source, 'html.parser')
        all_reviews = soup.select(
            '#mArticle > div.cont_evaluation > div.evaluation_review > ul > li')
        # print(all_reviews)
        for review in all_reviews:
            temp = []
            rating = review.select_one(
                '#mArticle > div.cont_evaluation > div.evaluation_review > ul > li > div > div > em').text
            # rating 정보가 없을 경우 임의로 3점 부여
            if rating == '작성일 : ':
                rating = '3점'
            rating = int(rating[0])
            txt_comment = review.select_one(
                '#mArticle > div.cont_evaluation > div.evaluation_review > ul > li > div.comment_info > p > span').text
            date = review.select_one(
                '#mArticle > div.cont_evaluation > div.evaluation_review > ul > li > div.comment_info > div > span.time_write').text
            temp.append(rating)
            temp.append(txt_comment)
            temp.append(date)
            review_info.append(temp)
            count += 1


'''
크롤러 클래스 작동 확인
음식점 확인 리스트 생성
'''
# crawler = Crawler()
# crawler.kakao_checker('마포 진미식당')
# restaurant_list_kakao = crawler.restaurant_list_kakao
# print(restaurant_list_kakao)

# restaurant_check = input('골라라 : ')
# crawler.kakao_crawler(restaurant_check)
# test = crawler.test
# print(test)

'''
[실패 로그]
1. 마포 진미식당
- 일반 크롤러만 사용시 크롤링을 하다 맘
- multiprocessing을 하면 아예 결과가 나오지 않음
'''
jobs = []


def main():
    crawler = Crawler()
    # restaurant_check 구하기 위한 과정
    crawler.kakao_checker('마포 진미식당')
    restaurant_list_kakao = crawler.restaurant_list_kakao
    print(restaurant_list_kakao)
    restaurant_check = input('골라라 : ')
    # 네이버 맛집 리스트 구하기
    crawler.naver_checker('마포 진미식당')
    # print(crawler.restaurant_list_naver)

    kakao_crawler = crawler.kakao_crawler(restaurant_check)
    naver_crawler = crawler.naver_crawler(restaurant_check)

    q = crawler.q

    crawlers = [kakao_crawler, naver_crawler]

    for crawler in crawlers:
        p = Process(target=crawler)
        jobs.append(p)
        p.start()

    for p in jobs:
        p.join()
        p.close()

    result = [q.get() for j in jobs]
    print(result)


if __name__ == '__main__':
    main()
