import time
import requests
import json

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
        self.restaurant_check = ''

    def get_kakao(self, queryInput):
        self.queryInput = queryInput
        print(Utils().check_tmp_result(self.driver, self.kakao, self.queryInput))
        self.restaurant_check = str(input('원하는 음식점이 어디입니까?: ').strip())
        self.init()

    def init(self):
        action = ActionChains(self.driver)

        tmp_result = Utils().check_tmp_result(
            self.driver, self.kakao, self.queryInput)
        my_index = tmp_result.index(self.restaurant_check)
        # 4번째 자리(3번째 인덱스)에 항상 광고가 들어와 있음 -> 따라서 이 때부터 index를 변경해 줘야 함
        if my_index >= 3:
            my_index += 1

        # 해당 음식점 페이지로 이동 : '리뷰' 글씨 클릭해야 함
        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(
            (By.XPATH, '//*[@id = "info.search.place.list"]/li[' + str(my_index+1) + ']/div[4]/a')))
        time.sleep(2)

        review = self.driver.find_element_by_xpath(
            '//*[@id = "info.search.place.list"]/li[' + str(my_index+1) + ']/div[4]/a')
        action.click(review).perform()

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

        count = 0
        target_page = -1
        review_info = []
        end_point = False

        while True:
            # 별점, 리뷰, 날짜 출력
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            try:
                self._init(count, review_info, soup, end_point)

                # 페이지 이동
                target_page += 1
                pages = self.driver.find_elements_by_css_selector(
                    '.paging_mapdetail .link_page')
                if target_page != len(pages):
                    self.driver.execute_script(
                        "arguments[0].click();", pages[target_page])
                else:
                    btn_next = self.driver.find_elements_by_css_selector(
                        '.paging_mapdetail .btn_next')
                    if btn_next:
                        self.driver.execute_script(
                            "arguments[0].click();", btn_next[0])
                        target_page = -1
                    else:
                        # 마지막 페이지 한 번 더 크롤링 후 끝내기
                        break

            except NoSuchElementException:
                break

        self.driver.quit()

        self.result_dict["final_rating_kakao"] = final_rating  # int
        self.result_dict["reviews_kakao"] = review_info  # list

    def _init(self, count, review_info, soup, is_endPoint):
        # 별점, 리뷰, 날짜 출력
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
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

        # if count >= 100:
        #     is_endPoint = True

        # return is_endPoint, count


class NaverCrawler:
    def __init__(self):
        self.restaurant_list_naver = []
        self.result_dict = dict()
        self.naver = 'https://m.map.naver.com/search2/search.naver?query='
        self.driver = Utils().getDriver()
        self.queryInput = ''

    def get_naver(self, queryInput, restaurant_check):
        self.queryInput = queryInput
        self.naver += self.queryInput
        print(Utils().check_tmp_result(self.driver, self.naver, self.queryInput))
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
        click_more = 0
        while click_more < 11:
            try:
                more_page = self.driver.find_element_by_css_selector(
                    '._3iTUo')
                self.driver.execute_script(
                    "arguments[0].click();", more_page)
                time.sleep(1)
                click_more += 1
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
            try:
                temp['rating'] = float(rating_tags[i].text)
            except:
                temp['rating'] = 0
            try:
                temp['comment'] = txt_comment_tags[i].text
            except:
                temp['comment'] = ''
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
        self.restaurant_check = ''

    def run_kakao(self, queryInput):
        k_crawler = KakaoCrawler()
        k_crawler.get_kakao(queryInput)
        result = k_crawler.result_dict
        self.results[f'{queryInput}-kakao'] = result
        self.restaurant_check = k_crawler.restaurant_check

    def run_naver(self, queryInput):
        n_crawler = NaverCrawler()
        n_crawler.get_naver(queryInput, self.restaurant_check)
        result = n_crawler.result_dict
        self.results[f'{queryInput}-naver'] = result

    def save_data(self):
        with open('data.json', 'w') as json_file:
            json.dump(self.results, json_file, ensure_ascii=False)


run = run_app()

if __name__ == '__main__':
    queryInput = str(input('음식점 이름을 입력하세요(지역과 이름) : ').strip())
    run.run_kakao(queryInput)
    run.run_naver(queryInput)
    run.save_data()
