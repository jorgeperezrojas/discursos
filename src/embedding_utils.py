import os
import re
from gensim.models.keyedvectors import KeyedVectors
import numpy as np
import text_processing as tp
from scipy.spatial.distance import cosine
from sklearn.decomposition import PCA
from collections import Counter
import re
import time
import sys

def get_metadata(presidente, data_directory = '../data'):
    presidente_directory = os.path.join(data_directory, presidente)
    processed_directory = os.path.join(presidente_directory, 'processed_text/')
    # get meta data 
    original_meta = {}
    with open(os.path.join(processed_directory,'meta.txt')) as in_meta_file:
        for line in in_meta_file:
            line = line[:-1] # drop the \n
            data = line.split('\t')
            
            name = data[0]
            date = data[1]
            title = data[2]
            subtitle = data[3]
            img = data[4]

            original_meta[name] = {}
            original_meta[name]['name'] = name
            original_meta[name]['date'] = date
            original_meta[name]['title'] = title
            original_meta[name]['subtitle'] = subtitle
            original_meta[name]['img'] = img
    return original_meta

def get_sentences(
        presidente,
        data_directory = '../data',
        min_len = 30,
        ):
    presidente_directory = os.path.join(data_directory, presidente)
    processed_directory = os.path.join(presidente_directory, 'processed_text/')
    clean_d_directory = os.path.join(processed_directory,'discursos_limpios')

    # get filenames in alphabetichal order
    filenames = []
    for filename in os.listdir(clean_d_directory):
        filenames.append(filename)
    filenames.sort()

    n_tokens = 0
    sentences = []
    
    re_to_split = '([\.\?!:])b?r?[\n ]+|\n'
    re_to_ignore = '[\.\?!:\n]' 
    
    # get sentences and their respective discourse names
    for filename in filenames:
        # get sentences from every file
        with open(os.path.join(clean_d_directory,filename)) as infile:
            raw_data = infile.read()
        raw_sentences = re.split(re_to_split,raw_data)
        sentences_in_discourse = []
        for i,raw_sentence in enumerate(raw_sentences):
            if raw_sentence == None or re.match(re_to_ignore, raw_sentence):
                continue
            ####
            assert raw_sentence != None and '\n' not in raw_sentence
            ####
            if i < (len(raw_sentences) - 1) and raw_sentences[i+1] != None:
                to_append = (raw_sentence + raw_sentences[i+1])
            else:
                to_append = raw_sentence
            to_append = to_append.strip()
            if len(to_append) < min_len or to_append in sentences_in_discourse:
                continue
            sentences_in_discourse.append(to_append)
            discourse_name = filename[:-4]
            sentences.append((to_append, discourse_name))
    return sentences


def load_word_vectors(wordvectors_file_vec='/Users/jperez/research/nlp/word-embeddings/spanish-word-embeddings/examples/fasttext-sbwc.3.6.e20.vec', cantidad=100000):
    print('Loading',cantidad,'vectors from',wordvectors_file_vec)
    wordvectors = KeyedVectors.load_word2vec_format(wordvectors_file_vec, limit=cantidad)
    return wordvectors


def avg_word_vector(words, 
                    word_vectors, 
                    normalize = False, 
                    frequencies = None, 
                    total_count = 0, 
                    n_parameter = 0.001,
                    leave_out = [],
                    leave_out_re = None,
                    ):
    
    if normalize and (frequencies == None or total_count == 0):
        raise Exception('Parameter frequencies and total_count should be defined when normalizing vectors.')
        
    size = word_vectors.vector_size
    avg_vec = np.zeros((size,), dtype="float32")
    n_words = 0
    
    for word in words:

        if leave_out_re == None:
            match_leave_out_re = False
        else:
            match_leave_out_re = re.match(leave_out_re,word)

        if word in word_vectors and word not in leave_out and not match_leave_out_re: # continue only if word is vocabulary, it is not in leave_out and it does not match the leave_out_re expresion (otherwise just  skip this word)
            n_words += 1
            
            if normalize:
                word_prob = frequencies[word] / total_count
                to_add = (n_parameter / (n_parameter + word_prob)) * word_vectors[word]
            else:
                to_add = word_vectors[word]
                
            avg_vec += to_add

    if n_words > 0:
        avg_vec = (1 / n_words) * avg_vec
    else: # if there is no info in the sentences just output a random vector
        avg_vec = np.random.rand(size)

    # TODO: do we need to normalize the vector before outputting it?
    return avg_vec


