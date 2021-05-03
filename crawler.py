import time
import requests

from urllib.parse import quote_plus
from bs4 import BeautifulSoup


from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

start = time.time()

kakao = 'https://map.kakao.com/'
# naver url은 query 부분까지 나옴
naver = 'https://m.map.naver.com/search2/search.naver?query='


def crawler(userUrl):
    global kakao
    global naver
    driver = webdriver.Chrome(
        r"/Users/jihun/Mywork/RealClassifier/chromedriver")

    if userUrl == kakao:
        return
    elif userUrl == naver:
        return
