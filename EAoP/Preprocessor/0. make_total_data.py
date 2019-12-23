'''
크롤링한 커뮤니티 게시글을 하나의 파일로 합하는 코드
Input : 커뮤니티 게시글이 저장된 csv 파일
Output : total_review.txt, total_review.p
'''

import csv
import time
import pickle

start = time.time()
total_data_list = []

for idx in [2,3,4,7,8,9]:
    file_directory = "????????"

    data = open(file_directory, 'r', encoding="utf-8")
    reader = csv.DictReader(data)
    for row in reader:
        review = row['content']
        if review not in total_data_list:  # 중복된 리뷰가 있는 경우 삭제하기 위함
            total_data_list.append(review)
    data.close()

print (len(total_data_list))

f = open("total_review.txt", "w", encoding="utf-8")
for idx in range(len(total_data_list)):
    f.write('###' + str(idx+1) + '\n')
    f.write(total_data_list[idx])
    f.write('\n')
f.close()

f = open("total_review.p", "wb")
pickle.dump(total_data_list,f)
f.close()

print (time.time() - start)
