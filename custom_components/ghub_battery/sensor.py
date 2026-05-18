from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass, RestoreSensor
from homeassistant.core import callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers import device_registry as dr
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    known_battery_devices = set()
    known_runtime_devices = set()
    devices_to_add = []

    # Lade bereits bekannte Entitäten aus der Registry, damit sie auch bei ausgeschaltetem PC existieren
    registry = er.async_get(hass)
    device_registry = dr.async_get(hass)
    existing_entities = er.async_entries_for_config_entry(registry, entry.entry_id)

    for entity_entry in existing_entities:
        if entity_entry.domain == "sensor":
            parts = entity_entry.unique_id.split("_")
            if len(parts) >= 4 and parts[0] == "ghub" and parts[1] == entry.entry_id:
                device_id = "_".join(parts[2:-1])
                sensor_type = parts[-1]

                device_name = f"Logitech {device_id}"
                if entity_entry.device_id:
                    device = device_registry.async_get(entity_entry.device_id)
                    if device and device.name:
                        device_name = device.name

                if sensor_type == "battery" and f"{device_id}_battery" not in known_battery_devices:
                    known_battery_devices.add(f"{device_id}_battery")
                    devices_to_add.append(GHubBatterySensor(entry.entry_id, device_id, device_name, {}))
                elif sensor_type == "runtime" and f"{device_id}_runtime" not in known_runtime_devices:
                    known_runtime_devices.add(f"{device_id}_runtime")
                    devices_to_add.append(GHubRuntimeSensor(entry.entry_id, device_id, device_name, {}))

    if devices_to_add:
        async_add_entities(devices_to_add)

    @callback
    def async_add_sensors(payload):
        entry_id = payload.get("entry_id")
        device_id = payload.get("deviceId")
        device_name = payload.get("device_name", f"Logitech {device_id}")
        
        new_devices = []
        if f"{device_id}_battery" not in known_battery_devices:
            known_battery_devices.add(f"{device_id}_battery")
            new_devices.append(GHubBatterySensor(entry_id, device_id, device_name, payload))
        
        if "mileage" in payload and f"{device_id}_runtime" not in known_runtime_devices:
            known_runtime_devices.add(f"{device_id}_runtime")
            new_devices.append(GHubRuntimeSensor(entry_id, device_id, device_name, payload))

        if new_devices:
            async_add_entities(new_devices)

    entry.async_on_unload(
        async_dispatcher_connect(hass, f"{entry.entry_id}_ghub_battery_update", async_add_sensors)
    )

class GHubBaseSensor(RestoreSensor):
    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(self, entry_id, device_id, device_name):
        self._entry_id = entry_id
        self._device_id = device_id
        self._device_name = device_name
        self._state = None

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._device_id)},
            "name": self._device_name,
            "manufacturer": "Logitech"
        }

    async def async_added_to_hass(self):
        await super().async_added_to_hass()
        
        # Stelle den letzten bekannten Wert wieder her, falls der PC offline ist
        last_sensor_data = await self.async_get_last_sensor_data()
        if last_sensor_data is not None and last_sensor_data.native_value is not None:
            self._state = last_sensor_data.native_value

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
        # Nur aktualisieren, wenn echte Daten ankommen (schützt den wiederhergestellten Wert)
        if "percentage" in payload:
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
        if "mileage" in payload:
            mileage = payload.get("mileage")
            self._state = round(mileage, 1) if mileage is not None else None

    @property
    def native_value(self):
        return self._state