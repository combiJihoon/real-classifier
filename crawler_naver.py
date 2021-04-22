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
# plusUrl = input('검색해 보아라: ')
plusUrl = '마북동 마북173'
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


# 리뷰 페이지로 이동
# WebDriverWait(driver, 10).until(EC.element_to_be_clickable(
#     (By.CSS_SELECTOR, '#app-root > div > div.place_detail_wrapper > div:nth-of-type(5) > div:nth-of-type(4) > div:nth-of-type(4) > div._2kAri > a'))).click()

# '스타벅스' 같은 경우 메뉴 바에 '선물하기'가 있어 '리뷰' 메뉴의 위치가 달라지게 된다.
# 따라서, 아래와 같이 try & except로 예외처리를 한다.
try:
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable(
        (By.XPATH, '//*[@id="app-root"]/div/div[2]/div[3]/div/div/div/div/a[7]')))

    review_page = driver.find_element_by_xpath(
        '//*[@id="app-root"]/div/div[2]/div[3]/div/div/div/div/a[4]')
    driver.execute_script("arguments[0].click();", review_page)
    time.sleep(1)
except:
    review_page = driver.find_element_by_xpath(
        '//*[@id="app-root"]/div/div[2]/div[3]/div/div/div/div/a[3]')
    driver.execute_script("arguments[0].click();", review_page)
    time.sleep(1)


# 더보기 계속 클릭하기
while True:
    try:
        more_page = driver.find_element_by_css_selector('._3iTUo')
        driver.execute_script("arguments[0].click();", more_page)
        time.sleep(1)
    except:
        break


while True:
    try:
        # 더보기 클릭이 다 끝난 후 전체적으로 크롤링
        li_tags = driver.find_elements_by_css_selector('._2Cv-r')
        rating_tags = driver.find_elements_by_css_selector(
            '._2tObC')
        txt_comment_tags = driver.find_elements_by_css_selector(
            '.WoYOw')
        date_tags = driver.find_elements_by_css_selector(
            'div.ZvQ8X > span:nth-of-type(1)')

        total_num = 0
        review_by_page = []
        for i in range(len(li_tags)):
            temp = []
            rating = rating_tags[i].text
            txt_comment = txt_comment_tags[i].text
            date = date_tags[i].text

            temp.append(rating)
            temp.append(txt_comment)
            temp.append(date)

            print(temp)
            total_num += 1
            review_by_page.append(temp)
    except NoSuchElementException:
        break

end = time.time()

# 몇 초 걸렸는지 확인
total_time = int(end-start)

# driver.quit()


# print('최저 별점을 남긴 고객들의 리뷰 내용입니다: ')
# print('최고 별점을 남긴 고객들의 리뷰 내용입니다: ')

print('------------------------------')
print('전체 리뷰 크롤링 결과')
print('걸린시간: ' + str(total_time) + '초')
# print('총 페이지 수 : ' + str(pageNum))
print('총 크롤링 리스트 개수 : ' + str(total_num))
print('------------------------------')
# print(review_info)
# print(review_by_page)
