from selenium import webdriver
from selenium.webdriver.common.by import By
from ckip_transformers.nlp import CkipWordSegmenter, CkipPosTagger
from mongo import attraction_db
from model.google import Google
from model.Spider import Spider 
from model.Word import Word 
import pandas as pd
import json
import time
import csv
import re
import os

# 定義名稱與URL
name = "淡水老街"
url = "https://www.google.com/maps/place/%E6%B7%A1%E6%B0%B4%E8%80%81%E8%A1%97/data=!4m7!3m6!1s0x3442a55860ccfd91:0xa40c1b50cf3e21c5!8m2!3d25.168927!4d121.4440921!16s%2Fg%2F11bzs506yn!19sChIJkf3MYFilQjQRxSE-z1AbDKQ?authuser=0&hl=zh-TW&rclk=1"
getTime = '1 年前'
wrong = []

# =====================================================
# Google 爬蟲
# =====================================================
# 啟動爬蟲
driver = webdriver.Chrome()
driver.set_window_size(800,800)
driver.get(url)

try:
    time.sleep(2)    # 點擊留言區
    list_input = driver.find_element(By.CSS_SELECTOR,'.RWPxGd button:nth-child(2)')
    list_input.click()
    time.sleep(2)    # 點擊排序按鈕
    sort_btn = driver.find_element(By.CSS_SELECTOR,'.m6QErb.Pf6ghf .TrU0dc button')
    sort_btn.click()
    time.sleep(2)    # 點擊以最新排序
    action_menu = driver.find_element(By.CSS_SELECTOR, '.fontBodyLarge.yu5kgd > div:nth-child(2)')
    action_menu.click()

    try:
        time.sleep(1)  
        lastItem = ''
        while 7 == 7:
            print(lastItem)
            row_list = Spider(driver).getElement()
            if (row_list[len(row_list)-1]["name"] == lastItem ):
                driver.quit()
                break

            lastItem = row_list[len(row_list)-1]["name"]
            if row_list[len(row_list)-1]["setTime"][-2:] != getTime[-2:]:
                time.sleep(1)
                Spider(driver).getElement()
            else:
                driver.quit()
                break
    except:
        print('發生錯誤')
        wrong.append({"name":name,"url":url,"type":"spider"})
        driver.quit()
except:
    print('發生錯誤')
    wrong.append({"name":name,"url":url,"type":"spider"})
    driver.quit()

time.sleep(1)

with open('./data/csv/{}.csv'.format(name), 'w', newline='', encoding='utf-8') as output_file:
        dict_writer = csv.DictWriter(output_file, ['name','setTime', 'star', 'content'])
        dict_writer.writeheader()         # 寫入標題
        dict_writer.writerows(row_list)   # 寫入值
                              
with open("./data/json/{}.json".format(name), "w", encoding="utf8") as f:
    json.dump(row_list, f, indent=2, sort_keys=True, ensure_ascii=False)

# =====================================================
# Ckip 斷詞計算tag
# =====================================================

if os.path.exists('./data/csv/{}.csv'.format(name)):
    # Initialize drivers
    ws_driver = CkipWordSegmenter(model="bert-base")
    pos_driver = CkipPosTagger(model="bert-base")
    try:
        dataset = pd.read_csv('./data/csv/{}.csv'.format(name))
        dataset['content'].fillna('', inplace=True) 
        dataset['content'] = dataset['content'].apply(lambda x: re.sub('[^\w\s\(\)\*\+\?\.\|]', '', str(x)))
        text_clean = Word(ws_driver,pos_driver).text_clean(dataset['content'])
        data = Word(ws_driver,pos_driver).save(text_clean)
        tag_value = data['words'].tolist()
        data.to_csv('./data/tfidf_csv/{}.csv'.format(name), encoding="utf-8-sig",index=False)
    except:
        wrong.append({"name":name,"url":url,"type":"ckip"})
        print('發生錯誤')

try:
    place_detail_data = Google().get_place_info(name,url,tag_value)
    place_detail_data = json.loads(place_detail_data)
    try:
        existing_data = attraction_db.attractionInfo.find_one({
            "$or": [
                {"place_id": place_detail_data["place_id"]},
                {"id": place_detail_data["id"]}
            ]
        })
        if existing_data is None:
            attraction_db.attractionInfo.insert_one(place_detail_data)
            print(f"{place_detail_data['name']}：已新增")
    except Exception as e:
        print(f"錯誤訊息：{e}")
        wrong.append({"name":name,"url":url,"type":"can't insert spots data"})
except:
    wrong.append({"name":name,"url":url,"type":"can't google place detail"})

try:
    print(wrong)
    with open("./data/warn/googleWrong.json", "w", encoding="utf8") as f:json.dump(wrong, f, indenWt=2, sort_keys=True, ensure_ascii=False)
except:
    print('無輸出錯誤檔 warn')