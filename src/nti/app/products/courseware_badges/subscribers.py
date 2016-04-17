#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from zope import component

from zope.lifecycleevent.interfaces import IObjectAddedEvent
from zope.lifecycleevent.interfaces import IObjectRemovedEvent

from nti.app.products.courseware_badges.interfaces import ICatalogEntryBadgeCache

from nti.contenttypes.courses.interfaces import ICourseInstance
from nti.contenttypes.courses.interfaces import	ICourseCatalogEntry
from nti.contenttypes.courses.interfaces import ICourseInstanceImportedEvent
from nti.contenttypes.courses.interfaces import ICourseInstanceAvailableEvent

@component.adapter(ICourseInstance, ICourseInstanceAvailableEvent)
def _course_instance_available(course, event):
	cache = component.getUtility(ICatalogEntryBadgeCache)
	cache.build(course)

@component.adapter(ICourseInstance, ICourseInstanceImportedEvent)
def _course_instance_imported(course, event):
	cache = component.getUtility(ICatalogEntryBadgeCache)
	cache.build(course)

@component.adapter(ICourseInstance, IObjectAddedEvent)
def _on_course_instance_added(course, event):
	cache = component.getUtility(ICatalogEntryBadgeCache)
	cache.build(course)

@component.adapter(ICourseInstance, IObjectRemovedEvent)
def _on_course_instance_removed(course, event):
	cache = component.getUtility(ICatalogEntryBadgeCache)
	entry = ICourseCatalogEntry(course, None)
	if entry is not None and entry.ntiid in cache:
		del cache[entry.ntiid]
