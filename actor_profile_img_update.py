from lib2to3.pgen2.driver import Driver
from pickle import NONE
from selenium import webdriver
from selenium.webdriver import ActionChains
from bs4 import BeautifulSoup
import pandas as pd 
import pymysql
import requests

host_name = ""
username = ""
password = ""
database_name = ""

db =  pymysql.connect(
    host = host_name,
    port = 3306,
    user = username,
    password = password,
    db = database_name,
    charset = 'utf8'
)

cursor = db.cursor()
cursor.execute('set names utf8')
db.commit()

SQL_QUERY = "select name from Actor WHERE profile_image_url is null"
cursor.execute(SQL_QUERY)
result = cursor.fetchall()
name_arr = []
for res in result:
    # 배우 이름
    name = res[0]
    if not len(name) == 0:
        name_arr.append(name)


browser = webdriver.Chrome()
browser.get("https://search.naver.com/search.naver?where=image")
#browser.maximize_window()
#로그인 PAGE 로 이동 
for name in name_arr:
    browser.implicitly_wait(10)
    elem = browser.find_element_by_id("nx_query").send_keys(name)
    browser.find_element_by_class_name("bt_search").click()
    browser.implicitly_wait(10)
    elem = browser.find_element_by_class_name("photo_tile")
    elem = elem.find_elements_by_class_name("thumb")
    img = elem[1].find_element_by_tag_name("img").get_attribute("src")
    SQL_QUERY = "update Actor set profile_image_url = '" + img + "'WHERE name = '"+ name + "';"
    cursor.execute(SQL_QUERY)
    db.commit()
    browser.back()
