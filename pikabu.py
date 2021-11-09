import time
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import time

chrome_options = Options()
chrome_options.add_argument('start-maximized')

driver = webdriver.Chrome(executable_path='./chromedriver.exe', options=chrome_options)

driver.get('https://pikabu.ru/')


for i in range(5):
    articles = driver.find_elements(By.TAG_NAME, 'article')
    actions = ActionChains(driver)
    actions.move_to_element(articles[-1])
    # actions.key_down(Keys.LEFT_CONTROL).key_down(Keys.c).key_up(Keys.LEFT_CONTROL).key_up(Keys.c)
    actions.perform()
    time.sleep(5)


















