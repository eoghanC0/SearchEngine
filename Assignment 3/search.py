import psycopg2

connection = psycopg2.connect(user="eoghan1",
                                  password="password",
                                  host="127.0.0.1",
                                  port="5432",
                                  database="wikipages")
cursor = connection.cursor()

search_keyword = raw_input("Enter search key word(s)")

postgres_select_query = "select \"Title\" from pages where \"Text\" like '%" + (search_keyword) + "%'"

cursor.execute(postgres_select_query)

page_records = cursor.fetchall()

if len(page_records) == 0:
    print("no records contain that phrase")
else:
    for row in page_records:
        print("Title = ", row[0],)
        #print("Text = ", row[1], "\n")

cursor.close()
connection.close()