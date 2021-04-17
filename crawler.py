import time
import requests

from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains


driver = webdriver.Chrome(r"/Users/jihun/Mywork/RealClassifier/chromedriver")
url = 'https://map.kakao.com/'
driver.get(url)

action = ActionChains(driver)

# kakaomap review 찾기
driver.find_element_by_css_selector(
    '.query.tf_keyword').send_keys('용인시 '+'마약생고기')
driver.find_element_by_css_selector('.query.tf_keyword').send_keys(Keys.ENTER)
time.sleep(2)


# double click
review = driver.find_element_by_css_selector(
    '#info\.search\.place\.list > li.PlaceItem.clickArea.PlaceItem-ACTIVE > div.rating.clickArea > a')
action.double_click(review).perform()


driver.switch_to.window(driver.window_handles[-1])
time.sleep(2)

soup = BeautifulSoup(driver.page_source, 'html.parser')
ratings = soup.select('.grade_star')

print(ratings[1].text)
