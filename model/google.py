from dotenv import load_dotenv,find_dotenv
from selenium import webdriver
from mongo import attraction_db
import googlemaps
import requests
import json
import os

class Google:
    def __init__(self):
        load_dotenv(find_dotenv())
        self.google_api_key = os.environ.get("GOOGLE_PLACES_API_KEY")
        self.driver = webdriver.Chrome()
        self.map_client = googlemaps.Client(self.google_api_key)

    def get_google_map_image(self,reference):
        try:
            self.driver.set_window_size(800,800)
            url = 'https://maps.googleapis.com/maps/api/place/photo?photoreference={photoreference}&sensor=false&maxheight=1200&maxwidth=1200&key={key}'.format(photoreference=reference,key=self.google_api_key)
            self.driver.get(url)
            return self.driver.current_url
        except:
            return 'none' 
        
    def get_place_info(self,location_name,url,tag):
        try:
            data = {}
            response = self.map_client.places(query = location_name)
            result = response.get('results') 

            place_detail = self.get_place_detail(location_name)
            data['name'] = location_name
            data['google_url'] = url
            try:data['address'] = place_detail['address']
            except:data['address'] = ''
            try:data['id'] = place_detail['id']
            except:data['id'] = ''
            try:data['region'] = place_detail['region']
            except:data['region'] = ''
            try:data['place_id'] = result[0]['place_id']
            except:data['place_id'] = ''
            try:data['google_address'] = result[0]['formatted_address']
            except:data['google_address'] = ''
            try:data['rating'] = result[0]['rating']
            except:data['rating'] = ''
            try:data['user_ratings_total'] = result[0]['user_ratings_total']
            except:data['user_ratings_total'] = ''
            try:data['lat'] = result[0]['geometry']['location']['lat']
            except:data['lat'] = ''
            try:data['lng'] = result[0]['geometry']['location']['lng']
            except:data['lng'] = ''
            try:data['photo_reference'] = result[0]['photos'][0]['photo_reference']
            except:data['photo_reference'] = ''
            try:data['photo_url'] = self.get_google_map_image(result[0]['photos'][0]['photo_reference'])
            except:data['photo_url'] = ''
            try: data['tag'] = tag
            except:data['tag'] = ''
            json_data = json.dumps(data, ensure_ascii=False)
            return json_data
        except:
            return 'none' 
        
    def generate_custom_id(self,city_name):
        # 可以自行定義每個縣市的編碼前綴
        city_prefixes = {
            "台北市": "TPE",
            "新北市": "TPH",
            "基隆市": "KLU",
            "宜蘭縣": "ILN",
            "桃園市": "TYC",
            "苗栗縣": "MAL",
            "新竹市": "HSC",
            "台中市": "TXG",
            "雲林縣": "YLH",
            "彰化縣": "CWH",
            "嘉義縣": "CHY",
            "台南市": "TNN",
            "高雄市": "KHH",
            "花蓮縣": "HWA",
            "台東縣": "KEL",
            "南投縣": "TTT",
            "屏東縣": "IUH",
            "澎湖縣": "PEH",
            "金門縣": "KMN",
        }
        prefix = city_prefixes.get(city_name,"") 
        return prefix
    
    def get_place_id(self,matching_city):
        prefix = self.generate_custom_id(matching_city)
        if prefix == '':return ''
        existing_ids = attraction_db.attractionInfo.find({"id": {"$regex": f"^{prefix}_\\d+$"}}, {"id": 1})
        existing_numbers = [int(doc["id"].split('_')[-1]) for doc in existing_ids]
        max_number = max(existing_numbers) if existing_numbers else 0
        new_number = max_number + 1
        if new_number > 999:
            prefix_parts = prefix.split('_')
            prefix_number = int(prefix_parts[1]) + 1
            prefix = f"{prefix_parts[0]}_{prefix_number:03d}"
            new_number = 1
        new_id = f"{prefix}_{new_number:03d}"
        return new_id
    
    def get_place_detail(self,location_name):
        city_list = ['新北市','基隆市','台北市','宜蘭縣','桃園市','苗栗縣','新竹市','台中市','雲林縣', '彰化縣','嘉義縣','台南市','高雄市','花蓮縣','台東縣','南投縣','屏東縣','澎湖縣','金門縣']
        api_url = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json"
        params = {
            "input": location_name,  # 您要搜尋的地點名稱
            "inputtype": "textquery",
            "fields": "formatted_address,name",
            "key": self.google_api_key  # 請替換為您的Google Maps API金鑰
        }
        response = requests.get(api_url, params=params)

        if response.status_code == 200:
            data = response.json()
            # 在這裡處理API回應的JSON資料
            formatted_address = data['candidates'][0]['formatted_address']
            formatted_address = formatted_address.replace("台灣", "")

            matching_city = ''
            for city in city_list:
                if city[:2] in formatted_address:
                    matching_city = city
                    break
                
            result = {
                "address": formatted_address,
                "id":self.get_place_id(matching_city),
                "region": matching_city 
            }
            return result
        else:
            return "無法取得回應。"