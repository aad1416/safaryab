from datetime import datetime, time
import primp
import orjson


min_price = 8500
max_time = (20, 0)
dep_data = "2026-08-22"
url = f"https://api.pateh.com/gateway/api/v2/bridge/flight/search?origin=MHD&destination=THR&departure_date={dep_data}&adult_count=1&child_count=0&infant_count=0"





pr = primp.Client(impersonate="random", impersonate_os="windows", http2_only=True)
flight_list = []
try:
    raw = pr.get(url)
    js: dict = orjson.loads(raw.content)
    for i in js.get("items"):
        if i["fare"] / 10000 < min_price and datetime.fromisoformat(i["depart"][0]["departure_datetime"]).time() < time(*max_time):
            flight_list.append((i["fare"] , datetime.fromisoformat(i["depart"][0]["departure_datetime"])))
    if flight_list:
        pr.post("https://safar.aad1416.workers.dev/_discordbot" , json = flight_list)
except Exception as e:
    print(e)
