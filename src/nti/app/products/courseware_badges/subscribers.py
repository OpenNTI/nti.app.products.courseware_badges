#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from zope import component

from nti.contentlibrary.interfaces import IAllContentPackageLibrariesDidSyncEvent
from nti.contentlibrary.interfaces import IAllContentPackageLibrariesWillSyncEvent

from nti.contenttypes.courses.interfaces import CourseInstanceAvailableEvent

from .interfaces import ICatalogEntryBadgeCache

@component.adapter(CourseInstanceAvailableEvent)
def _course_instance_available(event):
	cache = component.getUtility(ICatalogEntryBadgeCache)
	## we only want to update this cache is we are synchronizing
	if getattr(cache, '_v_synchronizing', False):
		cache.build(event.object)

@component.adapter(IAllContentPackageLibrariesWillSyncEvent)
def _libraries_will_sync_event(event):
	cache = component.getUtility(ICatalogEntryBadgeCache)
	cache._v_synchronizing = True

@component.adapter(IAllContentPackageLibrariesDidSyncEvent)
def _libraries_did_sync_event(event):
	cache = component.getUtility(ICatalogEntryBadgeCache)
	cache._v_synchronizing = False
