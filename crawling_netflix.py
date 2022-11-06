```python
from lib2to3.pgen2.driver import Driver
from pickle import NONE
from selenium import webdriver
from selenium.webdriver import ActionChains
from bs4 import BeautifulSoup
import pandas as pd 
import pymysql
import requests

browser = webdriver.Chrome()
browser.get("https://watcha.com/")
browser.find_element_by_class_name("css-qxkazn").click()

browser.implicitly_wait(10)
#아이디 입력
browser.find_element_by_class_name("css-2sw17l").send_keys("")
#비밀번호 입력
browser.find_element_by_class_name("css-s8pas4").send_keys("")
browser.find_element_by_class_name("css-11a3zmg").click()
browser.implicitly_wait(10)
#사용자 선택
browser.find_element_by_xpath("//*[@id='root']/div[1]/main/div/section/ul/li[1]/button").click()
browser.implicitly_wait(10)
browser.find_element_by_xpath("//*[@id='root']/div[1]/main/div[2]/section[3]/div[1]/div[2]/a").click()
browser.implicitly_wait(10)

for i in range(1,4):
    for j in range(1,7):
        xpath = "//*[@id='root']/div[1]/main/div[3]/section/div["+ str(i) +"]/div/ul/li["+ str(j) + "]/article[1]/a"
        browser.find_element_by_xpath(xpath).click()
        browser.implicitly_wait(10)
        elem = browser.find_element_by_class_name("css-fam3cq-StyledImageContainer")
        img = elem.find_element_by_tag_name("img").get_attribute("src")
        title = browser.find_element_by_xpath("//*[@id='root']/div[1]/main/div[2]/header[1]/div/section/div[2]/h1").text
        description = browser.find_element_by_class_name("css-1r9g1ow").text
        actor_list = []
        genre_list = []
        elems = browser.find_elements_by_class_name("css-11zhy3w")
        for p in range(len(elems)//2):
            position = elems[2*p + 1].find_element_by_class_name("css-hbs6kl-AccessoryModule").text
            if '연' in position or '우' in position:
                actor = elems[2*p + 1].find_element_by_class_name("css-15vtjyx").text
                actor_list.append(actor)
        genre_elem = browser.find_element_by_class_name("css-7kpqz6")
        genres = genre_elem.find_elements_by_class_name("css-1wnw4hn")
        for g in genres:
            genre = g.text
            genre_list.append(genre)
        print(title,description,actor_list,genre_list)
         ################## DB 넣기 코드 ######################
        host_name = ""
        username = ""
        password = ""
        database_name = "ott_damoa"

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
            SQL_QUERY = "insert into  Media_Platform (media_id, platform_id) values('" + str(media_num) + "',2);"
            cursor.execute(SQL_QUERY)
        db.commit()
        browser.back()
        browser.implicitly_wait(100) 
    browser.execute_script("window.scrollTo(0, 300)")
```
