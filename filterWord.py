from gensim.models import Word2Vec
import os

# 載入已經訓練好的Word2Vec模型，或者您可以訓練自己的模型
model = Word2Vec.load("./output_model/word2vec_gensim.model")

directory = './TopicFinal'

for file_name in os.listdir(directory):
    with open(f"./TopicFinal/{file_name}", "r", encoding="utf-8") as file:
        lines = file.readlines()

    valid_words = []

    for line in lines:
        word = line.strip()
        if word in model.wv:
            valid_words.append(word)

    with open(f"./TopicFilter/{file_name}", "w", encoding="utf-8") as output_file:
        output_file.write("\n".join(valid_words))

    print(f"保留了{len(valid_words)}個有效詞彙。")