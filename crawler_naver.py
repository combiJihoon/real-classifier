import time
import requests

from urllib.parse import quote_plus
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains


driver = webdriver.Chrome(r"/Users/jihun/Mywork/RealClassifier/chromedriver")
baseUrl = 'https://m.map.naver.com/search2/search.naver?query='
plusUrl = input('검색해 보아라: ')
# plusUrl = '용인시 마약생고기'
url = baseUrl + plusUrl
driver.get(url)

action = ActionChains(driver)

# navermap review 찾기
driver.find_element_by_css_selector(
    '#ct > div.search_listview._content._ctList > ul > li > div.item_info > a.a_item.a_item_distance._linkSiteview > div').click()
time.sleep(2)

soup = BeautifulSoup(driver.page_source, 'html.parser')
ratings = soup.select(
    '._1kUrA')

print(ratings[0].text[2:6])
