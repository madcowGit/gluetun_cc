from homeassistant import config_entries
from homeassistant.const import CONF_NAME, CONF_URL
from voluptuous import All, Length, Url, Optional, Invalid

def validate_instance_name(instance_name):
    if not isinstance(instance_name, str):
        raise Invalid('Instance name must be a string')
    if len(instance_name) < 1:
        raise Invalid('Instance name cannot be empty')

def validate_base_url(base_url):
    if not base_url.startswith('http'):
        raise Invalid('Base URL must start with http or https')

class GluetunConfigFlow(config_entries.ConfigFlow, domain="gluetun_cc"):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        schema = {  
            Optional(CONF_NAME, default="Default Name"): All(str, Length(min=1)),
            CONF_URL: All(str, validate_base_url),
            "instance_name": All(str, validate_instance_name)
        }

        if user_input is not None:
            instance_name = user_input.get('instance_name')
            base_url = user_input.get(CONF_URL)
            unique_id = f"{instance_name}_{base_url}"
            # Logic to create unique config entries using instance_name
            # logic to handle new entry vs existing ones goes here
            # Save the config entry with the unique_id

            return self.async_create_entry(title=user_input[CONF_NAME], data=user_input, unique_id=unique_id)

        return self.async_show_form(step_id="user", data_schema=schema)
