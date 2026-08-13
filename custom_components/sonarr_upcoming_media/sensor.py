from typing import Any, Dict, Optional
from collections.abc import Callable

from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.components.sensor import SensorEntity
from homeassistant.const import (
    CONF_API_KEY, 
    CONF_NAME, 
    )

from .const import DOMAIN
from .coordinator import SonarrDataCoordinator

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: Callable,
) -> None:
    coordinator: SonarrDataCoordinator = hass.data[DOMAIN][config_entry.entry_id]

    async_add_entities(
        [
            SonarrUpcomingMediaSensor(coordinator, config_entry),
            SonarrWantedMediaSensor(coordinator, config_entry),
        ],
        update_before_add=True,
    )

class SonarrMediaSensor(CoordinatorEntity[SonarrDataCoordinator], SensorEntity):
    def __init__(
        self,
        coordinator: SonarrDataCoordinator,
        config_entry: ConfigEntry,
        sensor_type: str,
        type_name: str,
    ):
        super().__init__(coordinator)
        self._coordinator = coordinator
        self._sensor_type = sensor_type
        prefix = f'{config_entry.data[CONF_NAME].capitalize()} ' if len(config_entry.data[CONF_NAME]) > 0 else ''
        self._name = f'{prefix}Sonarr {type_name} Media'
        self._api_key = config_entry.data[CONF_API_KEY]
        self._unique_id = f'{self._api_key}_Sonarr_{type_name}_Media'

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return self._name

    @property
    def unique_id(self) -> str:
        """Return the unique ID of the sensor."""
        return self._unique_id

    @property
    def state(self) -> Optional[str]:
        """Return the value of the sensor."""
        return "Online" if self._coordinator.data and self._coordinator.data.get('online', False) else "Offline"

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        if not self._coordinator.data:
            return {}
        return self._coordinator.data.get(self._sensor_type, self._coordinator.data.get('data', {}))

class SonarrUpcomingMediaSensor(SonarrMediaSensor):
    def __init__(self, coordinator: SonarrDataCoordinator, config_entry: ConfigEntry):
        super().__init__(coordinator, config_entry, "upcoming", "Upcoming")

class SonarrWantedMediaSensor(SonarrMediaSensor):
    def __init__(self, coordinator: SonarrDataCoordinator, config_entry: ConfigEntry):
        super().__init__(coordinator, config_entry, "wanted", "Wanted")