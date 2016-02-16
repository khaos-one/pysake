#
# Easy Windows registry access.
#
# By Egor 'khaos' Zelensky, 2016.
# License: MIT.
#
# Key access format: HKLM:\SOFTWARE\Microsoft...
#

import re
import winreg

_tome_map = {
		"HKCR": winreg.HKEY_CLASSES_ROOT,
		"HKEY_CLASSES_ROOT": winreg.HKEY_CLASSES_ROOT,
		"HKCU": winreg.HKEY_CURRENT_USER,
		"HKEY_CURRENT_USER": winreg.HKEY_CURRENT_USER,
		"HKLM": winreg.HKEY_LOCAL_MACHINE,
		"HKEY_LOCAL_MACHINE": winreg.HKEY_LOCAL_MACHINE,
		"HKU": winreg.HKEY_USERS,
		"HKEY_USERS": winreg.HKEY_USERS,
		"HKPD": winreg.HKEY_PERFORMANCE_DATA,
		"HKEY_PERFORMANCE_DATA": winreg.HKEY_PERFORMANCE_DATA,
		"HKCC": winreg.HKEY_CURRENT_CONFIG,
		"HKEY_CURRENT_CONFIG": winreg.HKEY_CURRENT_CONFIG,
		"HKDD": winreg.HKEY_DYN_DATA,
		"HKEY_DYN_DATA": winreg.HKEY_DYN_DATA
	}

def _split(path):
	global _tome_map
	m = re.search(r"([\w_]+):\\(.+)", path, re.IGNORECASE | re.DOTALL)
	if not m:
		return None, None
	return _tome_map.get(m.group(1), None), m.group(2)

def get(path, key):
	tome, path = _split(path)
	if not tome:
		return None
	try:
		with winreg.OpenKey(tome, path) as regkey:
			return winreg.QueryValueEx(regkey, key)[0]
	except:
		return None

def subkeys(path):
	tome, path = _split(path)
	if not tome:
		return None
	result = list()
	try:
		with winreg.OpenKey(tome, path) as regkey:
			try:
				i = 0
				while True:
					result.append(winreg.EnumKey(regkey, i))
					i += 1
			except:
				pass
	except:
		return None
	return result