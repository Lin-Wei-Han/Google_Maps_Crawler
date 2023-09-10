from sklearn.cluster import KMeans
from gensim.models import Word2Vec
import pandas as pd
import os

model = Word2Vec.load('model/word2vec_gensim.model')

tag_data = pd.read_csv('./data/topic_tag.csv')
tag_data = tag_data['tag'].values

word_vectors = [model.wv[word] for word in tag_data if word in model.wv]

num_clusters = 10  # 主題數量
kmeans = KMeans(n_clusters = num_clusters)
cluster_labels = kmeans.fit_predict(word_vectors)

word_clusters = {word: label for word, label in zip(tag_data, cluster_labels)}

output_dir = "Topic"

# 將每個主題的詞彙列表寫入文本檔
for cluster_id in range(num_clusters):
    cluster_words = [word for word, label in word_clusters.items() if label == cluster_id]
    output_filename = os.path.join(output_dir, f"topic_{cluster_id}.txt")
    with open(output_filename, "w", encoding="utf-8") as f:
        f.write("\n".join(cluster_words))
    print(f"主題 {cluster_id} 的詞彙列表已寫入 {output_filename}")