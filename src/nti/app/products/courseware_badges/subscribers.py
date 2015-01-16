#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from zope import component

from nti.processlifetime import IApplicationTransactionOpenedEvent

from .interfaces import ICatalogEntryBadgeCache

@component.adapter(IApplicationTransactionOpenedEvent)
def _after_database_opened_listener(event):
	manager = component.getUtility(ICatalogEntryBadgeCache)
	manager.build()
	