class SentencesVectors:
    _word_frequencies = Counter()
    _word_count = 0
    _frequencies_loaded = False
    
    @classmethod
    def _load_frequencies(cls,freq_file):
        print('Loading frequencies from',freq_file)
        with open(freq_file) as in_freq_file:
            for line in in_freq_file:
                data = line[:-1].split('\t')
                word = data[0]
                count = int(data[1])
                # update class variables
                cls._word_count += count
                cls._word_frequencies[word] = count
        cls._frequencies_loaded = True               
    
    def __init__(self, 
                 sentences, 
                 word_vectors, 
                 freq_file='../data/general/sbwc.freq', 
                 normalize = True, 
                 pc_rej = True,
                 leave_out  =  None,
                 consider_numbers = False,
                 ):
        
        self.sentences = sentences
        self.word_vectors = word_vectors
        self.sentences_vectors = []
        self._pc = None
        self._normalize = normalize
        self._pc_rej = pc_rej
        self.leave_out = leave_out
        if consider_numbers == False:
            self.leave_out_re = '[0-9]+'
        else:
            self.leave_out_re = None
        
        if self._normalize:
            if not self._frequencies_loaded:
                self._load_frequencies(freq_file)
                self._frequencies_loaded = True
        
        # set base sentence vectors
        self.sentences_vectors = [
            self._get_base_vector(sentence)
            for (sentence, _) in self.sentences
        ]
        
        # set PC rejected vectors
        if pc_rej:
            pca = PCA(n_components=1).fit(self.sentences_vectors)
            self._pc = pca.components_[0]
            self.sentences_vectors = [
                self._get_rej_pc_vector(base_vector)
                for base_vector in self.sentences_vectors
            ]
            
        # create a numpy array
        self.sentences_vectors_array = np.array(self.sentences_vectors)

        # compute the norm (and reciprocal) of all vectors for later use
        self.sentences_vectors_norm = np.linalg.norm(self.sentences_vectors_array, axis=1) 
        self.sentences_vectors_rec_norm = np.reciprocal(self.sentences_vectors_norm)                
            

    def _get_base_vector(self, sentence):
        if type(sentence) == str:
            words = re.split(tp.re_chars_for_splitting, sentence.strip().lower())
        else:
            words = sentence
        avg_vector = avg_word_vector(words, self.word_vectors, self._normalize, 
                                     frequencies = self._word_frequencies,
                                     total_count = self._word_count,
                                     leave_out = self.leave_out,
                                     leave_out_re = self.leave_out_re,
                                    )
        return avg_vector
    
    def _get_rej_pc_vector(self, vector):
        proj = (np.dot(vector, self._pc) * self._pc)
        rej = vector - proj
        return rej
    
    def get_sentence_vector(self, sentence):
        base_vector = self._get_base_vector(sentence)
        if self._pc_rej:
            vector = self._get_rej_pc_vector(base_vector)
        else:
            vector = base_vector
        return vector
            
    def most_similar(self, sentence, n=100, dist='cosine'):

        if dist != 'cosine':
            raise ValueError('Only cosine is currently allowed.')
                
        
        to_compare = self.get_sentence_vector(sentence)
        punto = self.sentences_vectors_array @ to_compare
        norm_to_compare = np.linalg.norm(to_compare)
        cos_sim = punto * self.sentences_vectors_rec_norm * 1/norm_to_compare

        cos_dist = 1 - cos_sim
        ranking = np.argsort(cos_dist)[:n]
        out_distances = cos_dist[ranking]  
        out_sentences = [self.sentences[i] for i in ranking]

        return out_sentences, ranking, out_distances

    def all_internal_dists(self, nn=100, dist='cosine'):
        return self.all_dists(self.sentences_vectors, nn=nn, dist=dist)

    def all_dists(self, sentences_vectors, nn=100, dist='cosine'):
        if dist != 'cosine':
            raise ValueError('Only cosine is currently allowed.')

        most_similar = []
        most_similar_distances = []
        
        tiempo_inicio = time.clock()
        tiempo_estimado = 0
        
        for i,to_compare in enumerate(sentences_vectors):       
            punto = self.sentences_vectors_array @ to_compare
            norm_to_compare = np.linalg.norm(to_compare)
            cos_sim = punto * self.sentences_vectors_rec_norm * 1/norm_to_compare
            cos_dist = 1 - cos_sim
            ranking = np.argsort(cos_dist)[:nn]
            values = cos_dist[ranking]

            most_similar.append(ranking)
            most_similar_distances.append(values)
            sys.stdout.write('\rCalculando distancias ' 
                             + str(i) + '/' + str(len(sentences_vectors)) 
                             + ' tiempo restante: ' + str(tiempo_estimado) + 'min'
                            )
            
            if (i+1) % 100 == 0:
                tiempo_actual = time.clock()
                delta_tiempo = tiempo_actual - tiempo_inicio
                tiempo_promedio = delta_tiempo / i
                restantes = len(sentences_vectors) - i
                tiempo_estimado = int(restantes * tiempo_promedio/ 60)
            
        return most_similar, most_similar_distances
