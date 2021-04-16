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
# review_url = driver.current_url
# review_url = "'"+review_url+"'"
# response = requests.get(review_url)

# soup = BeautifulSoup(response.text, 'html.parser')
html = driver.page_source

soup = BeautifulSoup(html.content, 'lxml')
# rating = soup.select(
#     '#mArticle > div.cont_evaluation > div.ahead_info > div > em')
rating = soup.select('#mArticle > div.cont_evaluation > div.ahead_info > div')
#mArticle > div.cont_evaluation
print(rating)
# rating_list = []
# if len(kakao_rating_list) != 0:
#     for rating in kakao_rating_list:
#         rating_list.append(rating)
# else:
#     print('왜 안됩니까요?')
