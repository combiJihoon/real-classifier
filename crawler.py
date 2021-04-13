import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains


driver = webdriver.Chrome(r"/Users/jihun/Mywork/RealClassifier/chromedriver")
url = 'https://map.kakao.com/'
driver.get(url)

actionChains = ActionChains(driver)


driver.find_element_by_css_selector(
    '.query.tf_keyword').send_keys('용인시 '+'마약생고기')
driver.find_element_by_css_selector('.query.tf_keyword').send_keys(Keys.ENTER)
time.sleep(2)

# click doesn't work....
review = driver.find_element_by_css_selector('.review')
# review = driver.find_element(By.ID, 'numberofreview')
actionChains.double_click(review).perform()
