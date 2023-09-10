from selenium import webdriver
from selenium.webdriver.common.by import By
from mongo import attraction_db
from bs4 import BeautifulSoup
import time
import re

def sort_by_weekday(operating_hours):
    days_order = ['星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日']
    sorted_hours = sorted(operating_hours, key=lambda x: days_order.index(x['week']))
    return sorted_hours

def scrollPage(driver,times):   # 滾動頁面
    counter = 0
    while counter <= times:
        pane = driver.find_element("xpath",'//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[3]')
        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", pane)
        time.sleep(1)
        counter += 1

def get_place_more_info(driver):
    try:
        data={}
        page_content = driver.page_source
        soup = BeautifulSoup(page_content, 'html.parser')
        open_time_week = []
        try:data["subtitle"] = soup.select('.DkEaL')[0].text
        except:data["subtitle"] = ""
        try:data["info"] = soup.select('.PYvSYb')[0].text
        except:data["info"] = ""
        try:data["site"] = soup.select('a.CsEnBe')[0].get('href')
        except:data["site"] = ""
        try:
            open_time = soup.select('.y0skZc')
            for time_up in open_time:
                week = time_up.select('td div')[0].text
                clock = time_up.select('td.mxowUb .G8aQO')[0].text
                result={}
                result['week'] = week
                result['clock'] = clock
                open_time_week.append(result)
            data["open_time"] = sort_by_weekday(open_time_week)
        except:
            open_time = []
            data["open_time"] = open_time
        try:
            time.sleep(1)
            library = driver.find_element(By.CSS_SELECTOR,'.aoRNLd.kn2E5e.NMjTrf.lvtCsd')
            library.click()
            time.sleep(1)
            scrollPage(driver,1)
            time.sleep(0.5)
            data["photo"] = get_photo_library(driver)
        except:
            data["photo"] = []
    except:
        data["subtitle"] = ""
        data["info"] = ""
        data["site"] = ""
        data["open_time"] = []
        data["photo"] = []
    return data

def get_photo(style):
    url_match = re.search(r'url\((.+)\);', style)
    if url_match:
        extracted_url = url_match.group(1)
        return extracted_url
    
def multiply_wh_parameters(original_url, factor):
    def modify_size(match):
        return f"{match.group(1)}{int(match.group(2)) * factor}"
    
    url_parts = original_url.split('=')

    if len(url_parts) > 1:
        modified_params = re.sub(r'([wh])(\d+)', modify_size, url_parts[1])
        modified_url = url_parts[0] + '=' + modified_params
    else:
        modified_url = original_url
    
    return modified_url

def get_photo_library(driver):
    page_content = driver.page_source
    soup = BeautifulSoup(page_content, 'html.parser')
    style_element = soup.find_all('div', class_='U39Pmb')

    photo_library = []

    for element in style_element:
        style_attribute = element['style']
        url = get_photo(style_attribute)
        url_pattern = re.compile(r'https?://(?:www\.)?[\w\.-]+(?:\.[a-zA-Z]{2,6})+[\w\.-]*[\?#]?[\w\.-=&]*')
        url = url.replace('"',"")
        if re.match(url_pattern, url):
            photo_library.append(multiply_wh_parameters(url,10))

    return photo_library

worng = []

# data_list = attraction_db.attractionInfo.find()
data_list = attraction_db.attractionInfo.find({"site": {"$exists": False}})

# 遍歷每筆資料並更新
for data in data_list:
    driver = webdriver.Chrome()
    driver.set_window_size(800,800)
    driver.get(data['google_url'])
    time.sleep(2)
    # 根據 name 和 google_url 抓取新資料
    try:
        result = get_place_more_info(driver)

        # 更新資料庫紀錄
        attraction_db.attractionInfo.update_one(
            {'id': data['id']},
            {'$set': {
                'subtitle': result['subtitle'],
                'info': result['info'],
                'site': result['site'],
                'open_time': result['open_time'],
                'photo': result['photo']
            }}
        ) 
        print(f"{data['name']}已更新")
        driver.quit()
    except:
        print(f"{data['name']}更新失敗")
        driver.quit()
        worng.append(data['name'])
        continue

print(worng)
driver.quit()