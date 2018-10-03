import requests
import pyowm
from datetime import datetime
import time



api_key = 'cc01eeec160945bb92713eacb27b7548'
fmt = '%Y-%m-%dT%H:%M:%S'
url = 'http://lapi.transitchicago.com/api/1.0/ttarrivals.aspx?key=cc01eeec160945bb92713eacb27b7548&mapid=40660&outputType=JSON'
offset_y = 12
owm = pyowm.OWM('a1dc33b1459c16525fcd48856fc424e3')  # You MUST provide a valid API key

def get_weather():
    import pyowm

    # Search for current weather in London (Great Britain)
    observation = owm.weather_at_place('London,GB')
    w = observation.get_weather()
    print(w)                      # <Weather - reference time=2013-12-18 09:20,
                                  # status=Clouds>

    # Weather details
    w.get_wind()                  # {'speed': 4.6, 'deg': 330}
    w.get_humidity()              # 87
    w.get_temperature('celsius')  # {'temp_max': 10.5, 'temp': 9.7, 'temp_min': 9.0}

    # Search current weather observations in the surroundings of
    # lat=22.57W, lon=43.12S (Rio de Janeiro, BR)
    observation_list = owm.weather_around_coords(-22.57, -43.12)

    print(observation_list)

def get_trains():

    r = requests.get(url).json()['ctatt']['eta']

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
