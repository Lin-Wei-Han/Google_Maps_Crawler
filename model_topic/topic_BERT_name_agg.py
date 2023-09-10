from transformers import AutoTokenizer, AutoModel
from sklearn.cluster import AgglomerativeClustering
import pandas as pd
import numpy as np
import torch
import os

data = pd.read_csv('./data/topic_name.csv')
data = data['name'].values

# 使用 BERT 預訓練模型進行詞向量獲取
# model_name = "bert-base-uncased"  # 使用 BERT Base 模型
model_name = "bert-large-uncased"  # 使用 BERT large 模型
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name)

# 將詞彙轉換為詞向量
word_vectors = []
for word in data:
    inputs = tokenizer(word, return_tensors="pt")
    with torch.no_grad():
        outputs = model(**inputs)
        word_vector = outputs.last_hidden_state.mean(dim=1).numpy()
        word_vectors.append(word_vector)
word_vectors = np.concatenate(word_vectors, axis=0)

num_clusters = 30  # 主題數量
# 使用層次聚類
agg_clustering = AgglomerativeClustering(n_clusters=num_clusters)
cluster_labels = agg_clustering.fit_predict(word_vectors)

word_clusters = {word: label for word, label in zip(data, cluster_labels)}

output_dir = "Topicname"

# 將每個主題的詞彙列表寫入文本檔
for cluster_id in range(num_clusters):
    cluster_words = [word for word, label in word_clusters.items() if label == cluster_id]
    output_filename = os.path.join(output_dir, f"topic_{cluster_id}.txt")
    with open(output_filename, "w", encoding="utf-8") as f:
        f.write("\n".join(cluster_words))
    print(f"主題 {cluster_id} 的詞彙列表已寫入 {output_filename}")