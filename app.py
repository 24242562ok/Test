from flask import Flask, render_template
import requests
from datetime import datetime

app = Flask(__name__)

# CWA API Key
api_key = "CWA-058D5716-80B5-401B-873D-D5611E4CDFC6"

@app.route('/')
def index():
    # 取得雲林縣天氣預報資料
    url_weather = f"https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-C0032-001?Authorization={api_key}"
    response_weather = requests.get(url_weather)
    
    if response_weather.status_code == 200:
        data = response_weather.json()
        location_data = next((loc for loc in data["records"]["location"] if loc["locationName"] == "雲林縣"), None)

        if location_data:
            weather_elements = {element["elementName"]: element["time"] for element in location_data["weatherElement"]}
            now_weather = weather_elements["Wx"][0]["parameter"]["parameterName"]
            pop = int(weather_elements["PoP"][0]["parameter"]["parameterName"])
            future_max_temp = int(weather_elements["MaxT"][1]["parameter"]["parameterName"])
            future_min_temp = int(weather_elements["MinT"][1]["parameter"]["parameterName"])
            rain_advice = "天氣穩定，無需攜帶雨具。" if pop < 30 else "有降雨機率，建議攜帶雨具。"
        else:
            now_weather, pop, future_max_temp, future_min_temp, rain_advice = None, None, None, None, None
    else:
        now_weather, pop, future_max_temp, future_min_temp, rain_advice = None, None, None, None, None

    # 取得虎尾觀測站氣溫
    url_temp = f"https://opendata.cwa.gov.tw/api/v1/rest/datastore/O-A0001-001?Authorization={api_key}"
    response_temp = requests.get(url_temp)
    
    if response_temp.status_code == 200:
        data_temp = response_temp.json()
        stations = data_temp["records"].get("Station", [])
        huwei_station = next((s for s in stations if s["StationId"] == "C0K330"), None)
        temp = float(huwei_station["WeatherElement"].get("AirTemperature", 0)) if huwei_station else None
    else:
        temp = None

    # 根據溫度推薦衣物
    if temp is not None:
        if temp >= 25.5:
            clothes = "短袖"
        elif temp >= 22.5:
            clothes = "短袖+薄長袖"
        elif temp >= 20.5:
            clothes = "短袖+厚長袖"
        elif temp >= 18.5:
            clothes = "厚長袖+厚外套"
        elif temp >= 16.5:
            clothes = "厚長袖+輕羽絨"
        elif temp >= 14.5:
            clothes = "厚長袖+厚羽絨"
        else:
            clothes = "全副武裝"
    else:
        clothes = "無法獲取資料"

    # 當前時間
    now = datetime.now()
    formatted_time = f"{now.year}年{now.month:02d}月{now.day:02d}日 {now.hour:02d}:{now.minute:02d}"

    return render_template("index.html", weather=now_weather, pop=pop, temp=temp, clothes=clothes, rain_advice=rain_advice, time=formatted_time)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

