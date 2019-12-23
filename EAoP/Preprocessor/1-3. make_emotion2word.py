'''
크롤링한 감정 기준 단어를 감정-단어, 단어-감정의 dictionary로 저장하는 코드
Input : emotion word.csv
Output : emotion2word_dict.p, word2emotion_dict.p
'''
import pickle
file_directory = "./Data/emotion word.csv"

f = open(file_directory)
data = f.read()
f.close()

emotion2word_dict = dict()
word2emotion_dict = dict()
for row in data.split('\n')[1:-1]:
    try:
        word, emotion = row.split(',')
    except:
        pass
    else:
        if emotion not in emotion2word_dict.keys():
            emotion2word_dict[emotion] = set()
        if word not in word2emotion_dict.keys():
            word2emotion_dict[word] = set()
        emotion2word_dict[emotion].add(word)
        word2emotion_dict[word].add(emotion)

''' 각 emotion 별 갯수 확인'''
print ("emotion2word_dict : ",emotion2word_dict)
print ("word2emotion_dict : ",word2emotion_dict)
print ("# of total emotion word : ", len(list(word2emotion_dict.keys())))
for emotion in emotion2word_dict.keys():
    print (emotion, len(emotion2word_dict[emotion]))

f = open("emotion2word_dict.p", 'wb')
pickle.dump(emotion2word_dict,f)
f.close()

f = open("word2emotion_dict.p", 'wb')
pickle.dump(word2emotion_dict, f)
f.close()
