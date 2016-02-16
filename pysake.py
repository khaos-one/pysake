# -*- coding: utf-8 -*-

#
# Pythonic version of automated project builder.
#
# By Egor 'khaos' Zelensky, 2016
# License: public domain
#

import os
import re
import sys
import winreg
import ezwinreg

from enum import Enum

#
# Module variables.
#

_fw_architecture = None
_fw_version = None
_is_64bit = sys.maxsize > 2**32

#
# Types.
#

class FwArchitecture(object):
	x86 = dict(bitness="Framework", build_tools_key="MSBuildToolsPath32")
	x64 = dict(bitness="Framework64", build_tools_key="MSBuildToolsPath")

class FwVersion(object):
	v1_0 = dict(versions=("v1.0.3705",), build_tools_version=None)
	v1_1 = dict(versions=("v1.1.4322",), build_tools_version=None)
	v2_0 = dict(versions=("v2.0.50727",), build_tools_version=None)
	v3_0 = dict(versions=("v2.0.50727",), build_tools_version=None)
	v3_5 = dict(versions=("v3.5", "v2.0.50727"), build_tools_version=None)
	v4_0 = dict(versions=("v4.0.30319",), build_tools_version=None)
	v4_5 = dict(versions=("v4.0.30319",), build_tools_version=None)
	v4_5_1 = dict(versions=("v4.0.30319",), build_tools_version=("14.0", "12.0"))
	v4_5_2 = dict(versions=("v4.0.30319",), build_tools_version=("14.0", "12.0"))
	v4_6 = dict(versions=("v4.0.30319",), build_tools_version=("14.0",))

class ConfigError(Exception):
	pass

#
# Public functions.
#

def use_framework(fw_version, fw_architecture=None):
	global _fw_version, _fw_architecture
	_fw_version = fw_version
	_fw_architecture = fw_architecture

#
# Internal functions.
#

def _get_visualstudio_install_path():
	from distutils.version import StrictVersion
	global _is_64bit
	if _is_64bit:
		path = "HKLM:\\SOFTWARE\\Wow6432Node\\Microsoft\\VisualStudio"
	else:
		path = "HKLM:\\SOFTWARE\\Microsoft\\VisualStudio"
	vsversions = ezwinreg.subkeys(path)
	r = re.compile("^[0-9.]+$")
	vsversions = list(filter(r.match, vsversions))
	vsversions.sort(key=StrictVersion)
	for ver in vsversions[::-1]:
		key = ezwinreg.get("%s\\%s" % (path, ver), "InstallDir")
		if key:
			return key
	return None

def _set_environ():
	global _fw_version, _fw_architecture, _is_64bit
	if not _fw_version:
		raise ConfigError
	if not _fw_architecture:
		_fw_architecture = FwArchitecture.x64 if _is_64bit else FwArchitecture.x86
	include_dirs = list()
	if _fw_version["build_tools_version"]:
		for tools_ver in _fw_version["build_tools_version"]:
			include_dirs.append(ezwinreg.get("HKLM:\\SOFTWARE\\Microsoft\\MSBuild\\ToolsVersions\\%s" % tools_ver, _fw_architecture["build_tools_key"]))
	vsinstalldir = _get_visualstudio_install_path()
	if vsinstalldir:
		include_dirs.append(vsinstalldir)
	for ver in _fw_version["versions"]:
		include_dirs.append("%s\\Microsoft.NET\\%s\\%s" % (os.environ["WINDIR"], _fw_architecture["bitness"], ver))
	for directory in include_dirs:
		if not os.path.exists(directory):
			raise ConfigError
	os.environ["PATH"] = ";".join(include_dirs) + ";" + os.environ["PATH"]


#
# Debug.
#

if __name__ == '__main__':
	use_framework(FwVersion.v4_5, FwArchitecture.x86)
	_set_environ()
