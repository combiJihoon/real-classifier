import time
import requests

from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

driver = webdriver.Chrome(r"/Users/jihun/Mywork/RealClassifier/chromedriver")
url = 'https://map.kakao.com/'
driver.get(url)

action = ActionChains(driver)
queryInput = input('검색해 보아라 : ')
# kakaomap review 찾기
driver.find_element_by_css_selector(
    '.query.tf_keyword').send_keys(queryInput)
driver.find_element_by_css_selector('.query.tf_keyword').send_keys(Keys.ENTER)
time.sleep(2)


# double click
review = driver.find_element_by_css_selector(
    '#info\.search\.place\.list > li:nth-of-type(1) > div.rating.clickArea > a')
action.double_click(review).perform()


driver.switch_to.window(driver.window_handles[-1])
time.sleep(2)

soup = BeautifulSoup(driver.page_source, 'html.parser')
ratings = soup.select('.grade_star')

# 별점 출력
print(ratings[1].text)

# 최고 별점 리뷰 및 최저 별점 리뷰(+날짜) 출력
# data-page가 끝날 때까지 반복한 후 별점이 가장 낮을 때 그 내용 출력(클 때도 마찬가지)

# # 별점, 리뷰, 날짜 출력
# all_reviews = soup.select(
#     '#mArticle > div.cont_evaluation > div.evaluation_review > ul > li')

# # print(all_reviews)
# review_info = []
# for review in all_reviews:
#     temp = []
#     rating = review.select_one(
#         '#mArticle > div.cont_evaluation > div.evaluation_review > ul > li > div > div > em').text
#     txt_comment = review.select_one(
#         '#mArticle > div.cont_evaluation > div.evaluation_review > ul > li > div.comment_info > p > span').text
#     date = review.select_one(
#         '#mArticle > div.cont_evaluation > div.evaluation_review > ul > li > div.comment_info > div > span.time_write').text
#     temp.append(rating)
#     temp.append(txt_comment)
#     temp.append(date)
#     review_info.append(temp)


# print(review_info)

# page 이동하며 review_info 크롤링
while True:
    review_by_page = []
    for i in range(1, 20):
        # 별점, 리뷰, 날짜 출력
        all_reviews = soup.select(
            '#mArticle > div.cont_evaluation > div.evaluation_review > ul > li')

        # print(all_reviews)
        review_info = []
        for review in all_reviews:
            temp = []
            rating = review.select_one(
                '#mArticle > div.cont_evaluation > div.evaluation_review > ul > li > div > div > em').text
            txt_comment = review.select_one(
                '#mArticle > div.cont_evaluation > div.evaluation_review > ul > li > div.comment_info > p > span').text
            date = review.select_one(
                '#mArticle > div.cont_evaluation > div.evaluation_review > ul > li > div.comment_info > div > span.time_write').text
            temp.append(rating)
            temp.append(txt_comment)
            temp.append(date)
            review_info.append(temp)

        review_by_page.append(review_info)

        time.sleep(2)
        # 다음 페이지 클릭
        next_page_btn = driver.find_element_by_xpath(
            '//*[@id = "mArticle"]/div[6]/div[4]/div/a['+str(i)+']')
        try:
            next_page_btn.click()
        except NoSuchElementException:
            break
        time.sleep(2)

# print('최저 별점을 남긴 고객들의 리뷰 내용입니다: ')
# print('최고 별점을 남긴 고객들의 리뷰 내용입니다: ')


driver.quit()

print(review_by_page)
