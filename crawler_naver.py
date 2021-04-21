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
review_page = driver.find_element_by_xpath(
    '//*[@id="app-root"]/div/div[2]/div[3]/div/div/div/div/a[4]')
driver.execute_script("arguments[0].click();", review_page)
time.sleep(1)

# '더보기' 누르면 리뷰 10개 더 등장 -> xpath에서 숫자 증가함 i = 1~ 10 하고 10 되면 +1 시켜서 반복문 바꿔야 함
# 별점, 리뷰, 날짜 출력
soup = BeautifulSoup(driver.page_source, 'html.parser')

pageNum = 1
j = 0
while True:
    try:
        review_info = []
        for i in range(j, j+10):
            temp = []
            # print(all_reviews)
            reviews = soup.select(
                '#app-root > div > div.place_detail_wrapper > div:nth-of-type(5) > div:nth-of-type(4) > div:nth-of-type(4) > div:nth-of-type(2) > ul> li')
            rating = reviews[i].select(
                '#app-root > div > div.place_detail_wrapper > div:nth-of-type(5) > div:nth-of-type(4) > div:nth-of-type(4) > div:nth-of-type(2) > ul > li:nth-of-type(' + str(i+1) + ') > div > div._1ZcDn > div._3D_HC > span._2tObC').text
            txt_comment = reviews[i].select(
                '#app-root > div > div.place_detail_wrapper > div:nth-of-type(5) > div:nth-of-type(4) > div:nth-of-type(4) > div:nth-of-type(2) > ul > li:nth-of-type(' + str(i+1) + ') > div > div.PVBo8 > a > span').text
            date = reviews[i].select(
                '#app-root > div > div.place_detail_wrapper > div:nth-of-type(5) > div:nth-of-type(4) > div:nth-of-type(4) > div:nth-of-type(2) > ul > li:nth-of-type(' + str(i+1) + ') > div > div._1ZcDn > div.ZvQ8X > span:nth-of-type(1)').text
            temp.append(rating)
            temp.append(txt_comment)
            temp.append(date)
            review_info.append(temp)
            # 기본 10개 리뷰 크롤링 끝나면 11부터 10개 크롤링 시작
            if i == 9:
                print('현재 페이지: '+str(pageNum))
                j += 10
                pageNum += 1
                # '더보기' xpath는 항상 동일함
                element = driver.find_element_by_xpath(
                    '//*[@id = "app-root"]/div/div[2]/div[5]/div[4]/div[4]/div[2]/a')
                driver.execute_script("arguments[0].click();", element)
        review_by_page.append(review_info)

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
