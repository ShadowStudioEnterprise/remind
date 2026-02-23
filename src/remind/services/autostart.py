import sys
import winreg
from remind.brand import INTERNAL_NAME


REG_PATH = r"Software\Microsoft\Windows\CurrentVersion\Run"


def enable_autostart():
    exe_path = sys.executable
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH, 0, winreg.KEY_SET_VALUE) as key:
        winreg.SetValueEx(key, INTERNAL_NAME, 0, winreg.REG_SZ, exe_path)


def disable_autostart():
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH, 0, winreg.KEY_SET_VALUE) as key:
            winreg.DeleteValue(key, INTERNAL_NAME)
    except FileNotFoundError:
        pass