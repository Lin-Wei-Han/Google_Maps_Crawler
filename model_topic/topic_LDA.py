from gensim import corpora
from gensim.models import LdaModel
import pandas as pd
import os

# model = Word2Vec.load('model/word2vec_gensim.model')

tag_data = pd.read_csv('./data/topic_tag.csv')
tag_data = tag_data['tag'].values

dictionary = corpora.Dictionary([tag_data])
corpus = [dictionary.doc2bow(tag_data)]

# LDA 主題模型
num_topics = 10  # 主題數量
lda_model = LdaModel(corpus, num_topics=num_topics, id2word=dictionary)


output_dir = "Topic"

# 將每個主題的詞彙列表寫入文本檔
for topic_id in range(num_topics):
    topic_words = lda_model.show_topic(topic_id, topn=10)
    topic_words_list = [word for word, _ in topic_words]
    output_filename = os.path.join(output_dir, f"topic_{topic_id}.txt")
    with open(output_filename, "w", encoding="utf-8") as f:
        f.write("\n".join(topic_words_list))
    print(f"主題 {topic_id} 的詞彙列表已寫入 {output_filename}")