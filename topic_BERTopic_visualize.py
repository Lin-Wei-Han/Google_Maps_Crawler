from bertopic import BERTopic
import pandas as pd

file_name = "topic_tag_20"
topics_count = 251

tag_data = pd.read_csv(f'./data/{file_name}.csv')
tag_data = tag_data['tag'].values

model = BERTopic.load('BERTopic')
# hierarchical_topics = model.hierarchical_topics(tag_data)


# 降維後視覺化
model.visualize_documents(tag_data).show()
model.visualize_topics().show()

# model.visualize_barchart(top_n_topics = topics_count).show()
# model.visualize_hierarchy(hierarchical_topics = hierarchical_topics).show()