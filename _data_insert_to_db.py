import pymysql
import datetime
import sys


'''
create table posts(id int(11) unsigned NOT NULL AUTO_INCREMENT, contents text, idx int(11) not null, primary key (id)) DEFAULT CHARSET=utf8mb4;
ALTER table posts convert to CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE posts CHANGE contents contents text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
'''

db = pymysql.connect(host='localhost', port=3306, user='root',
                     passwd='mysql', db='ccc', charset='utf8')

f = open('bns_total_review.txt')
l = f.readlines()


idx = 0


posts = []
post = ""
for s in l:
    cursor = db.cursor()
    if ("###" in s):
        try:
            post_idx = int(s.split("###")[1])-1
            # now = datetime.datetime.now()
            # now.strftime('%Y-%m-%d %H:%M:%S')
            escaped_post = pymysql.escape_string(post)
            sql = "insert into posts(contents, idx) values(\"{}\", \"{}\")".format(
                escaped_post, post_idx)
            cursor.execute(sql)
            db.commit()
            post = ""
            idx += 1
        except:
            print("Unexpected error:", sys.exc_info()[0])
    else:
        post += s

cursor.execute("insert into posts(contents, idx) values(\"{}\", \"{}\")".format(
    l[len(l)-1], post_idx+1))
db.commit()

db.close()
