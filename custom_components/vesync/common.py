"""Common utilities for VeSync Component."""
import logging

from pyvesync.vesyncfan import model_features as fan_model_features
from pyvesync.vesynckitchen import model_features as kitchen_model_features

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.helpers.entity import Entity, ToggleEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    VS_AIRFRYER_TYPES,
    VS_BINARY_SENSORS,
    VS_BUTTON,
    VS_FAN_TYPES,
    VS_FANS,
    VS_HUMIDIFIERS,
    VS_HUMIDIFIERS_TYPES,
    VS_LIGHTS,
    VS_NUMBERS,
    VS_SENSORS,
    VS_SWITCHES,
)

_LOGGER = logging.getLogger(__name__)


def has_feature(device, dictionary, attribute):
    """Return the detail of the attribute."""
    return getattr(device, dictionary, {}).get(attribute, None) is not None


async def async_process_devices(hass, manager):
    """Assign devices to proper component."""
    devices = {
        VS_SWITCHES: [],
        VS_FANS: [],
        VS_LIGHTS: [],
        VS_SENSORS: [],
        VS_HUMIDIFIERS: [],
        VS_NUMBERS: [],
        VS_BINARY_SENSORS: [],
        VS_BUTTON: [],
    }

    redacted = async_redact_data(
        {k: [d.__dict__ for d in v] for k, v in manager._dev_list.items()},
        ["cid", "uuid", "mac_id"],
    )

    _LOGGER.debug(
        "Found the following devices: %s",
        redacted,
    )

    if (
        manager.bulbs is None
        and manager.fans is None
        and manager.kitchen is None
        and manager.outlets is None
        and manager.switches is None
    ):
        _LOGGER.error("Could not find any device to add in %s", redacted)

    if manager.fans:
        for fan in manager.fans:
            # VeSync classifies humidifiers as fans
            if fan_model_features(fan.device_type)["module"] in VS_HUMIDIFIERS_TYPES:
                devices[VS_HUMIDIFIERS].append(fan)
            elif fan_model_features(fan.device_type)["module"] in VS_FAN_TYPES:
                devices[VS_FANS].append(fan)
            else:
                _LOGGER.warning(
                    "Unknown fan type %s %s (enable debug for more info)",
                    fan.device_name,
                    fan.device_type,
                )
                continue
            devices[VS_NUMBERS].append(fan)
            devices[VS_SWITCHES].append(fan)
            devices[VS_SENSORS].append(fan)
            devices[VS_BINARY_SENSORS].append(fan)
            devices[VS_LIGHTS].append(fan)

    if manager.bulbs:
        devices[VS_LIGHTS].extend(manager.bulbs)

    if manager.outlets:
        devices[VS_SWITCHES].extend(manager.outlets)
        # Expose outlets' power & energy usage as separate sensors
        devices[VS_SENSORS].extend(manager.outlets)

    if manager.switches:
        for switch in manager.switches:
            if not switch.is_dimmable():
                devices[VS_SWITCHES].append(switch)
            else:
                devices[VS_LIGHTS].append(switch)

    if manager.kitchen:
        for airfryer in manager.kitchen:
            if (
                kitchen_model_features(airfryer.device_type)["module"]
                in VS_AIRFRYER_TYPES
            ):
                _LOGGER.warning(
                    "Found air fryer %s, support in progress.\n", airfryer.device_name
                )
                devices[VS_SENSORS].append(airfryer)
                devices[VS_BINARY_SENSORS].append(airfryer)
                devices[VS_SWITCHES].append(airfryer)
                devices[VS_BUTTON].append(airfryer)
            else:
                _LOGGER.warning(
                    "Unknown device type %s %s (enable debug for more info)",
                    airfryer.device_name,
                    airfryer.device_type,
                )

    return devices


class VeSyncBaseEntity(CoordinatorEntity, Entity):
    """Base class for VeSync Entity Representations."""

    def __init__(self, device, coordinator) -> None:
        """Initialize the VeSync device."""
        self.device = device
        super().__init__(coordinator, context=device)

    @property
    def base_unique_id(self):
        """Return the ID of this device."""
        if isinstance(self.device.sub_device_no, int):
            return f"{self.device.cid}{str(self.device.sub_device_no)}"
        return self.device.cid

    @property
    def unique_id(self):
        """Return the ID of this device."""
        # The unique_id property may be overridden in subclasses, such as in sensors. Maintaining base_unique_id allows
        # us to group related entities under a single device.
        return self.base_unique_id

    @property
    def base_name(self):
        """Return the name of the device."""
        return self.device.device_name

    @property
    def name(self):
        """Return the name of the entity (may be overridden)."""
        return self.base_name

    @property
    def available(self) -> bool:
        """Return True if device is available."""
        return self.device.connection_status == "online"

    @property
    def device_info(self):
        """Return device information."""
        return {
            "identifiers": {(DOMAIN, self.base_unique_id)},
            "name": self.base_name,
            "model": self.device.device_type,
            "manufacturer": "VeSync",
            "sw_version": self.device.current_firm_version,
        }

    async def async_added_to_hass(self):
        """When entity is added to hass."""
        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_write_ha_state)
        )


class VeSyncDevice(VeSyncBaseEntity, ToggleEntity):
    """Base class for VeSync Device Representations."""

    def __init__(self, device, coordinator) -> None:
        """Initialize the VeSync device."""
        super().__init__(device, coordinator)

    @property
    def is_on(self):
        """Return True if device is on."""
        return self.device.device_status == "on"

    def turn_off(self, **kwargs):
        """Turn the device off."""
        self.device.turn_off()
