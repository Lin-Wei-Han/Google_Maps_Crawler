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

spotsList = pd.read_csv('./data/spot_list/spotsList_clean.csv') 
getTime = '1 年前'
wrong = []

for index, row in spotsList[900:1000].iterrows():
    print(row['name'])
    # =====================================================
    # Google 爬蟲
    # =====================================================
    time.sleep(2)
    driver = webdriver.Chrome()
    driver.set_window_size(800,800)
    driver.get(row['google_url'])

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
            wrong.append({"name":row['name'],"url":row['google_url'],"type":"spider"})
            driver.quit()
            continue
    except:
        print('發生錯誤')
        wrong.append({"name":row['name'],"url":row['google_url'],"type":"spider"})
        driver.quit()
        continue

    time.sleep(1)

    try:
        with open('./data/csv/{}.csv'.format(row['name']), 'w', newline='', encoding='utf-8-sig') as output_file:
            dict_writer = csv.DictWriter(output_file, ['name','setTime', 'star', 'content'])
            dict_writer.writeheader()         # 寫入標題
            dict_writer.writerows(row_list)   # 寫入值
        with open("./data/json/{}.json".format(row['name']), "w", encoding="utf8") as f:
            json.dump(row_list, f, indent=2, sort_keys=True, ensure_ascii=False)
    except:
        wrong.append({"name":row['name'],"url":row['google_url'],"type":"can't write csv"})
    # =====================================================
    # Ckip 斷詞計算tag
    # =====================================================
    if os.path.exists('./data/csv/{}.csv'.format(row['name'])):
    # Initialize drivers
        ws_driver = CkipWordSegmenter(model="bert-base")
        pos_driver = CkipPosTagger(model="bert-base")
        try:
            dataset = pd.read_csv('./data/csv/{}.csv'.format(row['name']))
            dataset['content'].fillna('', inplace=True) 
            dataset['content'] = dataset['content'].apply(lambda x: re.sub('[^\w\s\(\)\*\+\?\.\|]', '', str(x)))
            text_clean = Word(ws_driver,pos_driver).text_clean(dataset['content'])
            data = Word(ws_driver,pos_driver).save(text_clean)
            tag_value = data['words'].tolist()
            try: 
                data.to_csv('./data/tfidf_csv/{}.csv'.format(row['name']), encoding="utf-8-sig",index=False)
            except:
                wrong.append({"name":row['name'],"url":row['google_url'],"type":"can't write tfidf_csv"})
        except:
            wrong.append({"name":row['name'],"url":row['google_url'],"type":"ckip"})
            print('發生錯誤')
            continue

    # =====================================================
    # 取得詳細景點資訊
    # =====================================================
    try:
        place_detail_data = Google().get_place_info(row['name'],row['google_url'],tag_value)
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
                print(f"{index+2}：{place_detail_data['name']}：已新增")
        except Exception as e:
            print(f"錯誤訊息：{e}")
            wrong.append({"name":row['name'],"url":row['google_url'],"type":"can't insert spots data"})
            continue
    except Exception as e:
        print(f"錯誤訊息：{e}")
        wrong.append({"name":row['name'],"url":row['google_url'],"type":"can't google place detail"})
        continue
    


try:
    print(wrong)
    with open("./data/warn/googleWrong.json", "w", encoding="utf8") as f:
        json.dump(wrong, f, indent=2, sort_keys=True, ensure_ascii=False)
except Exception as e:
    print(f"錯誤訊息：{e}")
    print('無輸出錯誤檔 warn')