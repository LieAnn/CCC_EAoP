# -*- coding: utf-8 -*-
'''
크롤링한 게임 단어를 Mecab 사용자 사전 형태로 저장하는 코드
Input : game word.csv
Output : game word를 Mecab 사용자 사전 형태로 저장한 txt 파일
'''
def checkTrait(c):
    return (int((ord(c) - 0xAC00) % 28) != 0)

def checkTrait_word(word):
    for c in word:
        if checkTrait(c):
            return True
    return False

file_directory = "./Data/game word.csv"

total_game_word_list = []
trait_list = []

f = open(file_directory, 'r')
data = f.read()
f.close()

for word in data.split('\n'):
    if word != '' and word != '단어':
        total_game_word_list.append(word)

for word in total_game_word_list:
    if checkTrait_word(word):
        trait_list.append('T')
    else:
        trait_list.append('F')

f = open("game word.txt", 'w', encoding='utf-8')
for i in range(len(total_game_word_list)):
    f.write(str(total_game_word_list[i])+',,,,NNP,*,'+str(trait_list[i])+','+str(total_game_word_list[i])+',*,*,*,*,*\n')
f.close()