from ckip_transformers.nlp import CkipWordSegmenter, CkipPosTagger
import pandas as pd
import re
import os

print("Initializing drivers...")
ws_driver = CkipWordSegmenter(model="albert-base")
pos_driver = CkipPosTagger(model="albert-base")
print("Initializing drivers... done")

def process_article(article):
    if not article:
        return ""
    # 斷詞
    ws = ws_driver([article])
    # 詞性標注
    pos = pos_driver(ws)

    # 只留下名詞和動詞，並去掉特定詞性、一個字詞
    short_sentence = []
    stop_pos = set([]) #不使用停用詞
    for sentence_ws, sentence_pos in zip(ws, pos):
        for word_ws, word_pos in zip(sentence_ws, sentence_pos):
            is_N_or_V = word_pos.startswith("V") or word_pos.startswith("N")
            is_not_stop_pos = word_pos not in stop_pos
            is_not_one_charactor = len(word_ws) > 1
            if is_N_or_V and is_not_stop_pos and is_not_one_charactor:
                short_sentence.append(word_ws)
    # 回傳斷詞後的結果
    return " ".join(short_sentence)

count = 0
directory = './data/csv/'

for file in os.listdir(directory)[2400:]:
    print(file)
    dataset = pd.read_csv('./data/csv/{}'.format(file))
    dataset["content"].fillna("", inplace=True)
    content = dataset["content"].apply(lambda x: re.sub("[^\w\s\(\)\*\+\?\.\|]", "", str(x)))
    seg_result = content.apply(process_article)

    seg_result.to_csv('./data/seg_result/{}'.format(file), index=False)

    print(f"{count}:{file}已輸出")
    count = count + 1