"""
Support for Yandex Geocode sensors.

For more details about this platform, please refer to the documentation at
https://github.com/michaelmcarthur/GoogleGeocode-HASS
"""
# -*- coding: utf-8 -*-
from datetime import datetime
from datetime import timedelta 
import logging
import json
import requests
from requests import get

import voluptuous as vol

from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import (
    CONF_API_KEY, CONF_NAME, CONF_SCAN_INTERVAL, ATTR_ATTRIBUTION, ATTR_LATITUDE, ATTR_LONGITUDE)
import homeassistant.helpers.location as location
from homeassistant.util import Throttle
from homeassistant.helpers.entity import Entity
import homeassistant.helpers.config_validation as cv

_LOGGER = logging.getLogger(__name__)

CONF_ORIGIN = 'origin'
CONF_OPTIONS = 'options'
CONF_DISPLAY_ZONE = 'display_zone'
CONF_ATTRIBUTION = "Data provided by https://geocode-maps.yandex.ru"
CONF_GRAVATAR = 'gravatar'

ATTR_COUNTRY = 'Страна'
ATTR_REGION = 'Область'
ATTR_COUNTY = 'Район'
ATTR_CITY = 'Город'
ATTR_STREET = 'Улица'
ATTR_STREET_NUMBER = 'Номер дома'

DEFAULT_NAME = 'Yandex Geocode'
DEFAULT_OPTION = 'country, state'
DEFAULT_DISPLAY_ZONE = 'display'
DEFAULT_KEY = 'no key'
current = '0,0'
zone_check = 'a'
SCAN_INTERVAL = timedelta(seconds=15)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_ORIGIN): cv.string,
    vol.Optional(CONF_API_KEY, default=DEFAULT_KEY): cv.string,
    vol.Optional(CONF_OPTIONS, default=DEFAULT_OPTION): cv.string,
    vol.Optional(CONF_DISPLAY_ZONE, default=DEFAULT_DISPLAY_ZONE): cv.string,
    vol.Optional(CONF_GRAVATAR, default=None): vol.Any(None, cv.string),
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    vol.Optional(CONF_SCAN_INTERVAL, default=SCAN_INTERVAL):
        cv.time_period,
})

TRACKABLE_DOMAINS = ['device_tracker', 'sensor']

def setup_platform(hass, config, add_devices, discovery_info=None):
    """Setup the sensor platform."""
    name = config.get(CONF_NAME)
    api_key = config.get(CONF_API_KEY)
    origin = config.get(CONF_ORIGIN)
    options = config.get(CONF_OPTIONS)
    display_zone = config.get(CONF_DISPLAY_ZONE)
    gravatar = config.get(CONF_GRAVATAR) 

    add_devices([YandexGeocode(hass, origin, name, api_key, options, display_zone, gravatar)])


