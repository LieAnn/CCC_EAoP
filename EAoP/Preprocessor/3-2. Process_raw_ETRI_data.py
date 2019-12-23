'''
ETRI API를 적용한 raw 결과를 processing하는 코드.
Input : total_new_ETRI_result.p
Output : ETRI_pos_result_dict.p, ETRI_dependency_phrase_dict.p, ETRI_start_dict.p, ETRI_dependency_mod_dict.p
'''

import pickle
import re

BASE_CODE, CHOSUNG, JUNGSUNG = 44032, 588, 28

CHOSUNG_LIST = ['ㄱ', 'ㄲ', 'ㄴ', 'ㄷ', 'ㄸ', 'ㄹ', 'ㅁ', 'ㅂ', 'ㅃ', 'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅉ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ']
JUNGSUNG_LIST = ['ㅏ', 'ㅐ', 'ㅑ', 'ㅒ', 'ㅓ', 'ㅔ', 'ㅕ', 'ㅖ', 'ㅗ', 'ㅘ', 'ㅙ', 'ㅚ', 'ㅛ', 'ㅜ', 'ㅝ', 'ㅞ', 'ㅟ', 'ㅠ', 'ㅡ', 'ㅢ', 'ㅣ']
JONGSUNG_LIST = [' ', 'ㄱ', 'ㄲ', 'ㄳ', 'ㄴ', 'ㄵ', 'ㄶ', 'ㄷ', 'ㄹ', 'ㄺ', 'ㄻ', 'ㄼ', 'ㄽ', 'ㄾ', 'ㄿ', 'ㅀ', 'ㅁ', 'ㅂ', 'ㅄ', 'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ']

def convert(test_keyword):
    split_keyword_list = list(test_keyword)

    result = list()
    for keyword in split_keyword_list:
        if re.match('.*[ㄱ-ㅎㅏ-ㅣ가-힣]+.*', keyword) is not None:
            char_code = ord(keyword) - BASE_CODE
            char1 = int(char_code / CHOSUNG)
            result.append(CHOSUNG_LIST[char1])
            char2 = int((char_code - (CHOSUNG * char1)) / JUNGSUNG)
            result.append(JUNGSUNG_LIST[char2])
            char3 = int((char_code - (CHOSUNG * char1) - (JUNGSUNG * char2)))
            if char3==0:
                result.append('#')
            else:
                result.append(JONGSUNG_LIST[char3])
        else:
            result.append(keyword)
    return "".join(result)

path = './input/new_ETRI_result_??'

total_result_dict = dict()
for i in [0,1,2,3,4,5,6,7]:
    f = open(path + str(i) + ".p", "rb")
    data = pickle.load(f)
    f.close()
    total_result_dict.update(data)

remove_pos_list = ['SF', 'SP', 'SS', "SE", "SO", "SH", 'SW','NF','NV','NA','SN']

# 전체 데이터를 합치고 저장하는 코드
f = open("./input/total_new_ETRI_result.p", 'wb')
pickle.dump(total_result_dict, f)
f.close()

ETRI_pos_result_dict = dict()
ETRI_position_dict = dict()
for text_idx in total_result_dict.keys():
    if text_idx != 0:
        ETRI_pos_result_dict[text_idx] = []
        ETRI_position_dict[text_idx] = []

        one_text = total_result_dict[text_idx]
        if one_text == '##ERROR TEXT##':
            pass
        else:
            for sentence_idx in range(len(one_text)):
                sentence_result = []
                position_result = []

                one_sentence = one_text[sentence_idx]
                one_sentence_morp = one_sentence['morp']
                for word_idx in range(len(one_sentence_morp)):
                    one_word = one_sentence_morp[word_idx]
                    word_withPOS = one_word['lemma']+ '/..' + one_word["type"]
                    sentence_result.append(word_withPOS)
                    position_result.append( one_word['position'] )
                ETRI_pos_result_dict[text_idx].append(sentence_result)
                ETRI_position_dict[text_idx].append(position_result)

ETRI_dependency_phrase_dict = dict()
ETRI_dependency_mod_dict = dict()
for text_idx in total_result_dict.keys():
    if text_idx != 0:
        ETRI_dependency_phrase_dict[text_idx] = []
        ETRI_dependency_mod_dict[text_idx] = []

        one_text = total_result_dict[text_idx]
        if one_text == '##ERROR TEXT##':
            pass
        else:
            for sentence_idx in range(len(one_text)):
                phrase_list = []
                mod_list = []

                one_sentence = one_text[sentence_idx]
                one_sentence_dependency= one_sentence['dependency']
                for word_idx in range(len(one_sentence_dependency)):
                    one_word = one_sentence_dependency[word_idx]
                    phrase_list.append( one_word['text'] )
                    mod_list.append( list(map(lambda x: int(x), one_word['mod'])) )
                ETRI_dependency_phrase_dict[text_idx].append(phrase_list)
                ETRI_dependency_mod_dict[text_idx].append(mod_list)

ETRI_start_dict = dict()
count = 0
for text_idx in ETRI_pos_result_dict.keys():
    if text_idx != 0:
        ETRI_start_dict[text_idx] = []

        one_text_pos = ETRI_pos_result_dict[text_idx] # list of list
        one_text_dependency_phrase = ETRI_dependency_phrase_dict[text_idx] # list of list
        for sent_idx in range(len(one_text_dependency_phrase)):
            one_sent_pos = one_text_pos[sent_idx] # list of str
            one_sent_dependency_phrase = one_text_dependency_phrase[sent_idx] # list of str

            sent_start_list = [None] * len(one_sent_dependency_phrase)
            for word_dependency_idx in range(len(one_sent_dependency_phrase)):
                dependency_phrase = one_sent_dependency_phrase[word_dependency_idx]
                for word_pos_idx in range(len(one_sent_pos)):
                    pos_token = one_sent_pos[word_pos_idx].split("/..")[0]
                    if dependency_phrase[:len(pos_token)] == pos_token and word_pos_idx not in sent_start_list:
                        sent_start_list[word_dependency_idx] = word_pos_idx
                        break

            #sent_start_list에 None이 있는 걸 보정
            for idx in range(len(sent_start_list)):
                if sent_start_list[idx] == None:
                    if idx == 0:
                        sent_start_list[idx] = 0
                    else:
                        try:
                            start_idx = sent_start_list[idx - 1]+1
                        except:
                            pass
                        else:
                            final_idx = len(one_sent_pos)
                            for between_idx in range( start_idx,final_idx ):
                                if one_sent_pos[between_idx][0] == one_sent_dependency_phrase[idx][0] and between_idx not in sent_start_list:   # 첫 글자가 같은 경우 추가 or 첫 글자의 종성이 같은 경우 추가
                                    sent_start_list[idx] = between_idx
                                    break
            if None in sent_start_list:
                count += 1
            ETRI_start_dict[text_idx].append(sent_start_list)

f=open("./input/ETRI_pos_result_dict.p","wb")
pickle.dump(ETRI_pos_result_dict, f)
f.close()

f=open("./input/ETRI_dependency_phrase_dict.p","wb")
pickle.dump(ETRI_dependency_phrase_dict, f)
f.close()

f=open("./input/ETRI_start_dict.p","wb")
pickle.dump(ETRI_start_dict, f)
f.close()
f=open("./input/ETRI_dependency_mod_dict.p","wb")
pickle.dump(ETRI_dependency_mod_dict, f)
f.close()