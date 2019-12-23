'''
final_main_test에서 사용하는 EAoP의 주요한 함수를 저장하는 코드
'''
import numpy as np
import itertools
from scipy import spatial
from scipy.stats import gmean, hmean

def make_matrix(mecab_data, word2emotion_dict, emotion2word_dict, n_windows, n_filter):
    '''data만들기'''
    ''' load mecab data'''

    total_mecab_word_set = set()
    for k in mecab_data.keys():
        if k != 0:
            text = mecab_data[k]
            for sentence in text:
                for word in sentence:
                    total_mecab_word_set.add(word)

    print ('# of total mecab word : ', len(total_mecab_word_set))

    ''' load emotion data'''
    total_emotion_word_set = set(word2emotion_dict.keys())
    print ('# of total emotion word : ', len(total_emotion_word_set))

    ''' Make dictionary '''
    total_word_set = total_mecab_word_set | total_emotion_word_set
    num = len(total_word_set)
    print('# of total word : ', num)

    idx = 0
    idx2vocab = dict()
    vocab2idx = dict()
    for word in total_word_set:
        idx2vocab[idx] = word
        vocab2idx[word] = idx
        idx += 1


    ''' Count mecab word'''
    check = 0
    co_occurrence_mat = np.zeros((num, num))
    for k in mecab_data.keys():
        text = mecab_data[k]
        for sentence in text:
            for center_idx in range(len(sentence)):
                center_word = sentence[center_idx]
                context_idx_list = list(range(center_idx - n_windows, center_idx + n_windows + 1))
                context_idx_list.remove(center_idx)
                for context_idx in context_idx_list:
                    if context_idx < 0 or context_idx >= len(sentence):
                        pass
                    else:
                        context_word = sentence[context_idx]

                        if len(center_word) >= n_filter and len(context_word) >= n_filter: # 일정 길이 이상의 단어만 추가해준다
                            co_occurrence_mat[vocab2idx[center_word], vocab2idx[context_word]] += 1
                            co_occurrence_mat[vocab2idx[context_word], vocab2idx[center_word]] += 1

    ''' Add emotion word'''
    max_num = np.amax(co_occurrence_mat)

    for emotion in emotion2word_dict.keys():
        emotion_word_list = emotion2word_dict[emotion]

        for word in emotion_word_list:
            co_occurrence_mat[ vocab2idx[word], vocab2idx[word]] += max_num
        for word1, word2 in list(itertools.combinations(emotion_word_list, 2)):
            co_occurrence_mat[ vocab2idx[word1], vocab2idx[word2]] += max_num
            co_occurrence_mat[ vocab2idx[word2], vocab2idx[word1]] += max_num

    ''' Synchronize between mecab & emotion word'''
    # Mecab으로 POS tagging 했을 때 품사와 함께 저장하지만, 감정단어 사전에서 가져온 감정기준단어는 품사가 없기때문에 이를 더해주는 코드
    for emotion_word in total_emotion_word_set: # 품사가 없는 감정기준단어
        for mecab_word in total_mecab_word_set: # 품사가 있는 감정기준단어
            if emotion_word == mecab_word.split('/..')[0]:
                co_occurrence_mat[ vocab2idx[mecab_word], :] += co_occurrence_mat[vocab2idx[emotion_word], :]
                co_occurrence_mat[ :, vocab2idx[mecab_word]] += co_occurrence_mat[:, vocab2idx[emotion_word]]
    return co_occurrence_mat, vocab2idx, idx2vocab

def add_dependency(matrix, vocab2idx, idx2vocab, ETRI_pos_dict,ETRI_phrase_dict ,ETRI_start_dict, ETRI_mod_dict, weight):
    count = 0
    total_word_set = set(idx2vocab.values())
    for text_idx in ETRI_phrase_dict.keys():
        text_pos = ETRI_pos_dict[text_idx]
        text_start = ETRI_start_dict[text_idx]
        text_mod = ETRI_mod_dict[text_idx]
        text_phrase = ETRI_phrase_dict[text_idx]

        for sent_idx in range(len(text_phrase)):
            sent_pos = text_pos[sent_idx]
            sent_start = text_start[sent_idx]
            sent_mod = text_mod[sent_idx]
            sent_phrase = text_phrase[sent_idx]

            for phrase_idx in range(len(sent_phrase)):
                if len(sent_mod[phrase_idx]) != 0:
                    qual_start_idx = sent_start[phrase_idx]
                    if phrase_idx == len(sent_phrase) - 1:
                        qual_end_idx = len(sent_phrase)
                    else:
                        qual_end_idx = sent_start[phrase_idx + 1]
                    if qual_start_idx != None and qual_end_idx != None:
                        modificand_list = sent_pos[qual_start_idx:qual_end_idx]
                        for mod_idx in sent_mod[phrase_idx]:
                            mod_start_idx = sent_start[mod_idx]
                            mod_end_idx = sent_start[mod_idx + 1]
                            if mod_start_idx != None and mod_end_idx != None:
                                qualifier_list = sent_pos[mod_start_idx:mod_end_idx]

                                for modificand_word in modificand_list:
                                    for qualifier_word in qualifier_list:
                                        if modificand_word in total_word_set and qualifier_word in total_word_set:
                                            matrix[vocab2idx[modificand_word], vocab2idx[qualifier_word]] += weight
                                            matrix[vocab2idx[qualifier_word], vocab2idx[modificand_word]] += weight
                                            count += 1
    return matrix

