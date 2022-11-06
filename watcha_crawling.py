from lib2to3.pgen2.driver import Driver
from pickle import NONE
from selenium import webdriver
from selenium.webdriver import ActionChains
from bs4 import BeautifulSoup
import pandas as pd 
import pymysql
import requests


browser = webdriver.Chrome()
browser.get("https://www.wavve.com/")
#browser.maximize_window()
#인기 방송 으로 이동
elem = browser.find_element_by_xpath("//*[@id='contents']/div[1]/section/div[1]/a")
elem.click()
elem = browser.find_element_by_xpath("//*[@id='multisection_index_2']/a")
elem.click()
browser.implicitly_wait(10)

## 인기 차트 검색 ## 
for i in range (20):
    actor_list = []
    genre_list = []
    xpath_string = "//*[@id='contents']/div[2]/div[" + str(i+1) +"]/a"
    elem = browser.find_element_by_xpath(xpath_string)
    img = elem.find_element_by_class_name("thumb-img").get_attribute("src")
    elem.click()
    ##제목, 출연진, DESCRIPTION, Platform ##

    ## 제목 ## 
    title = browser.find_element_by_class_name("player-bottom-contents").find_element_by_class_name("episode-number").text
    print(title)
    elem = browser.find_element_by_class_name("content-preview-box")
    ## dersciption
    description = elem.text
    elems = browser.find_elements_by_class_name("content-actor-list")
    browser.find_element_by_class_name("info-toggle-button").click()
    ## 출연진 ## 
    for elem in elems:
        actor_list.append(elem.text)
    genre_elem = browser.find_element_by_class_name("detail-view-content-txt").find_elements_by_tag_name("tr")
    if len(genre_elem) >= 3:
        elems = genre_elem[1].find_elements_by_class_name("genre")
        ## 장르 ## 
        for elem in elems:
            tmp_arr = elem.text.split("#")
            tmp_arr = tmp_arr[1].split(",")
            genre_list.append(tmp_arr[0])
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
    ### Media 가 존재 하는지 검사
    SQL_QUERY = "select media_id from Media WHERE name = '" + title + "';"
    cursor.execute(SQL_QUERY)
    result = cursor.fetchone()
    db.commit()
    if result == None:
    ### Media 가 존재 하는 경우 ###
        SQL_QUERY = "insert into Media (name,image_url,description) values (" +"'" +title +"'" +","+"'" +img +"'"+","+ "'"+description +"'"+ ")"
        cursor.execute(SQL_QUERY)
        SQL_QUERY = "SELECT LAST_INSERT_ID() from Media"
        cursor.execute(SQL_QUERY)
        result = cursor.fetchone()
        # auto increment 번호 가공
        media_num = result[0]
    else:
    ## Media 가 존재 하는 경우 ###
        media_num = result[0]
    # 출연진
    for actor in actor_list:
        #ACTOR 가 ACTOR TABLE 에 존재하는지 확인 
        SQL_QUERY = "select actor_id from Actor WHERE name = '" + actor + "';"
        cursor.execute(SQL_QUERY)
        result = cursor.fetchone()
        ## 존재하지 않는 경우
        if result == None:
            SQL_QUERY = "insert into Actor (name) values ('" + actor + "');"
            cursor.execute(SQL_QUERY)
            SQL_QUERY = "SELECT LAST_INSERT_ID() from Media"
            cursor.execute(SQL_QUERY)
            result = cursor.fetchone()
        actor_id = result[0]
        ## ACTOR_MEDIA TABLE 에 존재 하는 경우 
        SQL_QUERY = "SELECT media_actor_id from Media_Actor WHERE media_id = '" + str(media_num) +"' and actor_id = '" + str(actor_id) + "'"
        cursor.execute(SQL_QUERY)
        result = cursor.fetchone()
        if result == None:
            SQL_QUERY = "insert into  Media_Actor (media_id, actor_id) values('" + str(media_num) + "','" + str(actor_id) + "');"
            cursor.execute(SQL_QUERY)
    # 장르 넣기
    for genre in genre_list:
        #Genre 가 Genre TABLE 에 존재하는지 확인 
        SQL_QUERY = "select genre_id from Genre WHERE name = '" + genre + "';"
        cursor.execute(SQL_QUERY)
        result = cursor.fetchone()
        ## 존재하지 않는 경우
        if result == None:
            SQL_QUERY = "insert into Genre (name) values ('" + genre + "');"
            cursor.execute(SQL_QUERY)
            SQL_QUERY = "SELECT LAST_INSERT_ID() from Genre"
            cursor.execute(SQL_QUERY)
            result = cursor.fetchone()
        genre_id = result[0]
        ## ACTOR_MEDIA TABLE 에 존재 하는 경우 
        SQL_QUERY = "SELECT media_genre_id from Media_Genre WHERE media_id = '" + str(media_num) +"' and genre_id = '" + str(genre_id) + "'"
        cursor.execute(SQL_QUERY)
        result = cursor.fetchone()
        if result == None:
            SQL_QUERY = "insert into  Media_Genre (media_id, genre_id) values('" + str(media_num) + "','" + str(genre_id) + "');"
            cursor.execute(SQL_QUERY)
    # 플랫폼
    # 플랫폼_MEDIA 없을 때만 주입 
    SQL_QUERY = "SELECT media_platform_id from Media_Platform WHERE media_id = '" + str(media_num) + "'and platform_id = 2;"
    cursor.execute(SQL_QUERY)
    result = cursor.fetchone()
    if result == None:
        SQL_QUERY = "insert into  Media_Platform (media_id, platform_id) values('" + str(media_num) + "',4);"
        cursor.execute(SQL_QUERY)
    db.commit()
    browser.back()
