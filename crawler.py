import time
import requests

from utils import Utils

from urllib.parse import quote_plus
from bs4 import BeautifulSoup

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException


class KakaoCrawler:
    def __init__(self):
        self.restaurant_list_kakao = []
        self.result_dict = dict()
        self.kakao = 'https://map.kakao.com/'
        self.driver = Utils().getDriver()
        self.queryInput = ''

    def get_kakao(self):
        self.queryInput = str(input().strip())
        print(Utils().check_tmp_result(self.driver, self.kakao, self.queryInput))
        restaurant_check = str(input().strip())
        self.init(restaurant_check)

    def init(self, restaurant_check):
        action = ActionChains(self.driver)

        tmp_result = Utils().check_tmp_result(
            self.driver, self.kakao, self.queryInput)
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


class NaverCrawler:
    def __init__(self):
        self.restaurant_list_naver = []
        self.result_dict = dict()
        self.naver = 'https://m.map.naver.com/search2/search.naver?query='
        self.driver = Utils().getDriver()
        self.queryInput = ''

    def get_naver(self):
        self.queryInput = str(input().strip())
        self.naver += self.queryInput
        print(Utils().check_tmp_result(self.driver, self.naver, self.queryInput))
        restaurant_check = str(input().strip())
        self.init(restaurant_check)

    def init(self, restaurant_check):
        tmp_result = Utils().check_tmp_result(self.driver, self.naver, self.queryInput)

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


class run_app:
    def __init__(self):
        self.results = dict()

    def run_kakao(self):
        k_crawler = KakaoCrawler()
        k_crawler.get_kakao()
        result = k_crawler.result_dict
        self.results['kakao'] = result

    def run_naver(self):
        n_crawler = NaverCrawler()
        n_crawler.get_naver()
        result = n_crawler.result_dict
        self.results['naver'] = result


run = run_app()

if __name__ == '__main__':
    run.run_naver()
    print(run.results)
