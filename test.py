from mongo import attraction_db
import requests

def generate_custom_id(city_name):
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

def get_place_id(matching_city):
    prefix = generate_custom_id(matching_city)
    if prefix == '':return ''
    matching_count = attraction_db.attractionInfo.count_documents({"id": {"$regex": f"^{prefix}"}})
    new_id = f"{prefix}_{matching_count + 1:03d}"
    return new_id

def get_place_detail(location_name):
    city_list = ['新北市','基隆市','台北市','宜蘭縣','桃園市','苗栗縣','新竹市','台中市','雲林縣', '彰化縣','嘉義縣','台南市','高雄市','花蓮縣','台東縣','南投縣','屏東縣','澎湖縣','金門縣']
    api_url = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json"
    params = {
        "input": location_name,  # 您要搜尋的地點名稱
        "inputtype": "textquery",
        "fields": "formatted_address,name",
        "key": "AIzaSyDO8r5ORxeM41JF82SFLdVRfEyjA08C_Ro"  # 請替換為您的Google Maps API金鑰
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
            "id":get_place_id(matching_city),
            "region": matching_city 
        }
        return result
    else:
        return "無法取得回應。"
    
print(get_place_detail('101觀景台'))