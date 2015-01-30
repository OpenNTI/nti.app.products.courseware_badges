#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from zope import component

from nti.contenttypes.courses.interfaces import CourseInstanceAvailableEvent

from .interfaces import ICatalogEntryBadgeCache

@component.adapter(CourseInstanceAvailableEvent)
def _course_instance_available(event):
	cache = component.getUtility(ICatalogEntryBadgeCache)
	cache.build(event.object)
