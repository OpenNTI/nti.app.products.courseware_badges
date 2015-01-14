#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

import gevent

from zope import component

from nti.dataserver.interfaces import IDataserverTransactionRunner

from nti.processlifetime import IApplicationTransactionOpenedEvent

from .interfaces import ICatalogEntryBadgeCache

@component.adapter(IApplicationTransactionOpenedEvent)
def _after_database_opened_listener(event):

	def build_cache():
		manager = component.getUtility(ICatalogEntryBadgeCache)
		manager.build()
	
	def build_catalog_entry_badge_cache():
		logger.info("Building catalog entry badge cache")
		transaction_runner = component.getUtility(IDataserverTransactionRunner)
		transaction_runner(build_cache)
	gevent.spawn(build_catalog_entry_badge_cache)
