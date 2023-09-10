from bertopic import BERTopic
import pandas as pd
import os

file_name = "topic_tag_20"
output_dir = "TopicFinal" 

tag_data = pd.read_csv(f'./data/{file_name}.csv')
tag_data = tag_data['tag'].values

# 初始化BERTopic模型
# topic_model = BERTopic(nr_topics=30,language="multilingual")
topic_model = BERTopic(language="multilingual",top_n_words=5000)

# 主題建模
# topics, probs = topic_model.fit_transform(tag_data)
topics, probs = topic_model.fit_transform(tag_data)

# 主題的關鍵詞和標籤分配
topic_keywords = topic_model.get_topic_info()
# 將每個主題的代表性文檔寫入文本檔
for topic_id , name, representative in topic_keywords[['Topic','Name', 'Representation']].values:
    docs_str = "\n".join(representative)
    output_filename = os.path.join(output_dir, f"topic_{name}.txt")
    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(docs_str)
    print(f"主題 {topic_id} 的代表性文檔已寫入 {output_filename}")

topic_model.save('BERTopic')
