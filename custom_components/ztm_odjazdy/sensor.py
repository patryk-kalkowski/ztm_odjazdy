import requests
import logging
from datetime import timedelta
from homeassistant.components.sensor import SensorEntity
from homeassistant.util import dt as dt_util

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    stop_id = config_entry.data.get("stop_id")
    friendly_name = config_entry.data.get("friendly_name")
    lines_raw = config_entry.data.get("lines", "")
    interval = config_entry.data.get("update_interval", 2)
    max_minutes = config_entry.data.get("max_minutes", 50)
    
    filter_list = [l.strip() for l in lines_raw.split(";")] if lines_raw else []
    
    sensor = ZtmSensor(stop_id, friendly_name, filter_list, interval, max_minutes)
    async_add_entities([sensor], True)

class ZtmSensor(SensorEntity):
    def __init__(self, stop_id, friendly_name, filter_list, interval, max_minutes):
        self._stop_id = stop_id
        self._filter_list = filter_list
        self._custom_name = friendly_name
        self._max_minutes = max_minutes
        self._state = None
        self._attributes = {}
        
        self._attr_scan_interval = timedelta(minutes=interval)
        self._attr_name = friendly_name
        self._attr_unique_id = f"ztm_odjazdy_{stop_id}"
    
    @property
    def state(self):
        return self._state
    
    @property
    def extra_state_attributes(self):
        return self._attributes
    
    def update(self):
        url = f"https://ckan2.multimediagdansk.pl/departures?stopId={self._stop_id}"
        
        try:
            r = requests.get(url, timeout=10)
            r.raise_for_status()
            data = r.json()
            
            now = dt_util.utcnow()
            departures = []
            
            for entry in data.get("departures", []):
                try:
                    route_id = str(entry.get("routeId"))
                    time_str = entry.get("estimatedTime")
                    
                    if not time_str:
                        continue
                    
                    dep_time = dt_util.parse_datetime(time_str)
                    if not dep_time:
                        continue
                    
                    diff_min = (dep_time - now).total_seconds() / 60

                    if self._filter_list and route_id not in self._filter_list:
                        continue
                    
                    if -2 <= diff_min <= self._max_minutes:
                        departures.append({
                            "linia": route_id,
                            "kierunek": entry.get("headsign"),
                            "czas": time_str,
                            "minuty": max(0, round(diff_min))
                        })
                        
                except Exception as entry_err:
                    _LOGGER.warning("Pominięto błędny odjazd: %s", entry_err)
                    continue
            
            departures.sort(key=lambda x: x["czas"])
            self._state = len(departures)
            self._attributes = {
                "stop_id": self._stop_id,
                "nazwa_przystanku": self._custom_name,
                "limit_minut": self._max_minutes,
                "odjazdy": departures,
                "ostatnia_aktualizacja": dt_util.now().strftime("%H:%M:%S")
            }
            
        except Exception as e:
            _LOGGER.error("Error ZTM Odjazdy (%s): %s", self._stop_id, e)
            self._state = "unavailable"