import pymysql
import pandas as pd
import sys

db = pymysql.connect(host='localhost', port=3306, user='root',
                     passwd='mysql', db='ccc', charset='utf8')
SQL = "SELECT * FROM new_posts"
# SQL = "SHOW TABLES"
df = pd.read_sql(SQL, db)

print(df)