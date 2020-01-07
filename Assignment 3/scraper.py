from bs4 import BeautifulSoup
import requests
import psycopg2

urls = ["https://en.wikipedia.org/wiki/Ironman_World_Championship"]
        #"https://en.wikipedia.org/wiki/International_Triathlon_Union"
        #"https://en.wikipedia.org/wiki/Ironman_Triathlon",
        #"https://en.wikipedia.org/wiki/World_Triathlon_Corporation"
        #"https://en.wikipedia.org/wiki/Ironman_70.3",
        #"https://en.wikipedia.org/wiki/Marathon"
        #"https://en.wikipedia.org/wiki/Cloud_computing",
        #"https://en.wikipedia.org/wiki/Google"
        #"https://en.wikipedia.org/wiki/Car",
        #"https://en.wikipedia.org/wiki/Giant_panda"]

pageID = 0
wordID = 0
fIndexID = 0

connection = psycopg2.connect(user="eoghan1",
                                  password="password",
                                  host="127.0.0.1",
                                  port="5432",
                                  database="wikipages")
cursor = connection.cursor()

for j in range(0, len(urls)):
    url = urls[j]
    response = requests.get(url, timeout = 5)

    page_content = BeautifulSoup(response.content, "html.parser")
    textContent = []

    for i in range(0, len(page_content.find_all('p'))):
        paragraphs = page_content.find_all("p")[i].text
        textContent.append(paragraphs)

    sql_delete_query = """Delete from forwardIndex"""
    cursor.execute(sql_delete_query)
    sql_delete_query = """Delete from pages"""
    cursor.execute(sql_delete_query)
    sql_delete_query = """Delete from words"""
    cursor.execute(sql_delete_query)

    connection.commit()

    postgres_insert_query = """ INSERT INTO \"pages\" (\"pageID\",\"Title\") VALUES (%s,%s)"""
    record_to_insert = (pageID, page_content.title.string)
    cursor.execute(postgres_insert_query, record_to_insert)

    connection.commit()

    pageID = pageID + 1

    wordList = []
    wordList = str(textContent).split()

    for i in range(0, len(wordList)):
        postgreSQL_select_Query = "select * from words where word = %s"

        cursor.execute(postgreSQL_select_Query, (wordList[i],))

        if len(cursor.fetchall()) == 0:
            postgres_insert_query = """ INSERT INTO \"words\" (\"wordID\",word) VALUES (%s,%s)"""
            record_to_insert = (wordID, wordList[i])
            cursor.execute(postgres_insert_query, record_to_insert)
            connection.commit()

            wordID = wordID + 1

        postgres_insert_query = """ INSERT INTO \"forwardIndex\" (\"ID\",\"pageID\",\"wordID\") VALUES (%s,%s,%s)"""
        record_to_insert = (fIndexID, pageID - 1, wordID -1)
        cursor.execute(postgres_insert_query, record_to_insert)
        connection.commit()

        fIndexID = fIndexID + 1

        postgres_insert_query = """ INSERT INTO \"invertedIndex\" (\"pageID\",\"wordID\") VALUES (%s,%s)"""
        record_to_insert = (pageID - 1, wordID - 1 )
        cursor.execute(postgres_insert_query, record_to_insert)
        connection.commit()

        
cursor.close()
connection.close()
