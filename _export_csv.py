import pymysql
import csv

db = pymysql.connect(host='localhost', port=3306, user='root',
                     passwd='mysql', db='ccc', charset='utf8')

f = open('./posts.tsv', 'w', encoding='utf-8', newline='')

csvwriter = csv.writer(f, delimiter='\t')
idx = 0

try:
    cursor = db.cursor()
    sql = "SELECT * FROM posts"
    cursor.execute(sql)
    result = cursor.fetchall()
    for row_data in result:
        print(row_data[2])
        id = row_data[2]
        contents = row_data[1]
        print([row_data[2], row_data[1]])
        csvwriter.writerow([row_data[2], row_data[1]])
finally:
    db.close()
    f.close()