def reduce_matrix(matrix, remove_pos_list, vocab2idx, idx2vocab):
    new_vocab2idx = dict()
    new_idx2vocab = dict()

    remove_idx_list = []

    for idx in range(len(matrix)):
        word_withPOS = idx2vocab[idx]
        if '/..' in word_withPOS:
            try:
                word, pos = word_withPOS.split('/..')
            except:
                print (word_withPOS)
            else:
                if pos in remove_pos_list:
                    remove_idx_list.append(idx)

    new_vocab_list = []
    for idx in idx2vocab.keys():
        if idx not in remove_idx_list:
            new_vocab_list.append(idx2vocab[idx])
    for idx in range(len(new_vocab_list)):
        new_idx2vocab[idx] = new_vocab_list[idx]
        new_vocab2idx[new_vocab_list[idx]] = idx


    new_matrix = np.delete(matrix, remove_idx_list, axis=0)
    new_matrix = np.delete(new_matrix, remove_idx_list, axis=1)

    return new_matrix, new_vocab2idx, new_idx2vocab


def remove_small_occurrence(matrix, n_filter_occurrence):
    filter_matrix = matrix >= n_filter_occurrence
    filter_matrix = filter_matrix.astype(int)
    return np.multiply(matrix, filter_matrix)


def check_query_results(model, query_list):
    ret = dict()
    for query in query_list:
        try:
            result = model.most_similar(query, number=10)
        except:
            result = "###ERROR###"
        ret[query] = result
    for k in ret.keys():
        print(k)
        print(ret[k])
    return ret


def show_difference(model, total_word_dependency_dict, query_list):
    ''' 수식어가 피수식어의 most similar 순위에서 몇번째인지보여주는 함수  '''
    ''' add dependency 파트를 주석처리하고 해보면 차이를 알 수 있다. '''
    for query in query_list:
        print('=======', query, '=======')
        rank = 0
        qualifier_list = total_word_dependency_dict[query]
        total_similarity_list = model.most_similar(query, 25000)
        for w, s in total_similarity_list:
            if w in qualifier_list:
                print(w, rank, s)
                qualifier_list.remove(w)
            rank += 1
        print(qualifier_list)


def find_emotion_centroid(one_word_vectors, emotion2word_dict, vocab2idx):
    ret = dict()

    for emotion in emotion2word_dict.keys():
        emotion_word_list = emotion2word_dict[emotion]
        for emotion_word in emotion_word_list:
            try:
                ret[emotion]
            except:
                ret[emotion] = one_word_vectors[vocab2idx[emotion_word]]
            else:
                ret[emotion] += one_word_vectors[vocab2idx[emotion_word]]
    for emotion in emotion2word_dict.keys():
        ret[emotion] = ret[emotion] / len(emotion2word_dict[emotion])
    return ret


def transform_based_emotion(one_word_vectors, emotion_centriod_dict, vocab2idx, method='Euclid'):
    ret = []
    emotion_order = ['공포', '기쁨', '놀람', '분노', '슬픔', '혐오']
    for word in vocab2idx.keys():
        new_word_vector = []
        word_vector = one_word_vectors[vocab2idx[word]]
        for emotion in emotion_order:
            emotion_centriod_vector = emotion_centriod_dict[emotion]
            if method == 'Euclid':
                new_word_vector.append(spatial.distance.euclidean(word_vector, emotion_centriod_vector))
            elif method == 'Cosine':
                new_word_vector.append(
                    1 - spatial.distance.cosine(word_vector, emotion_centriod_vector))  # cosine similarity
        ret.append(new_word_vector)
    return np.array(ret), emotion_order


def transform_sentence2vector(matrix, data, vocab2idx, method='AM'):
    ret = dict()
    for k in data.keys():
        ret[k] = []
        text = data[k]
        for sentence in text:
            vector = []
            for word in sentence:
                try:
                    vector.append(matrix[vocab2idx[word]])
                except:
                    pass
            vector = np.array(vector)
            if method == 'AM':
                sentence_vector = np.mean(vector, axis=0)
            elif method == 'GM':
                sentence_vector = gmean(vector, axis=0)
            elif method == 'HM':
                sentence_vector = hmean(vector, axis=0)
            ret[k].append(sentence_vector)

    return ret


def transform_text2vector(data, method='AM'):
    ret = dict()
    for k in data.keys():
        vector = np.array(data[k])
        if method == 'AM':
            text_vector = np.mean(vector, axis=0)
        elif method == 'GM':
            text_vector = gmean(vector, axis=0)
        elif method == 'HM':
            text_vector = hmean(vector, axis=0)
        ret[k] = text_vector
    return ret
