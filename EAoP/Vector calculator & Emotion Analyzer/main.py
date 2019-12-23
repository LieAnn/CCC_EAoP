'''
Preprocessing한 결과를 Glove를 통해 vectorize한 후 Emotion calculate하는 코드
Input : new_mecab_POS_data.p, word2emotion_dict.p, emotion2word_dict.p
        ETRI_pos_result_dict.p, ETRI_dependency_phrase_dict.p, ETRI_start_dict.p, ETRI_dependency_mod_dict.p
Output : matrix_based_emotion pickle 파일, vocab2idx pickle 파일, idx2vocab pickle 파일, sentence_vector_dict_AM pickle 파일, text_vector_dict_AM pickle 파일
'''

from main_functions import *
from scipy import sparse
from glove import Glove
import pickle
import numpy as np
import time

'''variable'''
n_windows = 3
n_filter_length = 2  # 한 단어의 최소 길이
n_filter_occurrence = 3
n_dim_list = [30]
n_epoch_list = [1000]

start = time.time()
for n_dim in n_dim_list:
    for n_epoch in n_epoch_list:
        for replicate in [1,2,3,4,5]:
            print (n_dim, n_epoch, replicate)
            ''' Data load'''
            directory = './input/'
            f = open(directory+'new_mecab_POS_data.p','rb')
            mecab_data = pickle.load(f)
            f.close()

            f = open(directory+'word2emotion_dict.p', 'rb')
            word2emotion_dict = pickle.load(f)
            f.close()

            f = open(directory+'emotion2word_dict.p', 'rb')
            emotion2word_dict = pickle.load(f)
            f.close()

            f=open("./input/ETRI_pos_result_dict.p","rb")
            ETRI_pos_result_dict = pickle.load(f)
            f.close()

            f=open("./input/ETRI_dependency_phrase_dict.p","rb")
            ETRI_dependency_phrase_dict = pickle.load(f)
            f.close()

            f=open("./input/ETRI_start_dict.p","rb")
            ETRI_start_dict = pickle.load(f)
            f.close()

            f=open("./input/ETRI_dependency_mod_dict.p","rb")
            ETRI_dependency_mod_dict = pickle.load(f)
            f.close()

            ''' make co-occurrence matrix'''
            co_occurrence_mat, vocab2idx, idx2vocab = make_matrix(mecab_data, word2emotion_dict, emotion2word_dict,n_windows, n_filter_length)
            print ("mean : ", np.mean(co_occurrence_mat))
            print ("median : ", np.median(co_occurrence_mat))
            print ("co-occurrrence matrix complete")

            ''' Add dependency'''
            weight = np.mean(co_occurrence_mat)
            co_occurrence_mat = add_dependency(matrix=co_occurrence_mat, vocab2idx=vocab2idx, idx2vocab=idx2vocab, ETRI_pos_dict=ETRI_pos_result_dict, ETRI_phrase_dict=ETRI_dependency_phrase_dict ,ETRI_start_dict = ETRI_start_dict, ETRI_mod_dict=ETRI_dependency_mod_dict, weight= weight)
            print ('add dependency complete')

            ''' reduce co-occurrence matrix'''
            remove_pos_list = ['JKS', 'JKC', 'JKG', 'JKO', 'JKB', 'JKV', 'JKQ', 'JX', 'JC', 'EP', 'EF', 'EC', 'ETN', 'ETM', 'XPN', 'XSN', 'XSV', 'XSA','XR','SF','SE','SSO','SSC','SC','SY','SL','SH','SN','UNKNOWN','UNDETERMINED']
            co_occurrence_mat, vocab2idx, idx2vocab = reduce_matrix(co_occurrence_mat, remove_pos_list, vocab2idx, idx2vocab)
            print ("Remove unnecessary POS complete")

            ''' Train the glove '''
            co_occurrence_csrmat = sparse.csr_matrix(co_occurrence_mat)
            glove = Glove(no_components = n_dim)
            ret_dict = glove.fit(co_occurrence_csrmat.tocoo(), epochs=n_epoch, verbose=True)
            glove.add_dictionary(vocab2idx)
            print ("Training glove complete")
            
            for i in range(n_epoch):
                if i % 100 == 0 or i == n_epoch-1:
                    one_word_vectors = ret_dict[i]
                    '''  explore the glove '''
                    emotion_centroid_dict = find_emotion_centroid(one_word_vectors, emotion2word_dict, vocab2idx)
                    ''' convert word vector to 6 dim vector'''
                    matrix_based_emotion, emotion_order = transform_based_emotion(one_word_vectors, emotion_centroid_dict, vocab2idx, method = 'Cosine')

                    ''' calculate sentence to 6 dim vector'''
                    sentence_vector_dict = transform_sentence2vector(matrix_based_emotion, mecab_data, vocab2idx, method = 'AM'  )

                    ''' calculate text to 6 dim vector '''
                    text_vector_dict = transform_text2vector( sentence_vector_dict, method = 'AM')
                
                    ''' 각 epoch별각 감정별  단어,문장, 텍스트갯수'''
                    word_count_list = [0,0,0,0,0,0]
                    for idx in range(matrix_based_emotion.shape[0]):
                        word_count_list[np.argmax(matrix_based_emotion[idx])] += 1

                    sent_count_list = [0,0,0,0,0,0]
                    for idx in sorted(list(sentence_vector_dict.keys())):
                        one_text = sentence_vector_dict[idx]
                        for sent_idx in range(len(one_text)):
                            if type(one_text[sent_idx]) != str:
                                sent_count_list[np.argmax(one_text[sent_idx])] += 1

                    text_count_list = [0,0,0,0,0,0]
                    for idx in sorted(list(text_vector_dict.keys())):
                        one_text = text_vector_dict[idx]
                        if type(one_text) != str:
                            text_count_list[np.argmax(one_text)] += 1

                    print ("=====",i,"=====")
                    print (emotion_order)
                    print (word_count_list)
                    print (sent_count_list)
                    print (text_count_list)
                    
                    # 데이터 저장
                    f = open("./output/except_more_POS/with/1/matrix_based_emotion" + str(n_dim) + "_" + str(n_epoch) + "_" + str(replicate) + "_" + str(i) + ".p", "wb")
                    pickle.dump(matrix_based_emotion, f)
                    f.close()

                    f = open("./output/except_more_POS/with/1/vocab2idx" + str(n_dim) + "_" + str(n_epoch) + "_" + str(replicate) + "_" + str(i)+ ".p", "wb")
                    pickle.dump(vocab2idx, f)
                    f.close()

                    f = open("./output/except_more_POS/with/1/idx2vocab" + str(n_dim) + "_" + str(n_epoch) + "_" + str(replicate) + "_" + str(i)+ ".p", "wb")
                    pickle.dump(idx2vocab, f)
                    f.close()

                    f = open("./output/except_more_POS/with/1/sentence_vector_dict_AM" + str(n_dim) + "_" + str(n_epoch) + "_" + str(replicate) + "_" + str(i)+ ".p", "wb")
                    pickle.dump(sentence_vector_dict, f)
                    f.close()

                    f = open("./output/except_more_POS/with/1/text_vector_dict_AM" + str(n_dim) + "_" + str(n_epoch) + "_" + str(replicate) + "_" + str(i)+ ".p", "wb")
                    pickle.dump(text_vector_dict, f)
                    f.close()
                    
print (time.time()-start)
