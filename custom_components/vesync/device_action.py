"""Provides device actions for Humidifier."""
from __future__ import annotations

import logging

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.components.device_automation import toggle_entity
from homeassistant.const import (
    ATTR_ENTITY_ID,
    ATTR_MODE,
    CONF_DEVICE_ID,
    CONF_DOMAIN,
    CONF_ENTITY_ID,
    CONF_TYPE,
)
from homeassistant.core import Context, HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.entity import get_capability
from homeassistant.helpers.typing import ConfigType, TemplateVarsType

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

# mypy: disallow-any-generics

SET_MODE_SCHEMA = cv.DEVICE_ACTION_BASE_SCHEMA.extend(
    {
        vol.Required(CONF_TYPE): "set_mode",
        vol.Required(CONF_ENTITY_ID): cv.entity_domain("fan"),
        vol.Required(ATTR_MODE): cv.string,
    }
)

ACTION_SCHEMA = vol.Any(SET_MODE_SCHEMA)


async def async_get_actions(
    hass: HomeAssistant, device_id: str
) -> list[dict[str, str]]:
    """List device actions for Humidifier devices."""
    registry = er.async_get(hass)
    actions = await toggle_entity.async_get_actions(hass, device_id, DOMAIN)

    # Get all the integrations entities for this device
    for entry in er.async_entries_for_device(registry, device_id):
        if entry.domain != "fan":
            continue

        base_action = {
            CONF_DEVICE_ID: device_id,
            CONF_DOMAIN: DOMAIN,
            CONF_ENTITY_ID: entry.entity_id,
        }

        actions.append({**base_action, CONF_TYPE: "set_mode"})

    return actions


async def async_call_action_from_config(
    hass: HomeAssistant,
    config: ConfigType,
    variables: TemplateVarsType,
    context: Context | None,
) -> None:
    """Execute a device action."""
    service_data = {ATTR_ENTITY_ID: config[CONF_ENTITY_ID]}

    if config[CONF_TYPE] != "set_mode":
        return await toggle_entity.async_call_action_from_config(
            hass, config, variables, context, DOMAIN
        )

    service = "set_preset_mode"
    service_data["preset_mode"] = config[ATTR_MODE]
    await hass.services.async_call(
        "fan", service, service_data, blocking=True, context=context
    )


async def async_get_action_capabilities(
    hass: HomeAssistant, config: ConfigType
) -> dict[str, vol.Schema]:
    """List action capabilities."""
    action_type = config[CONF_TYPE]

    if action_type != "set_mode":
        return {}

    try:
        available_modes = (
            get_capability(hass, config[ATTR_ENTITY_ID], "preset_modes") or []
        )
    except HomeAssistantError:
        available_modes = []
    fields = {vol.Required(ATTR_MODE): vol.In(available_modes)}
    return {"extra_fields": vol.Schema(fields)}
