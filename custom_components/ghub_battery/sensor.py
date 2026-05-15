from homeassistant.components.sensor import SensorEntity, SensorDeviceClass, SensorStateClass
from homeassistant.core import callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    known_battery_devices = set()
    known_runtime_devices = set()

    @callback
    def async_add_sensors(payload):
        entry_id = payload.get("entry_id")
        device_id = payload.get("deviceId")
        device_name = payload.get("device_name", f"Logitech {device_id}")
        
        if f"{device_id}_battery" not in known_battery_devices:
            known_battery_devices.add(f"{device_id}_battery")
            async_add_entities([GHubBatterySensor(entry_id, device_id, device_name, payload)])
        
        if "mileage" in payload and f"{device_id}_runtime" not in known_runtime_devices:
            known_runtime_devices.add(f"{device_id}_runtime")
            async_add_entities([GHubRuntimeSensor(entry_id, device_id, device_name, payload)])

    entry.async_on_unload(
        async_dispatcher_connect(hass, f"{entry.entry_id}_ghub_battery_update", async_add_sensors)
    )

class GHubBaseSensor(SensorEntity):
    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(self, entry_id, device_id, device_name):
        self._entry_id = entry_id
        self._device_id = device_id
        self._device_name = device_name

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

class GHubBatterySensor(GHubBaseSensor):
    _attr_device_class = SensorDeviceClass.BATTERY
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = "%"
    _attr_translation_key = "battery"

    def __init__(self, entry_id, device_id, device_name, initial_payload):
        super().__init__(entry_id, device_id, device_name)
        self._attr_unique_id = f"ghub_{entry_id}_{device_id}_battery"
        self._update_state(initial_payload)

    def _update_state(self, payload):
        self._state = payload.get("percentage")

    @property
    def native_value(self):
        return self._state

class GHubRuntimeSensor(GHubBaseSensor):
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = "h"
    _attr_icon = "mdi:clock-outline"
    _attr_translation_key = "runtime"

    def __init__(self, entry_id, device_id, device_name, initial_payload):
        super().__init__(entry_id, device_id, device_name)
        self._attr_unique_id = f"ghub_{entry_id}_{device_id}_runtime"
        self._update_state(initial_payload)

    def _update_state(self, payload):
        mileage = payload.get("mileage")
        self._state = round(mileage, 1) if mileage is not None else None

    @property
    def native_value(self):
        return self._state