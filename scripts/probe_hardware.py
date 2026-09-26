"""Probe this laptop's hardware and write the facts to docs/hardware.md (task 0.2).

Run with: uv run python scripts/probe_hardware.py
It replaces only its own section of docs/hardware.md, so sections that later scripts
append (local model speed, audio devices) survive a rerun.
"""

import json
import re
import shutil
import subprocess
import winreg
from datetime import date

from hardware_doc import HARDWARE_DOC, write_section

from ariel.config import REPO_ROOT

GB = 1024**3

WINDOWS_KEY = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion"
DISPLAY_ADAPTERS_KEY = (
    r"SYSTEM\CurrentControlSet\Control\Class\{4d36e968-e325-11ce-bfc1-08002be10318}"
)

# One PowerShell call returns the WMI facts as JSON, each key holding a list of instances.
# The leading comma stops PowerShell unrolling one-element lists.
CIM_QUERY = """
[Console]::OutputEncoding = [Text.Encoding]::UTF8
function Get-Facts($class, $properties) {
  return ,@(Get-CimInstance $class | Select-Object -Property $properties)
}
@{
  os  = Get-Facts Win32_OperatingSystem Caption, OSArchitecture
  cs  = Get-Facts Win32_ComputerSystem Manufacturer, Model, TotalPhysicalMemory
  cpu = Get-Facts Win32_Processor Name, NumberOfCores, NumberOfLogicalProcessors
  ram = Get-Facts Win32_PhysicalMemory Capacity
  gpu = Get-Facts Win32_VideoController Name, DriverVersion
} | ConvertTo-Json -Depth 3 -Compress
"""


def run(args: list[str]) -> str:
    """Run a command and return its standard output."""
    result = subprocess.run(
        args, capture_output=True, encoding="utf-8", errors="replace", check=True, timeout=60
    )
    return result.stdout


def windows_facts() -> dict[str, list[dict]]:
    """OS, machine, CPU, memory and GPU facts from WMI."""
    out = run(["powershell", "-NoProfile", "-NonInteractive", "-Command", CIM_QUERY])
    return json.loads(out.lstrip("﻿"))


def registry_value(key: str, name: str) -> object:
    """A value under HKEY_LOCAL_MACHINE, or None if the key or value is missing."""
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key) as handle:
            return winreg.QueryValueEx(handle, name)[0]
    except OSError:
        return None


def dedicated_vram_gb() -> dict[str, float]:
    """Dedicated video memory per display adapter, from its driver's registry key.

    Integrated graphics have no such value, because they share system RAM.
    """
    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, DISPLAY_ADAPTERS_KEY) as adapters:
        subkeys = [winreg.EnumKey(adapters, i) for i in range(winreg.QueryInfoKey(adapters)[0])]
    sizes: dict[str, float] = {}
    for subkey in filter(str.isdigit, subkeys):
        key = rf"{DISPLAY_ADAPTERS_KEY}\{subkey}"
        name = registry_value(key, "DriverDesc")
        size = registry_value(key, "HardwareInformation.qwMemorySize")
        if isinstance(name, str) and isinstance(size, int):
            sizes[name] = size / GB
    return sizes


def cuda_status() -> str:
    """Whether CUDA is usable, judged by nvidia-smi."""
    exe = shutil.which("nvidia-smi")
    if exe is None:
        return "not available (nvidia-smi not found)"
    try:
        header = run([exe])
        rows = run([exe, "--query-gpu=name,memory.total", "--format=csv,noheader,nounits"])
        cards = []
        for row in rows.strip().splitlines():
            name, mib = row.rsplit(",", 1)
            cards.append(f"{name.strip()} with {int(mib) / 1024:.1f} GB VRAM")
    except (OSError, subprocess.SubprocessError, ValueError) as exc:
        return f"not available (nvidia-smi failed: {exc})"
    version = re.search(r"CUDA Version:\s*([\d.]+)", header)
    cuda = f"CUDA {version.group(1)}" if version else "CUDA version unknown"
    return f"available, {cuda}: " + "; ".join(cards)


def machine_section() -> str:
    """The Markdown body of this script's section of docs/hardware.md."""
    facts = windows_facts()
    os_info, system, cpu = facts["os"][0], facts["cs"][0], facts["cpu"][0]
    version = registry_value(WINDOWS_KEY, "DisplayVersion")
    build = f"{registry_value(WINDOWS_KEY, 'CurrentBuild')}.{registry_value(WINDOWS_KEY, 'UBR')}"
    installed_gb = sum(stick["Capacity"] for stick in facts["ram"]) / GB
    usable_gb = system["TotalPhysicalMemory"] / GB
    vram = dedicated_vram_gb()
    disk = shutil.disk_usage(REPO_ROOT)

    windows = os_info["Caption"].removeprefix("Microsoft ")
    rows = [
        ("Machine", f"{system['Manufacturer']} {system['Model']}"),
        ("Windows", f"{windows}, version {version}, build {build}, {os_info['OSArchitecture']}"),
        (
            "CPU",
            f"{cpu['Name'].strip()}: {cpu['NumberOfCores']} cores, "
            f"{cpu['NumberOfLogicalProcessors']} threads",
        ),
        ("RAM", f"{installed_gb:.1f} GB installed, {usable_gb:.1f} GB usable"),
    ]
    for gpu in facts["gpu"]:
        if gpu["Name"] in vram:
            memory = f"{vram[gpu['Name']]:.1f} GB dedicated VRAM"
        else:
            memory = "no dedicated VRAM, shares system RAM"
        rows.append(("GPU", f"{gpu['Name']} (driver {gpu['DriverVersion']}): {memory}"))
    rows.append(("CUDA", cuda_status()))
    rows.append(
        (f"Free disk ({REPO_ROOT.drive})", f"{disk.free / GB:.1f} GB of {disk.total / GB:.1f} GB")
    )

    table = "\n".join(f"| {item} | {value} |" for item, value in rows)
    return (
        "## Machine\n\n"
        f"Probed on {date.today().isoformat()} by `scripts/probe_hardware.py`. "
        "Rerun it after a hardware or driver change.\n"
        "Model sizes chosen from these facts are in `docs/adr/0002-model-sizes.md`.\n\n"
        f"| Item | Value |\n|---|---|\n{table}\n"
    )


if __name__ == "__main__":
    body = machine_section()
    write_section("probe_hardware.py", body)
    print(body)
    print(f"Written to {HARDWARE_DOC}")
