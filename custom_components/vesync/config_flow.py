"""Config flow utilities."""
import logging
from collections import OrderedDict

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.components import dhcp
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from pyvesync.vesync import VeSync

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class VeSyncFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow."""

    VERSION = 1

    def __init__(self) -> None:
        """Instantiate config flow."""
        self._username = None
        self._password = None
        self.data_schema = OrderedDict()
        self.data_schema[vol.Required(CONF_USERNAME)] = str
        self.data_schema[vol.Required(CONF_PASSWORD)] = str

    @callback
    def _show_form(self, errors=None):
        """Show form to the user."""
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(self.data_schema),
            errors=errors or {},
        )

    async def async_step_user(self, user_input=None):
        """Handle a flow start."""
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        if not user_input:
            return self._show_form()

        self._username = user_input[CONF_USERNAME]
        self._password = user_input[CONF_PASSWORD]

        manager = VeSync(self._username, self._password)
        login = await self.hass.async_add_executor_job(manager.login)
        await self.async_set_unique_id(f"{self._username}-{manager.account_id}")
        self._abort_if_unique_id_configured()

        return (
            self.async_create_entry(
                title=self._username,
                data={
                    CONF_USERNAME: self._username,
                    CONF_PASSWORD: self._password,
                },
            )
            if login
            else self._show_form(errors={"base": "invalid_auth"})
        )

    async def async_step_dhcp(self, discovery_info: dhcp.DhcpServiceInfo) -> FlowResult:
        """Handle DHCP discovery."""
        hostname = discovery_info.hostname

        _LOGGER.debug("DHCP discovery detected device %s", hostname)
        self.context["title_placeholders"] = {"gateway_id": hostname}
        return await self.async_step_user()
