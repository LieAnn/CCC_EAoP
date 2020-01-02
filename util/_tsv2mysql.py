import pymysql
import pandas as pd
import sys
from sqlalchemy import create_engine
from pandas.io import sql

# iris 데이터
df = pd.read_csv('user_vector.tsv', sep='\t', encoding = "utf8")
# df = df.drop(["idx"], axis=1)


engine = create_engine("mysql+pymysql://{user}:{pw}@localhost/{db}"
                       .format(user="root",
                               pw="mysql",
                               db="ccc",
                               charset='utf8',
                               encoding='utf-8'))
conn = engine.connect()
df.to_sql(con=engine, name='users', if_exists='append')
conn.close()