from gensim.models import Word2Vec
import pandas as pd
import os

word_list = []
directory = './data/seg_result'

for file in os.listdir(directory):
    article = []
    dataset = pd.read_csv('./data/seg_result/{}'.format(file))
    dataset["content"].fillna("", inplace=True)
    for word in dataset["content"]:
        if word == "": continue
        for ws in word.split(' '):
            if ws != "":
                article.append(ws)
    word_list.append(article)

print(len(word_list))

model = Word2Vec(word_list, window=10, min_count=10, workers=6)
vocab = model.wv.index_to_key
vectors = model.wv[vocab]
print(vectors)

model.save('model/word2vec_gensim.model')

#======================================

model = Word2Vec.load('model/word2vec_gensim.model')

input_word = ['七星潭','自然']

similar_words = model.wv.most_similar(input_word, topn=200)
similar_words, scores = zip(*similar_words)

similar_vectors=[]
for x in similar_words:
   similar_vectors.append(x)

print(list(similar_words))