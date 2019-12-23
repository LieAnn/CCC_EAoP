'''
커뮤니티 게시글을 ETRI API를 이용하여 POS tagging과 의존구문분석한 결과를 저장하는 코드
Input : total_review.p
Output : new_ETRI_result_.p
'''

import urllib3
import json
import pickle
import ast

def ETRI_analyzer(text, analysisCode):
    openApiURL = "????????"
    accessKey = "????????"

    requestJson = {
        "access_key": accessKey,
        "argument": {
            "text": text,
            "analysis_code": analysisCode
        }
    }
    http = urllib3.PoolManager()
    response = http.request(
        "POST",
        openApiURL,
        headers={"Content-Type": "application/json; charset=UTF-8"},
        body=json.dumps(requestJson)
    )

    return response

file_directory = '../total_review.p'
f = open(file_directory,'rb')
data = pickle.load(f)
f.close()

ETRI_dict = dict()

for idx in range(0, 5000):
    ETRI_dict[idx] = []
    if idx % 100 == 0:
        print ("=============", idx)

    text = data[idx]
    new_text_list = text.split('\n')
    new_text_list = [sent.strip() for sent in new_text_list]
    while '' in new_text_list:
        new_text_list.remove('')
    new_text = '\n'.join(new_text_list)

    result = ETRI_analyzer(new_text, analysisCode= 'dparse')
    result = result.data.decode('utf-8')
    result = ast.literal_eval(result) # bytes를 dict로 바꾸어주는 역활
    try:
        core_result = result['return_object']
    except:
        print ("ERROR : ", idx)
        print (result['reason'])
        ETRI_dict[idx] = '##ERROR TEXT##'
    else:
        result_dict = json.loads(json.dumps(core_result))
        result_list = result_dict['sentence']
        for one_sentence_dict in result_list:
            a = dict()
            a['dependency'] = one_sentence_dict['dependency']
            a['morp'] = one_sentence_dict['morp']
            ETRI_dict[idx].append(a)

    if idx % 10 == 0: # To backup
        f = open("./input/new_ETRI_result_??.p","wb")
        pickle.dump(ETRI_dict, f)
        f.close()

f = open("./input/new_ETRI_result_??.p","rb")
data = pickle.load(f)
f.close()