class YandexGeocode(Entity):
    """Representation of a Yandex Geocode Sensor."""

    def __init__(self, hass, origin, name, api_key, options, display_zone, gravatar):
        """Initialize the sensor."""
        self._hass = hass
        self._name = name
        self._api_key = api_key
        self._options = options.lower()
        self._display_zone = display_zone.lower()
        self._state = "Обновление данных"
        self._gravatar = gravatar

        self._country = None
        self._county = None
        self._region = None
        self._city = None
        self._city = None
        self._street = None
        self._street_number = None        
        self._zone_check_current = None

        # Check if origin is a trackable entity
        if origin.split('.', 1)[0] in TRACKABLE_DOMAINS:
            self._origin_entity_id = origin
        else:
            self._origin = origin

        if gravatar is not None:
            self._picture = self._get_gravatar_for_email(gravatar)
        else:
            self._picture = None

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def entity_picture(self):
        """Return the picture of the device."""
        return self._picture
        
    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        return{
            ATTR_STREET: self._street,
            ATTR_STREET_NUMBER: self._street_number,
            ATTR_CITY: self._city,
            ATTR_COUNTY: self._county,
            ATTR_REGION: self._region,
            ATTR_COUNTRY: self._country,
            ATTR_ATTRIBUTION: CONF_ATTRIBUTION,
        }

    @Throttle(SCAN_INTERVAL)
    def update(self):
        """Get the latest data and updates the states."""

        if hasattr(self, '_origin_entity_id'):
            self._origin = self._get_location_from_entity(
                self._origin_entity_id
            )

        """Update if location has changed."""

        global current
        global zone_check_count
        global zone_check
        global user_display
        zone_check = self.hass.states.get(self._origin_entity_id).state
        zone_check_count = 2

        if zone_check == self._zone_check_current:
            zone_check_count = 1
        if zone_check == 'not_home':
            zone_check_count = 2
        if zone_check_count == 1:
            pass
        elif self._origin == None:
            pass
        elif current == self._origin:
            pass
        else:
            _LOGGER.info("yandex request sent")
            self._zone_check_current = self.hass.states.get(self._origin_entity_id).state
            zone_check_count = 2
            lat = self._origin
            current = lat
            self._reset_attributes()
            if self._api_key == 'no key':
                url = "https://geocode-maps.yandex.ru/"
            else:
                url = "https://geocode-maps.yandex.ru/1.x/?apikey=" + self._api_key + "&geocode=" + lat + "&format=json" + "&results=1"
            yandex = get(url)
            json_input = yandex.text
            decoded = json.loads(json_input)
            country = 'Не определено'
            county = 'Не определено'
            state = 'Не определено'
            city = 'Не определено'
            street = 'Не определено'
            street_number = 'Не определено'
                        
            for component in decoded['response']['GeoObjectCollection']['featureMember']:
                for data in component["GeoObject"]["metaDataProperty"]["GeocoderMetaData"]["Address"]["Components"]:
                    if 'country' in data["kind"]:
                        country = data["name"]
                        self._country = country
                    if 'area' in data["kind"]:
                        county = data["name"]
                        self._county = county
                    if 'province' in data["kind"]:
                        state = data["name"]
                        self._region = state
                    if 'locality' in data["kind"]:
                        city = data["name"]
                        self._city = city
                    if 'street' in data["kind"]:
                        street = data["name"]
                        self._street = street
                    if 'house' in data["kind"]:
                        street_number = data["name"]
                        self._street_number = street_number
            try:
                if 'formatted' in decoded:
                    formatted_address = decoded['formatted']
                    self._formatted_address = formatted_address			
            
            except IndexError:
                pass

            if 'error_message' in decoded:
                self._state = decoded['error_message']
                _LOGGER.error("You have exceeded your daily requests or entered a incorrect key please create or check the api key.")
            elif self._display_zone == 'hide' or zone_check == "not_home":
                if street == 'Unnamed Road':
                    street = alt_street
                    self._street = alt_street
                if city == '':
                    city = city
                    if city == '':
                        city = county

                display_options = self._options
                user_display = []

                if "country" in display_options:
                    self._append_to_user_display(country)
                if "state" in display_options:
                    self._append_to_user_display(state)
                if "county" in display_options:
                    self._append_to_user_display(county)
                if "city" in display_options:
                    self._append_to_user_display(city)
                if "street" in display_options:
                    user_display.append(street)
                if "street_number" in display_options:
                    user_display.append(street_number)
                """if "postal_code" in display_options:
                    self._append_to_user_display(postal_code)"""
                
                        
                user_display = ', '.join(  x for x in user_display )
                
                if user_display == '':
                    user_display = county
                self._state = user_display
            else:
                self._state = zone_check[0].upper() + zone_check[1:]

    def _get_location_from_entity(self, entity_id):
        """Get the origin from the entity state or attributes."""
        entity = self._hass.states.get(entity_id)

        if entity is None:
            _LOGGER.error("Unable to find entity %s", entity_id)
            return None

        # Check if the entity has origin attributes
        if location.has_location(entity):
            return self._get_location_from_attributes(entity)

        # When everything fails just return nothing
        return None

    def _reset_attributes(self):
        """Resets attributes."""
        self._country = None
        self._region = None
        self._county = None
        self._city = None
        self._street = None
        self._street_number = None
        
    def _append_to_user_display(self, append_check):
        """Appends attribute to state if false."""
        if append_check == "":
            pass
        else:
            user_display.append(append_check)

    @staticmethod
    def _get_location_from_attributes(entity):
        """Get the lat/long string from an entities attributes."""
        attr = entity.attributes
        return "%s,%s" % (attr.get(ATTR_LONGITUDE), attr.get(ATTR_LATITUDE))
        
    def _get_gravatar_for_email(self, email: str):
        """Return an 80px Gravatar for the given email address.
        Async friendly.
        """
        import hashlib
        url = 'https://www.gravatar.com/avatar/{}.jpg?s=80&d=wavatar'
        return url.format(hashlib.md5(email.encode('utf-8').lower()).hexdigest())
