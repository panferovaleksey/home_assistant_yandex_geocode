# home_assistant_yandex_geocode
**UPDATE 25.04.2019 add required additional files for Home Assistant version 0.92. Please download additional new file: manifest.json and create empty file __init__.py in component folder.**

**UPDATE 29.03.2019 small modification for correct work in small city in Russia. Please update sensor.py from new file.**

Custom component reverse geocoding with Yandex Geocode for Home Assistant.

Reworked code based on Google Geocode Home Assistant component "michaelmcarthur" (original link: https://github.com/michaelmcarthur/GoogleGeocode-HASS)

**This component is relevant for Russian users, using Cyrillic. For other use original Google Geocode component.
All titles in Russian. Address formatted for Russian features.**

Installation:

**For HA version before 0.88.2**
Copy the yandex_geocode.py file and place it in <config_dir>/custom_components/sensor/yandex_geocode.py.

**For HA version after 0.89**
Copy the yandex_geocode.py file, rename to sensor.py and place it in <config_dir>/custom_components/yandex_geocode/sensor.py.

Setup in sensor section:

```
platform: yandex_geocode
name: name
origin: device_tracker.name
options: street, street_number
display_zone: hide
gravatar: your_fravatar_id
api_key: your_api_key_for_yandex_geocode
```
  
Yandex Geocode API key request page - https://tech.yandex.ru/maps/geocoder/
  
![Sensor in home assistant](https://github.com/renat85/home_assistant_yandex_geocode/blob/master/HA_Sensor_Yandex.JPG?raw=true)

![Sensor full in home assistant](https://github.com/renat85/home_assistant_yandex_geocode/blob/master/HA_Sensor_Yandex_full.png?raw=true)
