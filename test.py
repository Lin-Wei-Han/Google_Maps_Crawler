from gensim.models import Word2Vec
from mongo import attraction_db
import pandas as pd
import os


directory = './TopicFilter'

for file in os.listdir(directory):
    data = {}
    topic_name = os.path.splitext(file)[0]
    with open(f'./TopicFilter/{file}', "r", encoding="utf-8") as file:
        data['topic'] = topic_name
        data['topic_tag'] = [line.strip() for line in file]
        data['type'] = "景點"
        attraction_db.spotsTopic.insert_one(data)


""" 
merged_name = []
merged_tags = []

cursor = attraction_db.attractionInfo.find({}, {"tag": 1})  # 檢索所有文件的'tag'欄位

for document in cursor:
    if "tag" in document:
        tags = document["tag"][:20]  # 取前十個tag
        merged_tags.extend(tags)  # 將tags合併到merged_tags陣列中

# unique_tags = list(set(merged_tags))
# data = {"tag": unique_tags}

data = {"tag": merged_tags}
df = pd.DataFrame(data)

df.to_csv('topic_tag_all.csv',encoding="utf-8-sig",index=False)
print(df)

"""

""" 
cursor = attraction_db.attractionInfo.find({}, {"name": 1})  # 檢索所有文件的'tag'欄位

for document in cursor:
    if "name" in document:
        name = document["name"]
        merged_name.append(name)


data = {"name": merged_name}
df = pd.DataFrame(data)

df.to_csv('topic_name.csv',encoding="utf-8-sig",index=False)
print(df) 
"""