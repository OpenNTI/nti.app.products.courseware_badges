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

from nti.contenttypes.courses.interfaces import ICourseInstance
from nti.contenttypes.courses.interfaces import ICourseInstanceAvailableEvent

from .interfaces import ICatalogEntryBadgeCache

@component.adapter(ICourseInstanceAvailableEvent)
def _course_instance_available(event):
	cache = component.getUtility(ICatalogEntryBadgeCache)
	cache.build(event.object)

@component.adapter(ICourseInstance, IObjectAddedEvent)
def _on_course_instance_added(course, event):
	cache = component.getUtility(ICatalogEntryBadgeCache)
	cache.build(course)
