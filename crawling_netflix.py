from lib2to3.pgen2.driver import Driver
from pickle import NONE
from selenium import webdriver
from selenium.webdriver import ActionChains
from bs4 import BeautifulSoup
import pandas as pd 
import pymysql
import requests


browser = webdriver.Chrome()
browser.get("https://www.netflix.com/kr/")
#browser.maximize_window()
#로그인 PAGE 로 이동 
elem = browser.find_element_by_class_name("authLinks")
elem.click()

browser.implicitly_wait(10)
#아이디 입력
browser.find_element_by_id("id_userLoginId").send_keys("아이디")
#비밀번호 입력
browser.find_element_by_id("id_password").send_keys("비밀번호")
#로그인 버튼 누르기
elem = browser.find_element_by_class_name("login-button")
elem.click()
#사용자 선택
browser.implicitly_wait(10)
elem = browser.find_element_by_xpath("//*[@id='appMountPoint']/div/div/div[1]/div[1]/div[2]/div/div/ul/li[4]/div/a")
elem.click()
elem = browser.find_element_by_xpath("//*[@id='appMountPoint']/div/div/div[1]/div[1]/div[1]/div/div/ul/li[5]/a")
elem.click()
# 접속 완료 ... 
#Top 10 들어가기 
browser.implicitly_wait(10)
# 컨텐츠 pick
for i in range (5):
    browser.implicitly_wait(10)
    xpath_string = "#title-card-1-"+ str(i) + " > div.ptrack-content > a"
    elem = browser.find_element_by_css_selector(xpath_string)
    #이미지
    img = elem.find_element_by_class_name("boxart-image-in-padded-container").get_attribute("src")
    #제목
    title = elem.find_element_by_class_name("fallback-text-container").text
    elem.click()
    browser.implicitly_wait(10)
    #설명
    elem = browser.find_element_by_class_name("preview-modal-synopsis")
    description = elem.text
    browser.implicitly_wait(10)
    # 출연
    actor_list = []
    elem = browser.find_elements_by_class_name("previewModal--tags")
    actor_elems = elem[0].find_elements_by_class_name("tag-item")
    for actor_elem in actor_elems:
        tmp = actor_elem.text.split(",")
        actor_list.append(tmp[0])
    # 장르
    genre_list = []
    genre_elems = elem[1].find_elements_by_class_name("tag-item")
    for genre_elem in genre_elems:
        tmp = genre_elem.text.split(",")
        genre_list.append(tmp[0])
    ################## DB 넣기 코드 ######################
    host_name = "End 포인트 주소"
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
    SQL_QUERY = "SELECT media_platform_id from Media_Platform WHERE media_id = '" + str(media_num) + "'and platform_id = 1;"
    cursor.execute(SQL_QUERY)
    result = cursor.fetchone()
    if result == None:
        SQL_QUERY = "insert into  Media_Platform (media_id, platform_id) values('" + str(media_num) + "',1);"
        cursor.execute(SQL_QUERY)
    db.commit()
    ###################################################
    browser.back()
