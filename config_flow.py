import aiohttp
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers.selector import SelectSelector, SelectSelectorConfig, SelectSelectorMode

from .const import DOMAIN

STOPS_URL = "https://ckan.multimediagdansk.pl/dataset/c24aa637-3619-4dc2-a171-a23eec8f2172/resource/d3e96eb6-25ad-4d6c-8651-b1eb39155945/download/stopsingdansk.json"

class ZtmGdanskConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        
        # Pobieranie listy przystanków z API
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(STOPS_URL, timeout=10) as response:
                    data = await response.json()
                    stops_data = sorted(data.get("stops", []), key=lambda x: x["stopName"])
                    
                    options = [
                        {
                            "value": str(stop["stopId"]), 
                            "label": f"{stop['stopName']} {stop['stopCode']}"
                        }
                        for stop in stops_data if stop.get("nonpassenger") == 0
                    ]
        except Exception:
            return self.async_abort(reason="cannot_connect")

        if user_input is not None:
            if user_input.get("update_interval", 1) < 1:
                errors["update_interval"] = "invalid_interval"
            else:
                selected_label = next(
                    (opt["label"] for opt in options if opt["value"] == user_input["stop_id"]), 
                    user_input["stop_id"]
                )
                
                await self.async_set_unique_id(user_input["stop_id"])
                self._abort_if_unique_id_configured()
                
                return self.async_create_entry(
                    title=selected_label, 
                    data={
                        **user_input,
                        "friendly_name": selected_label
                    }
                )

        data_schema = vol.Schema({
            vol.Required("stop_id"): SelectSelector(
                SelectSelectorConfig(
                    options=options,
                    mode=SelectSelectorMode.DROPDOWN,
                    translation_key="stop_id"
                )
            ),
            vol.Optional("lines", default=""): str,
            vol.Optional("update_interval", default=1): vol.Coerce(int),
            vol.Optional("max_minutes", default=50): vol.Coerce(int),
        })

        return self.async_show_form(
            step_id="user", 
            data_schema=data_schema, 
            errors=errors
        )