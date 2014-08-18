#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""
from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from zope import component

from zope.security.interfaces import IParticipation
from zope.security.management import endInteraction
from zope.security.management import newInteraction
from zope.security.management import restoreInteraction

from zope.preference.interfaces import IPreferenceGroup

from nti.contenttypes.courses.interfaces import ICourseCatalogEntry

from nti.contenttypes.courses.interfaces import ICourseInstance

from nti.app.products.badges import BADGES
from nti.app.products.badges import get_badge
from nti.app.products.badges import get_all_badges
from nti.app.products.badges import assertion_exists

from nti.app.products.courseware.interfaces import IPrincipalEnrollmentCatalog

from .utils import get_badge_type 
from .utils import find_course_badges_from_badges

from .interfaces import ICourseBadgeCatalog

VIEW_BADGES = BADGES
VIEW_EARNED_COURSE_BADGES = u'EarnedCourseBadges'

def show_course_badges(user):
	prefs = component.getUtility(IPreferenceGroup, name='Badges.Course')
	endInteraction()
	try:
		newInteraction(IParticipation(user))
		return prefs.show_course_badges
	finally:
		restoreInteraction()

def get_course_badges(course_iden):
	result = find_course_badges_from_badges(course_iden, get_all_badges())
	return result

def get_universe_of_course_badges_for_user(user):
	"""
	return the badges for the courses a user in enrolled in
	"""
	result = []
	for catalog in component.subscribers((user,), IPrincipalEnrollmentCatalog):
		for course in catalog.iter_enrollments():
			course = ICourseInstance(course)
			adapted = ICourseBadgeCatalog(course)
			result.append((course, adapted.iter_badges()))
	return result

def get_course_badges_for_user(user):
	"""
	return the badges for the courses a user in enrolled in
	"""
	result = []
	for _, badges in get_universe_of_course_badges_for_user(user):
		result.extend(badges)
	return result

def get_earned_course_badges(user):
	"""
	return the earned course badges for a user
	"""
	result = []
	for badge in get_course_badges_for_user(user):
		if assertion_exists(user, badge):
			result.append(badge)
	return result

def get_catalog_entry_for_badge(badge):
	entry = ICourseCatalogEntry(badge, None)
	return entry
