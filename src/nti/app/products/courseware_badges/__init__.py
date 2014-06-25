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

import repoze.lru

from nti.app.products.courseware.interfaces import ICourseCatalogEntry

from nti.contenttypes.courses.interfaces import ICourseInstance

from nti.app.products.badges import BADGES
from nti.app.products.badges import get_badge
from nti.app.products.badges import get_all_badges
from nti.app.products.badges import assertion_exists

from nti.app.products.courseware.interfaces import IPrincipalEnrollmentCatalog

from . import utils
from . import interfaces

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
	result = []
	badge_map = component.getUtility(interfaces.ICourseBadgeMap)
	names = badge_map.get_badge_names(course_iden)
	if names is None:
		badges = utils.find_course_badges_from_badges(course_iden, get_all_badges())
		# populate course badge map
		for badge in badges:
			result.append(badge)
			kind = utils.get_badge_type(badge)
			badge_map.add(course_iden, badge.name, kind)
		# mark in case no badge is found
		badge_map.mark(course_iden)
	else:
		for name in names:
			badge = get_badge(name)
			if badge is not None:
				result.append(badge)
	return result

def get_universe_of_course_badges_for_user(user):
	"""
	return the badges for the courses a user in enrolled in
	"""
	result = []
	for catalog in component.subscribers((user,), IPrincipalEnrollmentCatalog):
		for course in catalog.iter_enrollments():
			course = ICourseInstance(course)
			adapted = interfaces.ICourseBadgeCatalog(course)
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
