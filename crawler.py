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

kakao = 'https://map.kakao.com/'
# naver url은 query 부분까지 나옴
naver = 'https://m.map.naver.com/search2/search.naver?query='

# 해야하는 것
# 가게가 없을 경우, 리뷰가 없을 경우 예외처리
# 사용자 input 받고 checker 실행한 뒤 'driver'도 리턴해 줘야 함


def getDriver():
    options = ChromeOptions()
    options.add_argument('headless')
    options.add_argument("disable-gpu")

    driver = webdriver.Chrome(
        r"/Users/jihun/Mywork/django-project/revclassifier/chromedriver")

    return driver


def kakao_checker(queryInput, driver):
    global kakao

    driver.get(kakao)
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
    restaurant_list = []
    for restaurant in restaurants_to_be_list:
        restaurant_list.append(restaurant.text)

    return restaurant_list, driver


def naver_checker(queryInput, driver):
    global naver
    # plusUrl = '마북동 전주콩나물해장국'
    url = naver + queryInput
    driver.get(url)

    # 원하는 음식점이 맞는지 확인 : 음식점 리스트 출력 및 선택
    # html로 옮기면 사용자가 클릭하도록 바꾸어야 할 듯
    WebDriverWait(driver, 3).until(EC.element_to_be_clickable(
        (By.CSS_SELECTOR, 'div.item_tit._title > strong')))
    restaurants_to_be_list = driver.find_elements_by_css_selector(
        'div.item_tit._title > strong')
    restaurant_list = []
    for restaurant in restaurants_to_be_list:
        restaurant_list.append(restaurant.text)

    return restaurant_list, driver


def kakao_crawler(restaurant_list, restaurant_check, driver):

    action = ActionChains(driver)
    my_xpath = restaurant_check

    # 4번째 자리(3번째 인덱스)에 항상 광고가 들어와 있음 -> 따라서 이 때부터 index를 변경해 줘야 함
    my_index = restaurant_list.index(my_xpath)
    if my_index >= 3:
        my_index += 1

    # 해당 음식점 페이지로 이동 : '리뷰' 글씨 클릭해야 함
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable(
        (By.XPATH, '//*[@id = "info.search.place.list"]/li[' + str(my_index+1) + ']/div[4]/a')))
    time.sleep(2)

    review = driver.find_element_by_xpath(
        '//*[@id = "info.search.place.list"]/li[' + str(my_index+1) + ']/div[4]/a')
    action.double_click(review).perform()

    driver.switch_to.window(driver.window_handles[-1])
    time.sleep(2)

    # 총 평균 별점
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    # 총 평점 출력
    try:
        ratings = soup.select('.grade_star')
        final_rating = ratings[1].text
    except:
        return ''

    count = 0

    # 다음 페이지 클릭
    # i는 1~ , j는 1~5 단위의 페이지
    i = j = 1
    pageNum = 1
    count = 0
    review_info = []

    while True:
        try:
            reviewCrawler_kakao(count, review_info, driver)
            # review_by_page.append(review_info)

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
                reviewCrawler_kakao(count, review_info, driver)
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

    driver.quit()

    return final_rating, low_review_info, high_review_info


def naver_crawler(restaurant_list, restaurant_check, driver):
    my_xpath = restaurant_check
    my_index = restaurant_list.index(my_xpath)
    # 해당 음식점 페이지로 이동
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable(
        (By.XPATH, '//*[@id="ct"]/div[2]/ul/li[' + str(my_index+1) + ']/div[1]/a/div'))).click()
    time.sleep(2)

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    # 총 평점 구하기 : 없을 경우 리뷰도 없으므로 빈 문자열 리턴
    try:
        ratings = soup.select(
            '._1kUrA')
        final_rating = ratings[0].text[2:6]
    except:
        return ''

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

    # 더보기 클릭이 다 끝난 후 전체적으로 크롤링
    li_tags = driver.find_elements_by_css_selector('._2Cv-r')
    rating_tags = driver.find_elements_by_css_selector(
        '._2tObC')
    txt_comment_tags = driver.find_elements_by_css_selector(
        '.WoYOw')
    date_tags = driver.find_elements_by_css_selector(
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

    driver.quit()

    return final_rating, low_review_info, high_review_info


def reviewCrawler_kakao(count, review_info, driver):
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
        count += 1


# 전체 크롤링 과정 다시 반복 후 restaurant_list, driver 리턴

driver = getDriver()
restaurant_list, driver = kakao_checker("영광보쌈", driver)
driver.quit()


def main():
    freeze_support()

    p1 = Process(target=kakao_crawler, args=(restaurant_list,
                                             "영광보쌈", driver,))
    p2 = Process(target=naver_crawler, args=(restaurant_list,
                                             "영광보쌈", driver,))

    p1.daemon = True
    p2.daemon = True

    p1.start()
    p2.start()

    p1.close()
    p2.close()

    p1.join()
    p2.join()


if __name__ == '__main__':
    main()
