import os
import platform
import socket
import urllib.request


def get_system_info():

    info = {
        "os": "Unknown",
        "version": "Unknown",
        "kernel": platform.release(),
        "architecture": platform.machine(),
        "hostname": socket.gethostname(),
        "cpu": os.cpu_count(),
        "ram": "Unknown",
        "root": os.geteuid() == 0,
        "ip": get_public_ip(),
    }

    try:
        with open("/etc/os-release") as f:
            data = {}

            for line in f:
                if "=" in line:
                    key, value = line.strip().split("=", 1)
                    data[key] = value.strip('"')

            info["os"] = data.get("ID", "Unknown")
            info["version"] = data.get("VERSION_ID", "Unknown")

    except Exception:
        pass

    try:
        with open("/proc/meminfo") as f:
            for line in f:
                if line.startswith("MemTotal"):
                    ram = int(line.split()[1])
                    info["ram"] = f"{round(ram / 1024 / 1024, 2)} GB"
                    break

    except Exception:
        pass

    return info


def get_public_ip():

    try:
        with urllib.request.urlopen(
            "https://api.ipify.org",
            timeout=3
        ) as response:
            return response.read().decode()

    except Exception:
        return "Unavailable"