from homeassistant.components.binary_sensor import BinarySensorEntity, BinarySensorDeviceClass
from homeassistant.core import callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.restore_state import RestoreEntity
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    known_charging_devices = set()
    devices_to_add = []

    registry = er.async_get(hass)
    device_registry = dr.async_get(hass)
    existing_entities = er.async_entries_for_config_entry(registry, entry.entry_id)

    for entity_entry in existing_entities:
        if entity_entry.domain == "binary_sensor":
            parts = entity_entry.unique_id.split("_")
            if len(parts) >= 4 and parts[0] == "ghub" and parts[1] == entry.entry_id:
                device_id = "_".join(parts[2:-1])
                sensor_type = parts[-1]

                device_name = f"Logitech {device_id}"
                if entity_entry.device_id:
                    device = device_registry.async_get(entity_entry.device_id)
                    if device and device.name:
                        device_name = device.name

                if sensor_type == "charging" and f"{device_id}_charging" not in known_charging_devices:
                    known_charging_devices.add(f"{device_id}_charging")
                    devices_to_add.append(GHubChargingBinarySensor(entry.entry_id, device_id, device_name, {}))

    if devices_to_add:
        async_add_entities(devices_to_add)

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

class GHubChargingBinarySensor(BinarySensorEntity, RestoreEntity):
    _attr_device_class = BinarySensorDeviceClass.BATTERY_CHARGING
    _attr_should_poll = False
    _attr_has_entity_name = True
    _attr_translation_key = "charging"

    def __init__(self, entry_id, device_id, device_name, initial_payload):
        self._entry_id = entry_id
        self._device_id = device_id
        self._device_name = device_name
        self._attr_unique_id = f"ghub_{entry_id}_{device_id}_charging"
        self._is_on = None
        self._update_state(initial_payload)

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._device_id)},
            "name": self._device_name,
            "manufacturer": "Logitech"
        }

    async def async_added_to_hass(self):
        await super().async_added_to_hass()
        
        state = await self.async_get_last_state()
        if state is not None and state.state in ("on", "off"):
            self._is_on = state.state == "on"

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
        if "charging" in payload:
            self._is_on = payload.get("charging", False)

    @property
    def is_on(self):
        return self._is_on