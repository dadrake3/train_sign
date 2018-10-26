import requests
import json
import pyowm
from datetime import datetime
import time
from wifi import Cell



api_key = 'cc01eeec160945bb92713eacb27b7548'
fmt = '%Y-%m-%dT%H:%M:%S'
url = 'http://lapi.transitchicago.com/api/1.0/ttarrivals.aspx?key=cc01eeec160945bb92713eacb27b7548&mapid=40660&outputType=JSON'
offset_y = 12
owm = pyowm.OWM('a1dc33b1459c16525fcd48856fc424e3')  # You MUST provide a valid API key
google_api_key = 'AIzaSyDLQ5jyuG_srSR4S4lNYnSbSs9zI6Mvtok'

old_weather = ''

def get_weather():
    global old_weather
    cells = Cell.all('wlan0')
    wifi_aps = []

    url = 'https://www.googleapis.com/geolocation/v1/geolocate?key=' + google_api_key

    payload = {"considerIp": "true", 'wifiAccessPoints': []}
    jsonPayload = json.dumps(payload)
    headers = {'content-type': 'application/json'}



    for cell in cells:
        #signal -> signal strength
        #quality -> signal to noise raito
        w = {
            'macAddress': cell.address,
            'signalStrength': cell.signal,
            'channel': cell.channel,
            'signalToNoiseRatio': cell.quality
        }

        payload['wifiAccessPoints'].append(w)

    try:
        r = requests.post(url,data=jsonPayload,headers = headers)
        response = json.loads(r.text)
    except:
        if old_weather:
            return old_weather
        else:
            return None, None

    observation = owm.weather_around_coords(response['location']['lat'], response['location']['lng'], limit=1)
    w = observation[0].get_weather()

    c = w.get_status()
    b = w.get_temperature('fahrenheit')['temp']  # {'temp_max': 10.5, 'temp': 9.7, 'temp_min': 9.0}


    ret = (str(int(b)) + '\N{DEGREE SIGN}', c)
    old_weather = ret
    return ret


def get_trains():

    try:
        r = requests.get(url).json()['ctatt']['eta']
    except:
        return None

    arrivals = []

    for eta in r:
        arr = {}
        if eta['trDr'] == '5':
            arr['dest'] = 'Loop'
        elif eta['trDr'] == '1':
            arr['dest'] = 'Kimball'
        else:
            pass

        d1 = datetime.strptime(eta['prdt'], fmt)
        d2 = datetime.strptime(eta['arrT'], fmt)

        # Convert to Unix timestamp
        d1_ts = time.mktime(d1.timetuple())
        d2_ts = time.mktime(d2.timetuple())

        # They are now in seconds, subtract and then divide by 60 to get minutes.
        if eta['isApp'] == '1':
            arr['is_app'] = True
        else:
            arr['is_app'] = False

        arr['arr_t'] = str(int((d2_ts - d1_ts) / 60))

        arrivals.append(arr)

    return arrivals
