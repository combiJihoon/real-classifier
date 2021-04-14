import time

from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains


driver = webdriver.Chrome(r"/Users/jihun/Mywork/RealClassifier/chromedriver")
url = 'https://map.kakao.com/'
driver.get(url)

actionChains = ActionChains(driver)

# kakaomap review 찾기
driver.find_element_by_css_selector(
    '.query.tf_keyword').send_keys('용인시 '+'마약생고기')
driver.find_element_by_css_selector('.query.tf_keyword').send_keys(Keys.ENTER)
time.sleep(2)


# double click
review = driver.find_element_by_css_selector(
    '#info\.search\.place\.list > li.PlaceItem.clickArea.PlaceItem-ACTIVE > div.rating.clickArea > a').action()
actionChains.double_click(review).perform()

# ratings = []
html = driver.page_source
soup = BeautifulSoup(html, 'html.parser')

kakao_rating = soup.select(
    '.grade_star').text

print(kakao_rating)
