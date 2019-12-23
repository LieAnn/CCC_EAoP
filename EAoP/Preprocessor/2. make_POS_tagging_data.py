'''
커뮤니티 게시글을 Meacb을 이용하여 POS tagging한 결과를 저장하는 코드. 단어와 POS tagging 결과를 tuple 형태로 저장한다.
Input : total_review.p
Output : new_mecab_POS_data.p, new_mecab_POS_data.txt
'''

import MeCab
import pickle

def convert_mecab(mecab_result):
    out = mecab_result.split("\n")
    ret = []
    for one_review in out:
        a = one_review.split(",")
        needs = a[0]  # ex) '오색\tNNG' or '한\tXSA+ETM'
        try:
            word, pos = needs.split('\t')
        except:
            pass
        else:
            if '+' in pos:
                other_needs = a[-1]
                for word_pos in other_needs.split('+'):
                    b = word_pos.split('/')
                    ret.append( (b[0], b[1]))
            else:
                ret.append( (word, pos))
    return ret

mecab = MeCab.Tagger()

file_directory = '../total_review.p'

f = open(file_directory,'rb')
total_data_list = pickle.load(f)
f.close()

total_word_list = []
new_total_data_dict = dict()

for idx in range(1, len(total_data_list)):
    if idx % 100 == 0 :
        print (idx)

    new_text= []

    text = total_data_list[idx]
    new_text_list = text.split('\n')
    new_text_list = [sent.strip() for sent in new_text_list]
    while '' in new_text_list:
        new_text_list.remove('')

    result = [mecab.parse(new_text) for new_text in new_text_list]

    mecab_result = [convert_mecab(a) for a in result]

    for one_sent_list in mecab_result:
        new_one_sent_list = []
        for one_tuple in one_sent_list:
            try:
                one_tuple[1]
            except:
                one_tuple = (one_tuple[0], 'UNDETERMINED')
            new_word = one_tuple[0] + '/..' + one_tuple[1]
            total_word_list.append(new_word)
            new_one_sent_list.append(new_word)
        if len(new_one_sent_list) > 0:
            new_text.append(new_one_sent_list)
    new_total_data_dict[idx] = new_text

f = open('./input/new_mecab_POS_data.p', 'wb')
pickle.dump(new_total_data_dict, f)
f.close()

f = open('./input/new_mecab_POS_data.txt','w', encoding='utf-8')
for idx in sorted(new_total_data_dict.keys()):
    f.write('###' + str(idx) + '\n')
    small_list = new_total_data_dict[idx]
    for one_sent in small_list:
        f.write(str(one_sent))
        f.write('\n')
f.close()