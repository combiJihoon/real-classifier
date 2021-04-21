import time
import requests

from urllib.parse import quote_plus
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException

start = time.time()

driver = webdriver.Chrome(r"/Users/jihun/Mywork/RealClassifier/chromedriver")
baseUrl = 'https://m.map.naver.com/search2/search.naver?query='
plusUrl = input('검색해 보아라: ')
# plusUrl = '용인시 마약생고기'
url = baseUrl + plusUrl
driver.get(url)

action = ActionChains(driver)

# 해당 음식점 페이지로 이동
WebDriverWait(driver, 10).until(EC.element_to_be_clickable(
    (By.XPATH, '//*[@id="ct"]/div[2]/ul/li[1]/div[1]/a[2]'))).click()
time.sleep(2)


soup = BeautifulSoup(driver.page_source, 'html.parser')
ratings = soup.select(
    '._1kUrA')

print(ratings[0].text[2:6])


# page 이동하며 review_info 크롤링
review_by_page = []

# 리뷰 페이지로 이동
# WebDriverWait(driver, 10).until(EC.element_to_be_clickable(
#     (By.CSS_SELECTOR, '#app-root > div > div.place_detail_wrapper > div:nth-of-type(5) > div:nth-of-type(4) > div:nth-of-type(4) > div._2kAri > a'))).click()
reviews = driver.find_element_by_xpath(
    '//*[@id="app-root"]/div/div[2]/div[3]/div/div/div/div/a[4]')
driver.execute_script("arguments[0].click();", reviews)
time.sleep(1)

# 다음 페이지 클릭
# i는 1~ , j는 1~5 단위의 페이지
pageNum = 1
while True:
    try:
        # 별점, 리뷰, 날짜 출력
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        all_reviews = soup.select(
            '#app-root > div > div.place_detail_wrapper > div:nth-of-type(5) > div:nth-of-type(4) > div:nth-of-type(4) > div:nth-of-type(2) > ul > li')
        # print(all_reviews)

        review_info = []
        for review in all_reviews:
            temp = []
            rating = review.select_one(
                '#app-root > div > div.place_detail_wrapper > div:nth-of-type(5) > div:nth-of-type(4) > div:nth-of-type(4) > div:nth-of-type(2) > ul > li> div > div._1ZcDn > div._3D_HC > span._2tObC').text
            txt_comment = review.select_one(
                '#app-root > div > div.place_detail_wrapper > div:nth-of-type(5) > div:nth-of-type(4) > div:nth-of-type(4) > div:nth-of-type(2) > ul > li> div > div.PVBo8 > a > span').text
            date = review.select_one(
                '#app-root > div > div.place_detail_wrapper > div:nth-of-type(5) > div:nth-of-type(4) > div:nth-of-type(4) > div:nth-of-type(2) > ul > li> div > div._1ZcDn > div.ZvQ8X > span:nth-of-type(1)').text
            temp.append(rating)
            temp.append(txt_comment)
            temp.append(date)
            review_info.append(temp)

        review_by_page.append(review_info)

        print('현재 페이지: '+str(pageNum))
        # print(review_info)

        element = driver.find_element_by_xpath(
            '//*[@id = "app-root"]/div/div[2]/div[5]/div[4]/div[4]/div[2]/a')
        driver.execute_script("arguments[0].click();", element)
        # 페이지 이동
        # if i == 5 and j == 1:
        #     i = 2
        #     j += 1
        # elif i == 6 and j >= 2:
        #     i = 2
        #     j += 1
        # else:
        #     i += 1
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


# # rating = review.select_one(
# #     '#app-root > div > div.place_detail_wrapper > div:nth-of-type(5) > div:nth-of-type(4) > div:nth-of-type(4) > div:nth-of-type(2) > ul > li> div > div._1ZcDn > div._3D_HC > span._2tObC').text
# # txt_comment = review.select_one(
# #     '#app-root > div > div.place_detail_wrapper > div:nth-of-type(5) > div:nth-of-type(4) > div:nth-of-type(4) > div:nth-of-type(2) > ul > li> div > div.PVBo8 > a > span').text
# # date = review.select_one(
# #     '#app-root > div > div.place_detail_wrapper > div:nth-of-type(5) > div:nth-of-type(4) > div:nth-of-type(4) > div:nth-of-type(2) > ul > li> div > div._1ZcDn > div.ZvQ8X > span:nth-of-type(1)').text
