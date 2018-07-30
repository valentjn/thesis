# -*- coding: utf-8 -*-

"""
remotely
~~~~~~~~

:copyright: (c) 2012 by Kefei Dan Zhou, (c) 2018 by Julian Valentin
:license: ISC, see LICENSE for more details.

"""

__title__ = 'remotely'
__version__ = '0.3.0'
__author__ = 'Kefei Dan Zhou'
__copyright__ = ('Copyright 2012 Kefei Dan Zhou, '
                 'Copyright 2018 Julian Valentin')


from .remotely import remotely
from .remotely import RemoteClient
from .remotely_server import create_remotely_server
from .remotely_server import RemotelyException
