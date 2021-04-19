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

start = time.time()

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

# 총 평균 별점
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
review_by_page = []

# 다음 페이지 클릭

# i는 1~ , j는 1~5 단위의 페이지
i = j = 1
pageNum = 1
while True:
    try:
        # 별점, 리뷰, 날짜 출력
        soup = BeautifulSoup(driver.page_source, 'html.parser')
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

        print('현재 페이지: '+str(pageNum))
        # print(review_info)

        # # 페이지가 5의 배수인지 확인 : 5의 배수면 '다음'을 누를 것
        # if i % 5 == 0:
        #     # 다음 누르기
        #     btn_next = driver.find_element_by_class_name('.btn_next')
        #     driver.execute_script("arguments[0].click();", btn_next)
        #     time.sleep(2)
        # # 5의 배수가 아니라면 숫자 누를 것
        # else:
        element = driver.find_element_by_xpath(
            '//*[@id = "mArticle"]/div[5]/div[4]/div/a['+str(i)+']')
        driver.execute_script("arguments[0].click();", element)
        if i == 5 and j == 1:
            i = 2
            j += 1
        elif i == 6 and j >= 2:
            i = 2
            j += 1
        else:
            i += 1
        pageNum += 1

        time.sleep(2)

        # WebDriverWait(driver, 20).until(EC.element_to_be_clickable(
        #     (By.XPATH, '//*[@id = "mArticle"]/div[5]/div[4]/div/a['+str(i)+']'))).click()
        # driver.find_element_by_css_selector(
        #     '#mArticle > div.cont_evaluation > div.evaluation_review > div')
        # next_pg = driver.find_element_by_link_text(str(i)).click()
        # action.move_to_element(next_pg).perform()
        # action.click().perform()
        time.sleep(2)

    except NoSuchElementException:
        break

end = time.time()

# 몇 초 걸렸는지 확인
total_time = int(end-start)

driver.quit()


# print('최저 별점을 남긴 고객들의 리뷰 내용입니다: ')
# print('최고 별점을 남긴 고객들의 리뷰 내용입니다: ')

print('------------------------------')
print('전체 리뷰 크롤링 결과')
print('걸린시간: ' + str(total_time) + '초')
print('총 페이지 수 : ' + str(pageNum))
print('------------------------------')
print(review_by_page)

print(len(review_by_page))
