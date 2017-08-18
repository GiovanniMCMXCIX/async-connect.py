# -*- coding: utf-8 -*-

"""
Asynchronous Connect API Wrapper
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
A basic wrapper for the Monstercat Connect API.

:copyright: (c) 2016-2017 GiovanniMCMXCIX
:license: MIT, see LICENSE for more details.
"""

__title__ = 'connect'
__author__ = 'GiovanniMCMXCIX'
__license__ = 'MIT'
__copyright__ = 'Copyright 2016-2017 GiovanniMCMXCIX'
__version__ = '0.1.0a0'

from collections import namedtuple

VersionInfo = namedtuple('VersionInfo', 'major minor micro releaselevel serial')

version_info = VersionInfo(major=0, minor=1, micro=0, releaselevel='alpha', serial=0)
