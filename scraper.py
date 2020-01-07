from __future__ import unicode_literals
from bs4 import BeautifulSoup
import requests
import psycopg2

#!/usr/bin/env python
# coding=utf-8

urls = ["https://en.wikipedia.org/wiki/Ironman_World_Championship",
        "https://en.wikipedia.org/wiki/Giant_panda",
        "https://en.wikipedia.org/wiki/Ironman_Triathlon"]
        #"https://en.wikipedia.org/wiki/World_Triathlon_Corporation"
        #"https://en.wikipedia.org/wiki/Ironman_70.3",
        #"https://en.wikipedia.org/wiki/Marathon"
        #"https://en.wikipedia.org/wiki/Cloud_computing",
        #"https://en.wikipedia.org/wiki/Google"
        #"https://en.wikipedia.org/wiki/Car",
        #""]

pageID = 0
wordID = 0
fIndexID = 0

connection = psycopg2.connect(user="eoghan1",
                                  password="password",
                                  host="127.0.0.1",
                                  port="5432",
                                  database="wikipages")
cursor = connection.cursor()

sql_delete_query = """Delete from \"invertedIndex\""""
cursor.execute(sql_delete_query)
sql_delete_query = """Delete from \"forwardIndex\""""
cursor.execute(sql_delete_query)
sql_delete_query = """Delete from pages"""
cursor.execute(sql_delete_query)
sql_delete_query = """Delete from words"""
cursor.execute(sql_delete_query)

for j in range(0, len(urls)):
    url = urls[j]
    response = requests.get(url, timeout = 5)

    page_content = BeautifulSoup(response.content, "html.parser")
    textContent = []
    boldWords = []

    for i in range(0, len(page_content.find_all('p'))):
        paragraphs = page_content.find_all("p")[i].text
        textContent.append(paragraphs)

    for i in range(0, len(page_content.find_all('b'))):
        bold = page_content.find_all("b")[i].text
        boldWords.append(bold)

    boldWordsList = []
    boldWordsList = str(boldWords).split()

    connection.commit()

    postgres_insert_query = """ INSERT INTO \"pages\" (\"pageID\",\"Title\") VALUES (%s,%s)"""
    record_to_insert = (pageID, page_content.title.string)
    cursor.execute(postgres_insert_query, record_to_insert)

    connection.commit()

    wordList = []
    wordList = str(textContent).split()
    wordList[0] = (wordList[0])[1:]
    wordList[len(wordList) - 1] = (wordList[len(wordList) - 1])[:len(wordList[len(wordList) - 1]) - 1]
    temp = 0

    allowed = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789()"
    for i in range(0, len(wordList)):
        if any(wordList[i].startswith(x) for x in allowed):
             temp = 1           
        else:
            wordList[i] = (wordList[i])[1:]
        if any(wordList[i].endswith(x) for x in allowed):
            temp = 1
        else:
            wordList[i] = (wordList[i])[:len(wordList[i]) - 1]

    wordList = [item.strip() for item in wordList if str(item)]

    for i in range(0, len(wordList)):
        postgreSQL_select_Query = "select \"wordID\" from words where word = %s"
        cursor.execute(postgreSQL_select_Query, (wordList[i],))
        forwardIndex_WordID = cursor.fetchall()

        pageArray = []

        if len(forwardIndex_WordID) == 0:
            postgres_insert_query = """ INSERT INTO \"words\" (\"wordID\",word) VALUES (%s,%s)"""
            record_to_insert = (wordID, wordList[i])
            cursor.execute(postgres_insert_query, record_to_insert)
            connection.commit()
            postgres_insert_query = """ INSERT INTO \"forwardIndex\" (\"ID\",\"pageID\",\"wordID\") VALUES (%s,%s,%s)"""
            record_to_insert = (fIndexID, pageID, wordID)
            cursor.execute(postgres_insert_query, record_to_insert)
            connection.commit()
            pageArray.append(pageID)
            postgres_insert_query = """ INSERT INTO \"invertedIndex\" (\"wordID\",\"pageID\") VALUES (%s,%s)"""
            record_to_insert = (wordID, pageArray)
            cursor.execute(postgres_insert_query, record_to_insert)
            connection.commit()
            wordID = wordID + 1
        else:
            postgres_insert_query = """ INSERT INTO \"forwardIndex\" (\"ID\",\"pageID\",\"wordID\") VALUES (%s,%s,%s)"""
            record_to_insert = (fIndexID, pageID, forwardIndex_WordID[0])
            cursor.execute(postgres_insert_query, record_to_insert)
            connection.commit()
            pageArray.append(pageID)
            postgreSQL_select_Query = "select \"pageID\" from \"invertedIndex\" where \"wordID\" = %s"
            cursor.execute(postgreSQL_select_Query,forwardIndex_WordID[0])
            currentPages = cursor.fetchall()
            pageArray = currentPages[0][0]
            pageArray.append(pageID)
            pageArray = set(pageArray)
            pageArray = list(pageArray)
            postgres_update_query = """ update \"invertedIndex\" set \"pageID\" = %s where \"wordID\" = %s"""
            cursor.execute(postgres_update_query, (pageArray, forwardIndex_WordID[0]))
            connection.commit()

        fIndexID = fIndexID + 1
    pageID = pageID + 1

cursor.close()
connection.close()