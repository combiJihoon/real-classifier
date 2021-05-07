import time
import requests

from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver import ChromeOptions
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

start = time.time()

options = ChromeOptions()
options.add_argument('headless')
options.add_argument("disable-gpu")

driver = webdriver.Chrome(
    r"/Users/jihun/Mywork/RealClassifier/chromedriver", options=options)

# driver = webdriver.Chrome(
#     r"/Users/jihun/Mywork/RealClassifier/chromedriver")
url = 'https://map.kakao.com/'
driver.get(url)

action = ActionChains(driver)
queryInput = input('검색해 보아라 : ')
# kakaomap review 찾기
driver.find_element_by_css_selector(
    '.query.tf_keyword').send_keys(queryInput)
driver.find_element_by_css_selector('.query.tf_keyword').send_keys(Keys.ENTER)
time.sleep(2)


# 원하는 음식점이 맞는지 확인 : 음식점 리스트 출력 및 선택
# html로 옮기면 사용자가 클릭하도록 바꾸어야 할 듯
WebDriverWait(driver, 5).until(EC.element_to_be_clickable(
    (By.CSS_SELECTOR, 'strong.tit_name > a')))
restaurants_to_be_list = driver.find_elements_by_css_selector(
    'strong.tit_name > a.link_name')
restaurant_list = []
for restaurant in restaurants_to_be_list:
    restaurant_list.append(restaurant.text)

print('음식점 리스트 확인해 보라')
print(restaurant_list)
my_xpath = input('원하는 이름 말하라 : ')

# 4번째 자리(3번째 인덱스)에 항상 광고가 들어와 있음 -> 따라서 이 때부터 index를 변경해 줘야 함
my_index = restaurant_list.index(my_xpath)
if my_index >= 3:
    my_index += 1
print(my_index)

# 해당 음식점 페이지로 이동 : '리뷰' 글씨 클릭해야 함
WebDriverWait(driver, 10).until(EC.element_to_be_clickable(
    (By.XPATH, '//*[@id = "info.search.place.list"]/li[' + str(my_index+1) + ']/div[4]/a')))
time.sleep(2)

review = driver.find_element_by_xpath(
    '//*[@id = "info.search.place.list"]/li[' + str(my_index+1) + ']/div[4]/a')
action.double_click(review).perform()


driver.switch_to.window(driver.window_handles[-1])
time.sleep(2)

# ----------

# 총 평균 별점
soup = BeautifulSoup(driver.page_source, 'html.parser')
ratings = soup.select('.grade_star')


def reviewCrawler():
    # 별점, 리뷰, 날짜 출력
    soup = BeautifulSoup(driver.page_source, 'html.parser')
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


# 별점 출력
try:
    final_rating = ratings[1].text
    print(final_rating)

    # 다음 페이지 클릭
    # i는 1~ , j는 1~5 단위의 페이지
    i = j = 1
    pageNum = 1
    count = 0
    review_info = []

    while True:
        try:
            reviewCrawler()
            # review_by_page.append(review_info)

            print('현재 페이지: '+str(pageNum))
            if count >= 100:
                break
            try:
                element = driver.find_element_by_xpath(
                    '//*[@id = "mArticle"]/div[5]/div[4]/div/a['+str(i)+']')
                driver.execute_script("arguments[0].click();", element)
            # 2페이지까지 밖에 없을 경우 예외처리 후 크롤링
            except:
                element = driver.find_element_by_xpath(
                    '//*[@id = "mArticle"]/div[4]/div[4]/div/a')
                driver.execute_script("arguments[0].click();", element)
                time.sleep(2)
                reviewCrawler()
                count += 1
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

except IndexError:
    print('아직 리뷰가 없습니다.')

print('------------------------------')
print('전체 리뷰 크롤링 결과')
print('총 페이지 수 : ' + str(pageNum))
print('크롤링한 리뷰 수 : ' + str(count))
print('------------------------------')
print(review_info)
print('------------------------------')

print('최저 별점을 남긴 고객들의 리뷰 내용입니다: ')
if len(review_info) >= 10:
    print(review_info[:6])
elif 0 < len(review_info) < 10:
    print(review_info[0])
elif len(review_info) == 0:
    print('아직 리뷰가 없어서 확인이 불가능 합니다.')

print('------------------------------')
print('최고 별점을 남긴 고객들의 리뷰 내용입니다: ')
if len(review_info) >= 10:
    print(review_info[-6:])
elif 0 < len(review_info) < 10:
    print(review_info[-1])
elif len(review_info) == 0:
    print('아직 리뷰가 없어서 확인이 불가능 합니다.')

end = time.time()

# 몇 초 걸렸는지 확인
total_time = int(end-start)
print('걸린시간: ' + str(total_time) + '초')

# driver.quit()

driver.close()
