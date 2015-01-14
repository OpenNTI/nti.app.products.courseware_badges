#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""
from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

from zope import interface
from zope.schema import vocabulary
from zope.interface.interface import taggedValue

from nti.app.client_preferences.interfaces import TAG_EXTERNAL_PREFERENCE_GROUP

from nti.schema.field import Bool

COURSE_COMPLETION = u'completion'
COURSE_BADGE_TYPES = (COURSE_COMPLETION,)
COURSE_BADGE_TYPES_VOCABULARY = \
	vocabulary.SimpleVocabulary([vocabulary.SimpleTerm(_x) for _x in COURSE_BADGE_TYPES])

class ICourseBadgeSettings(interface.Interface):
	"""
	The root of the settings tree for badges
	"""
	taggedValue(TAG_EXTERNAL_PREFERENCE_GROUP, 'write')

	show_course_badges = Bool(title="Enable/disable showing course badges",
							  description="Enable/disable showing course badges",
							  default=False)

class ICourseBadgeCatalog(interface.Interface):

	def iter_badges():
		"""
		Return an iterable of badges for a course
		"""

class ICatalogEntryBadgeCache(interface.Interface):
	"""
	Marker interface for a course badges cache utility
	"""
	
	def get_badge_names(ntiid):
		"""
		return the badge names for the specified catalog entry ntiid
		"""
	
	def is_course_badge(name):
		"""
		return if badge is a course name
		"""