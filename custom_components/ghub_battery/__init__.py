import asyncio
import json
import logging
import websockets
import re
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.const import Platform

from .const import DOMAIN, CONF_HOST

_LOGGER = logging.getLogger(__name__)
PLATFORMS = [Platform.SENSOR, Platform.BINARY_SENSOR]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "device_names": {},
        "ws_task": None
    }
    host = entry.data[CONF_HOST]

    task = hass.loop.create_task(ghub_ws_listener(hass, entry.entry_id, host))
    hass.data[DOMAIN][entry.entry_id]["ws_task"] = task

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        task = hass.data[DOMAIN][entry.entry_id]["ws_task"]
        if task:
            task.cancel()
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok

async def ghub_ws_listener(hass: HomeAssistant, entry_id: str, host: str):
    uri = f"ws://{host}:9010"
    headers = {
        "Host": "localhost:9010",
        "Origin": "file://",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache"
    }

    while True:
        try:
            async with websockets.connect(uri, additional_headers=headers, subprotocols=["json"], ping_interval=20, ping_timeout=20) as ws:
                _LOGGER.info("Erfolgreich mit G Hub WebSocket verbunden")
                
                await ws.send(json.dumps({
                    "msgId": "1",
                    "verb": "SUBSCRIBE",
                    "path": "/battery/state/changed"
                }))
                
                await ws.send(json.dumps({
                    "msgId": "2",
                    "verb": "SUBSCRIBE",
                    "path": "/devices/state/changed"
                }))
                
                await ws.send(json.dumps({
                    "msgId": "3",
                    "verb": "GET",
                    "path": "/devices/list"
                }))
                
                while True:
                    msg = await ws.recv()
                    data = json.loads(msg)
                    path = data.get("path", "")
                    payload = data.get("payload")
                    
                    if not payload:
                        continue
                        
                    if path == "/devices/state/changed":
                        state = payload.get("state")
                        if state == "active":
                            await ws.send(json.dumps({
                                "msgId": "refresh_list",
                                "verb": "GET",
                                "path": "/devices/list"
                            }))
                            
                    elif path == "/devices/list":
                        device_infos = payload.get("deviceInfos", [])
                        for device in device_infos:
                            dev_id = device.get("id")
                            name = device.get("extendedDisplayName") or device.get("deviceModel") or f"Logitech {dev_id}"
                            if dev_id:
                                hass.data[DOMAIN][entry_id]["device_names"][dev_id] = name
                                
                                await ws.send(json.dumps({
                                    "msgId": f"get_{dev_id}",
                                    "verb": "GET",
                                    "path": f"/battery/{dev_id}/state"
                                }))
                                
                    # Regex angepasst für robustere Erkennung beim Reconnect
                    elif path == "/battery/state/changed" or re.match(r"^/battery/.+/state$", path):
                        device_id = payload.get("deviceId")
                        
                        if device_id:
                            device_name = hass.data[DOMAIN][entry_id]["device_names"].get(device_id, f"Logitech {device_id}")
                            payload["entry_id"] = entry_id
                            payload["device_name"] = device_name
                            
                            async_dispatcher_send(hass, f"{entry_id}_ghub_battery_update", payload)
                            async_dispatcher_send(hass, f"{entry_id}_ghub_battery_{device_id}", payload)
                            
        except asyncio.CancelledError:
            break
        except Exception as e:
            _LOGGER.debug(f"G Hub WS getrennt: {e}. Reconnect in 10 Sekunden...")
            await asyncio.sleep(10)