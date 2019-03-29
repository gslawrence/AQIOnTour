# Laser Egg On Tour
# Provides live readings of Laser Egg data.

import requests
from datetime import datetime, timezone
import time
interval = 60

# Register at https://dashboard.kaiterra.cn/ and click on the Developer tab
# to obtain an API key and paste it below. Register your devices here as well.
kaiterra_api_key = "API_KEY_GOES_HERE"
# Next, get the UDID of each device you wish to pull data from and enter them.
devices = [
    {"name": "Name", "type": 0, "udid": "00000000-0000-0000-0000-000000000000", "data": []},
    {"name": "Name2", "type": 1, "udid": "00000", "data": []},
    ]

def utc_to_local(utc_dt):
    return utc_dt.replace(tzinfo=timezone.utc).astimezone(tz=None)

def ReadDevices(devices):
    #print("Beginning access procedure at {}.".format(datetime.utcnow()))
    for device in devices:
            #print("Accessing {}...".format(device["name"]))
            if device["type"] == 0: #if this is a Kaiterra device
                res = requests.get("https://api.origins-china.cn/v1/lasereggs/{}?key={}".format(device["udid"], kaiterra_api_key))
                rawdata = res.json()
                ftime = datetime.strptime(rawdata['info.aqi']['ts'], "%Y-%m-%dT%H:%M:%SZ") #convert ts to datetime
                try:
                    device["data"].append({}) #Append a blank dictionary.
                    device["data"][-1]["timestamp"] = ftime #Add formatted time to dict.
                    device["data"][-1]["pm25"] = rawdata['info.aqi']['data']['pm25'] #Add PM2.5 measurement to dict.
                    device["data"][-1]["pm10"] = rawdata['info.aqi']['data']['pm10'] #Add PM10 measurement to dict.
                    device["data"][-1]["humid"]= rawdata['info.aqi']['data']['humidity']
                    device["data"][-1]["temp"] = rawdata['info.aqi']['data']['temp']
                except KeyError:
                    time.sleep(0.0001)
            elif device["type"] == 1: #if this is a PurpleAir device
                res = requests.get("https://www.purpleair.com/json?show={}".format(device["udid"]))
                rawdata = res.json()
                ftime = datetime.utcfromtimestamp(rawdata["results"][1]["LastSeen"])
                try:
                    device["data"].append({}) #Append a blank dictionary.
                    device["data"][-1]["timestamp"] = ftime #Add formatted time to dict.
                    device["data"][-1]["pm25"] = rawdata["results"][1]["PM2_5Value"] #Add PM2.5 measurement to dict.
                    device["data"][-1]["humid"]= rawdata["results"][1]["humidity"]
                    device["data"][-1]["temp"] = (int(rawdata["results"][1]["temp_f"]) - 32) * (5/9)
                except KeyError: #do nothing
                    print("KeyError")
def __main__():
    #print("Entering __main__.")
    while True:
        ReadDevices(devices)
        print("Live Air Quality Data - Updated {}".format(datetime.now()))
        print("Name              PM2.5   PM10    Humid   Temp   Last Update")
        for device in devices:
            devOutput = ""
            devOutput += "{:16} ".format(device["name"])
            if "pm25" in device["data"][-1]:
                devOutput += "{:6.2f}  ".format(float(device["data"][-1]["pm25"]))
            else: devOutput += "  --    " #missing datapoint
            if "pm10" in device["data"][-1]:
                devOutput += "{:6.2f}  ".format(float(device["data"][-1]["pm10"]))
            else: devOutput += "  --    " #missing datapoint
            if "humid" in device["data"][-1]:
                devOutput += "{:6.2f}  ".format(float(device["data"][-1]["humid"]))
            else: devOutput += "  --    " #missing datapoint
            if "temp" in device["data"][-1]:
                devOutput += "{:6.2f}  ".format(float(device["data"][-1]["temp"]))
            else: devOutput += "  --    " #missing datapoint
            if "timestamp" in device["data"][-1]:
                devOutput += "{}  ".format(utc_to_local(device["data"][-1]["timestamp"]).strftime("%Y-%m-%d %H:%M:%S UTC %z"))
            print(devOutput)
        print("==============================================================================")
        for i in range(0, interval - 1):
            time.sleep(1)
__main__()
