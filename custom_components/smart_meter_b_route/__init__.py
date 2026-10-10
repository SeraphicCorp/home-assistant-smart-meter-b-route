"""The Smart Meter B Route integration."""

import logging

from momonga import EchonetPropertyCode, Momonga

from homeassistant.const import CONF_DEVICE, CONF_ID, CONF_PASSWORD, Platform
from homeassistant.core import HomeAssistant

from .const import CONF_SUPPORTS_TOTAL_EXPORTED
from .coordinator import BRouteConfigEntry, BRouteUpdateCoordinator

_LOGGER = logging.getLogger(__name__)
PLATFORMS: list[Platform] = [Platform.SENSOR]


def _detect_supports_total_exported(device: str, id: str, password: str) -> bool:
    with Momonga(dev=device, rbid=id, pwd=password) as mo:
        return (
            EchonetPropertyCode.measured_cumulative_energy_reversed
            in mo.get_properties_to_get_values()
        )


async def async_migrate_entry(hass: HomeAssistant, entry: BRouteConfigEntry) -> bool:
    """Migrate old config entries to the current version."""
    if entry.version == 1:
        supports_total_exported = await hass.async_add_executor_job(
            _detect_supports_total_exported,
            entry.data[CONF_DEVICE],
            entry.data[CONF_ID],
            entry.data[CONF_PASSWORD],
        )
        hass.config_entries.async_update_entry(
            entry,
            data={**entry.data, CONF_SUPPORTS_TOTAL_EXPORTED: supports_total_exported},
            version=2,
        )

    return True


async def async_setup_entry(hass: HomeAssistant, entry: BRouteConfigEntry) -> bool:
    """Set up Smart Meter B Route from a config entry."""

    coordinator = BRouteUpdateCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: BRouteConfigEntry) -> bool:
    """Unload a config entry."""
    await hass.async_add_executor_job(entry.runtime_data.api.close)
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
