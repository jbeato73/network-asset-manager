# =============================================================================
# asset_manager.py
#
# Author  : Jose M. Beato
# Created : March 9, 2026
# Built with the assistance of Claude (Anthropic) — claude.ai
#
# Description:
#   Manages network device objects with support for maintenance mode,
#   live connectivity checks via HTTP, and inventory reporting. Models
#   a real-world infrastructure pulse check with maintenance window logic
#   — devices in maintenance are skipped during health checks.
#
# Project Setup (run in terminal before opening VS Code):
# ─────────────────────────────────────────────────────
#   1. cd /Users/jmb/PythonProjects
#   2. uv init network-asset-manager
#   3. cd network-asset-manager
#   4. code .
#   5. python3 -m venv .venv
#   6. source .venv/bin/activate
#   7. pip install requests
#   # Create this file as: asset_manager.py
#
# GitHub Commit (after completing):
# ──────────────────────────────────
#   git add asset_manager.py
#   git commit -m "refactor: standardize asset_manager.py header and structure"
#   git push origin main
# =============================================================================

import requests  # Third-party: HTTP connectivity checks


# =============================================================================
# SECTION 1 — DEVICE MODEL
# Best Practice: Use a class to encapsulate device state and behavior.
# This keeps all device-related logic in one place and makes it easy
# to manage a fleet of devices without duplicating code.
# =============================================================================


class NetworkDevice:
    """
    Represents a single managed network device.

    Attributes:
        name           (str):  Device hostname (e.g., "NY-CORE-01").
        ip_address     (str):  Device IP address.
        model          (str):  Hardware model (e.g., "Cisco Nexus").
        api_url        (str):  Optional HTTP endpoint for live health check.
        status         (str):  Current operational status.
        in_maintenance (bool): Whether the device is in a maintenance window.
    """

    def __init__(self, name, ip_address, model, api_url=None):
        self.name           = name
        self.ip_address     = ip_address
        self.model          = model
        self.api_url        = api_url
        self.status         = "OFFLINE"
        self.in_maintenance = False


# =============================================================================
# SECTION 2 — MAINTENANCE MANAGEMENT
# Best Practice: Encapsulate state transitions in dedicated methods so
# the caller never directly mutates object attributes.
# =============================================================================


    def toggle_maintenance(self):
        """
        Toggles the device's maintenance mode on or off.
        Status is updated to reflect the current maintenance state.
        """
        self.in_maintenance = not self.in_maintenance
        self.status = "MAINTENANCE" if self.in_maintenance else "OFFLINE"
        state_label = "ENABLED" if self.in_maintenance else "DISABLED"
        print(f"[INFO] {self.name} — Maintenance Mode: {state_label}")


# =============================================================================
# SECTION 3 — CONNECTIVITY CHECK
# Best Practice: Separate the "skip" decision from the "connect" attempt.
# Maintenance mode is a policy — connectivity is a technical check.
# =============================================================================


    def connect(self):
        """
        Checks if the device is reachable via HTTP.
        Devices in maintenance mode are skipped without a network call.

        If no api_url is set, the device is simulated as online for
        environments where a live endpoint isn't available.
        """
        if self.in_maintenance:
            print(f"[INFO] Skipping {self.name} — device is in Maintenance Mode.")
            return

        if not self.api_url:
            self.status = "SIMULATED-ONLINE"
            print(f"[WARN] {self.name} — No API URL configured. Simulating online.")
            return

        try:
            response = requests.get(self.api_url, timeout=3)
            self.status = (
                "ONLINE" if response.status_code == 200
                else f"ERROR-{response.status_code}"
            )
            print(f"[INFO] {self.name} — Status: {self.status}")
        except requests.exceptions.RequestException:
            self.status = "UNREACHABLE"
            print(f"[WARN] {self.name} — Connection FAILED. Status: UNREACHABLE")


# =============================================================================
# SECTION 4 — INVENTORY REPORTING
# Best Practice: Reporting methods return a formatted string rather than
# printing directly — this makes them reusable in CSV, JSON, or UI output.
# =============================================================================


    def get_info(self):
        """
        Returns a formatted inventory string for this device.

        Returns:
            str: Single-line summary including maintenance state, status, and IP.
        """
        maint_label = "[MAINTENANCE]" if self.in_maintenance else "[ACTIVE]"
        return (
            f"{maint_label}  {self.name:<20} "
            f"Status: {self.status:<20} "
            f"IP: {self.ip_address}"
        )


# =============================================================================
# SECTION 5 — SUMMARY PRINT
# Best Practice: Always print a human-readable summary to the console
# so you know what happened when you run the script.
# =============================================================================


def print_summary(devices):
    """
    Prints a formatted inventory summary for all devices.

    Args:
        devices (list[NetworkDevice]): All managed devices.
    """
    print()
    print("=" * 60)
    print("  NETWORK ASSET MANAGER — INVENTORY REPORT")
    print("  Jose M. Beato | March 9, 2026")
    print("=" * 60)
    for device in devices:
        print(f"  {device.get_info()}")
    print("=" * 60)
    print()


# =============================================================================
# SECTION 6 — MAIN ENTRY POINT
# Best Practice: Always use `if __name__ == "__main__"` to protect your
# main logic. This allows other scripts to import NetworkDevice without
# automatically running the pipeline.
# =============================================================================


def main():
    """
    Orchestrates the full pipeline:
    Setup Devices → Maintenance Window → Pulse Check → Print Summary
    """
    print()
    print("=" * 60)
    print("  asset_manager.py — Starting...")
    print("=" * 60)
    print()

    core_switch = NetworkDevice("NY-CORE-01", "10.0.0.1", "Cisco Nexus")
    api_gateway = NetworkDevice(
        "GLOBAL-GW", "8.8.8.8", "Cloud-Gateway", api_url="https://google.com"
    )

    devices = [core_switch, api_gateway]

    # Simulate a scheduled maintenance window before pulse check
    print("[INFO] --- Scheduled Maintenance Window ---")
    api_gateway.toggle_maintenance()

    print("\n[INFO] --- Running Infrastructure Pulse Check ---")
    for device in devices:
        device.connect()

    print_summary(devices)


if __name__ == "__main__":
    main()

