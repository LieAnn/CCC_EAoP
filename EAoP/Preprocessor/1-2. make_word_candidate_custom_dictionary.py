# -*- coding: utf-8 -*-
'''
soynlp WordExtractor를 이용하여 Word Candidate를 추출하는 코드
Input : total_review.p
Output : Word Candidate를 Mecab 사용자 사전 형태로 저장한 txt 파일
'''
from soynlp.word import WordExtractor
from pykospacing import spacing
import math
import MeCab
import time
import pickle

def split_with_enter_and_spacing(text):
    new_text_list = text.split('\n')
    new_text_list = [sent.strip() for sent in new_text_list]
    new_text_list = [spacing(sent) for sent in new_text_list]
    while '' in new_text_list:
        new_text_list.remove('')

    return new_text_list

def word_score(score):
    return (score.cohesion_forward * math.exp(score.right_branching_entropy))

def convert_mecab(mecab_result):
    out = mecab_result.split("\n")
    ret = []
    for one_review in out:
        a = one_review.split(",")
        needs = a[0]
        ret.append(tuple(needs.split("\t")))
    return ret

start = time.time()

f =  open("total_review.p","rb")
total_data_list = pickle.load(f)
f.close()

print (len(total_data_list))

word_extractor = WordExtractor(min_frequency = 100, min_cohesion_forward=0.05, min_right_branching_entropy=0.0)

word_extractor.train(total_data_list)
words = word_extractor.extract()
print ("# of word candidate : ", len(words))

word_candidate_with_score = sorted(words.items(), key=lambda x:word_score(x[1]), reverse=True)
mecab = MeCab.Tagger()
mecab_word_set = set()
for idx in range(len(total_data_list)):
    try:
        out = mecab.parse(total_data_list[idx])
    except:
        print ("Error in Mecab : " ,idx+1)
    else:
        mecab_result = convert_mecab(out)
        for one_word in mecab_result:
            mecab_word_set.add(one_word[0])

# 각 word candidate마다 각 클래스의 품사 태깅된 단어가 없는지 확인
mecab_add_word = []
for idx in range(len(word_candidate_with_score)):
    word_candidate = word_candidate_with_score[idx][0]

    if word_candidate not in mecab_word_set:
        mecab_add_word.append(word_candidate)

print ("# of mecab word candidate : ", len(mecab_add_word))

f = open('mecab word candidate spacing_100.txt', "w", encoding="utf-8")
for word in mecab_add_word:
    f.write(str(word) + ",,,,NNP,*,F,"+ str(word) + ",*,*,*,*,*" + "\n")
f.close()

print (time.time()- start)