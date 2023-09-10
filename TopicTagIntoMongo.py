from mongo import attraction_db
import os

topics_dict = {}
directory = './TopicFilter'

for file in os.listdir(directory):
    topic_name = os.path.splitext(file)[0]
    with open(f'./TopicFilter/{file}', "r", encoding="utf-8") as file:
        topics_dict[topic_name] = [line.strip() for line in file]

# 設定條件，主題必須匹配至少5個標籤才能存入文件的 "topic" 欄位
min_tags_required = 1
# 過濾出 "topic" 屬性的陣列長度小於等於3的文件
results = attraction_db.attractionInfo.find()
filtered_results = [result for result in results if len(result.get("topic", [])) <= 3]

# attraction_db.attractionInfo.find()
for document in filtered_results:
    tags = document.get("tag", [])

    matching_topics = {}
    
    # 遍歷主題字典，計算匹配度
    for topic, topic_tags in topics_dict.items():
        intersection = len(set(topic_tags) & set(tags))
        matching_topics[topic] = intersection

    # 過濾出匹配度超過5個標籤的主題
    filtered_topics = [topic for topic, intersection in matching_topics.items() if intersection >= min_tags_required]

    # 將匹配的主題列表按匹配度排序（降序）
    sorted_matching_topics = sorted(filtered_topics, key=lambda x: matching_topics[x], reverse=True)
    
    print(f'{document["name"]}:{sorted_matching_topics}')

    attraction_db.attractionInfo.update_one(
        {"name": document["name"]},
        {"$set": {"topic": sorted_matching_topics}}
    )