from homeassistant.components.binary_sensor import BinarySensorEntity, BinarySensorDeviceClass
from homeassistant.core import callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    known_charging_devices = set()

    @callback
    def async_add_binary_sensor(payload):
        entry_id = payload.get("entry_id")
        device_id = payload.get("deviceId")
        device_name = payload.get("device_name", f"Logitech {device_id}")
        
        if f"{device_id}_charging" not in known_charging_devices:
            known_charging_devices.add(f"{device_id}_charging")
            async_add_entities([GHubChargingBinarySensor(entry_id, device_id, device_name, payload)])

    entry.async_on_unload(
        async_dispatcher_connect(hass, f"{entry.entry_id}_ghub_battery_update", async_add_binary_sensor)
    )

class GHubChargingBinarySensor(BinarySensorEntity):
    _attr_device_class = BinarySensorDeviceClass.BATTERY_CHARGING
    _attr_should_poll = False
    _attr_has_entity_name = True
    _attr_translation_key = "charging"

    def __init__(self, entry_id, device_id, device_name, initial_payload):
        self._entry_id = entry_id
        self._device_id = device_id
        self._device_name = device_name
        self._attr_unique_id = f"ghub_{entry_id}_{device_id}_charging"
        self._update_state(initial_payload)

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._device_id)},
            "name": self._device_name,
            "manufacturer": "Logitech"
        }

    async def async_added_to_hass(self):
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass, f"{self._entry_id}_ghub_battery_{self._device_id}", self._handle_update
            )
        )

    @callback
    def _handle_update(self, payload):
        self._update_state(payload)
        self.async_write_ha_state()

    def _update_state(self, payload):
        self._is_on = payload.get("charging", False)

    @property
    def is_on(self):
        return self._is_on