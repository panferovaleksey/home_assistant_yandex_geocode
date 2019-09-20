# home_assistant_yandex_geocode

Custom component reverse geocoding with Yandex Geocode for Home Assistant.

Reworked code based on Google Geocode Home Assistant component "michaelmcarthur" (original link: https://github.com/michaelmcarthur/GoogleGeocode-HASS)

**This component is relevant for Russian users, using Cyrillic. For other use original Google Geocode component.
All titles in Russian. Address formatted for Russian features.**

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