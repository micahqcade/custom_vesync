"""VeSync integration."""

from datetime import timedelta
import logging

from pyvesync.vesync import VeSync

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME, Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .common import async_process_devices
from .const import (
    DOMAIN,
    SERVICE_UPDATE_DEVS,
    VS_BINARY_SENSORS,
    VS_BUTTON,
    VS_DISCOVERY,
    VS_FANS,
    VS_HUMIDIFIERS,
    VS_LIGHTS,
    VS_MANAGER,
    VS_NUMBERS,
    VS_SENSORS,
    VS_SWITCHES,
)

PLATFORMS = {
    Platform.SWITCH: VS_SWITCHES,
    Platform.FAN: VS_FANS,
    Platform.LIGHT: VS_LIGHTS,
    Platform.SENSOR: VS_SENSORS,
    Platform.HUMIDIFIER: VS_HUMIDIFIERS,
    Platform.NUMBER: VS_NUMBERS,
    Platform.BINARY_SENSOR: VS_BINARY_SENSORS,
    Platform.BUTTON: VS_BUTTON,
}

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = cv.removed(DOMAIN, raise_if_present=False)


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Set up Vesync as config entry."""
    username = config_entry.data[CONF_USERNAME]
    password = config_entry.data[CONF_PASSWORD]

    time_zone = str(hass.config.time_zone)

    manager = VeSync(username, password, time_zone)

    login = await hass.async_add_executor_job(manager.login)

    if not login:
        _LOGGER.error("Unable to login to the VeSync server")
        return False

    hass.data[DOMAIN] = {config_entry.entry_id: {}}
    hass.data[DOMAIN][config_entry.entry_id][VS_MANAGER] = manager

    # Create a DataUpdateCoordinator for the manager
    async def async_update_data():
        """Fetch data from API endpoint."""
        try:
            await hass.async_add_executor_job(manager.update)
        except Exception as err:
            raise UpdateFailed(f"Update failed: {err}") from err

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="vesync",
        update_method=async_update_data,
        update_interval=timedelta(seconds=30),
    )

    # Fetch initial data so we have data when entities subscribe
    await coordinator.async_refresh()

    # Store the coordinator instance in hass.data
    hass.data[DOMAIN][config_entry.entry_id]["coordinator"] = coordinator

    device_dict = await async_process_devices(hass, manager)
    platforms_list: list = []

    for p, vs_p in PLATFORMS.items():
        hass.data[DOMAIN][config_entry.entry_id][vs_p] = []
        if device_dict[vs_p]:
            hass.data[DOMAIN][config_entry.entry_id][vs_p].extend(device_dict[vs_p])
            platforms_list.append(p)
    await hass.config_entries.async_forward_entry_setups(config_entry, platforms_list)

    async def async_new_device_discovery(service: ServiceCall) -> None:
        """Discover if new devices should be added."""
        manager = hass.data[DOMAIN][config_entry.entry_id][VS_MANAGER]
        dev_dict = await async_process_devices(hass, manager)

        def _add_new_devices(platform: str) -> None:
            """Add new devices to hass."""
            old_devices = hass.data[DOMAIN][config_entry.entry_id][PLATFORMS[platform]]
            if new_devices := list(
                set(dev_dict.get(VS_SWITCHES, [])).difference(old_devices)
            ):
                old_devices.extend(new_devices)
                if old_devices:
                    async_dispatcher_send(
                        hass, VS_DISCOVERY.format(PLATFORMS[platform]), new_devices
                    )
                else:
                    hass.async_create_task(hass.config_entries.async_forward_entry_setups(config_entry, platform))

        for k in PLATFORMS:
            _add_new_devices(k)

    hass.services.async_register(
        DOMAIN, SERVICE_UPDATE_DEVS, async_new_device_discovery
    )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(
        entry, list(PLATFORMS.keys())
    )
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
