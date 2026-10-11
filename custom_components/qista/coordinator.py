"""DataUpdateCoordinator for modern Qista cloud integration."""
from __future__ import annotations

from datetime import timedelta
import logging
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import QistaApiClient, QistaAuthError, QistaConnectionError
from .const import DEFAULT_SCAN_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)


class QistaDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Manage fetching Qista trap data from GraphQL API."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: QistaApiClient,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )
        self.client = client

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch all traps and their status."""
        try:
            bams = await self.client.get_bams()
            data: dict[str, Any] = {"devices": {}}

            for bam in bams:
                bam_id = bam.get("id")
                if not bam_id:
                    continue

                name = (
                    bam.get("externalCustomName")
                    or bam.get("internalCustomName")
                    or bam.get("reference")
                    or f"Borne {bam_id}"
                )

                consumables = bam.get("consumablesRemaining") or {}
                bait_data = consumables.get("bait") or {}
                co2_data = consumables.get("co2") or {}

                data["devices"][str(bam_id)] = {
                    "id": bam_id,
                    "reference": bam.get("reference"),
                    "name": name,
                    "type": bam.get("type", "Borne anti-moustique"),
                    "working_status": bam.get("workingStatus", "unknown"),
                    "operating_status": bam.get("operatingStatus", "unknown"),
                    "sim_status": bam.get("simStatus"),
                    "is_connected": bam.get("isConnected", True),
                    "lat": bam.get("lat"),
                    "lng": bam.get("lng"),
                    "mosquitoe_catch_day": bam.get("mosquitoeCatchDay", 0),
                    "mosquitoe_catch_week": bam.get("mosquitoeCatchWeek", 0),
                    "mosquitoe_catch_total": bam.get("mosquitoeCatchTotal", 0),
                    "bait_remaining_days": bait_data.get("days"),
                    "co2_remaining_days": co2_data.get("days"),
                    "loaded_co2_bottle_label": bam.get("loadedCo2BottleLabel"),
                }

            return data

        except QistaAuthError as err:
            raise UpdateFailed(f"Authentication error: {err}") from err
        except QistaConnectionError as err:
            raise UpdateFailed(f"Error communicating with Qista API: {err}") from err
        except Exception as err:
            _LOGGER.exception("Unexpected error fetching Qista data: %s", err)
            raise UpdateFailed(f"Unexpected error: {err}") from err
