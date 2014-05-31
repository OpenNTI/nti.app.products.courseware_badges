#!/usr/bin/env python
# -*- coding: utf-8 -*
"""
.. $Id$
"""
from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

import os
import re

from zope import component

from zope.security.interfaces import IParticipation
from zope.security.management import endInteraction
from zope.security.management import newInteraction
from zope.security.management import restoreInteraction

from zope.preference.interfaces import IPreferenceGroup

import repoze.lru

from nti.badges.openbadges import interfaces as open_interfaces

from nti.contenttypes.courses.interfaces import ICourseInstance

from nti.app.products.badges import BADGES
from nti.app.products.badges import get_badge
from nti.app.products.badges import get_all_badges
from nti.app.products.badges import assertion_exists

from nti.app.products.courseware.interfaces import IPrincipalEnrollmentCatalog

from nti.ntiids import ntiids

from . import interfaces

VIEW_BADGES = BADGES
VIEW_EARNED_COURSE_BADGES = u'EarnedCourseBadges'

course_completion_badge = u'course_completion_badge'
course_badge_types = (course_completion_badge,)

def base_root_ntiid(ntiid):
	"""
	return the 'root' ntiid of a source ntiid. That is, we remove from the NTIID-source
	specific part anything after the first period (.)  so from
	tag:nextthought.com,2011-10:OU-HTML-CLC3403_LawAndJustice.clc_3403_law_and_justice
	we get tag:nextthought.com,2011-10:OU-HTML-CLC3403_LawAndJustice
	"""
	parts = ntiids.get_parts(ntiid)
	specfic = parts.specific.split('.')[0]
	result = ntiids.make_ntiid(provider=parts.provider,
							   nttype=parts.nttype,
							   specific=specfic,
							   base=parts.date)
	return result

def get_image_filename(badge):
	image = open_interfaces.IBadgeClass(badge).image
	filename = os.path.basename(image)
	filename = os.path.splitext(filename)[0] if filename else None
	return filename

badge_pattern = re.compile(".+\.course_.+_badge$", re.I | re.U)
def is_course_badge(badge):
	filename = get_image_filename(badge)
	result = badge_pattern.match(filename) if filename else None
	return True if result else False

@repoze.lru.lru_cache(1000)
def get_course_badge_names(course_ntiid, badge_types=course_badge_types):
	"""
	return all the course badges.

	The image file name of a course badge is 'root' course NTIID plus a period (.) plus course_{type}_badge
	e.g tag_nextthought.com_2011-10_OU-HTML-CLC3403_LawAndJustice.course_completion_badge.png
	that is the completion badge of the tag:nextthought.com,2011-10:OU-HTML-CLC3403_LawAndJustice
 	course
 	"""

	badge_type_ntiids = set()
	parts = ntiids.get_parts(course_ntiid)
	pre_specfic = '.'.join(parts.specific.split('.')[0:-1]) or parts.specific
	for subtype in badge_types:
		specfic = '%s.%s' % (pre_specfic, subtype)
		name = ntiids.make_ntiid(provider=parts.provider,
								 nttype=parts.nttype,
								 specific=specfic,
								 base=parts.date)
		badge_type_ntiids.add(name.replace(':', '_').replace(',', '_'))

	result = []
	for badge in get_all_badges():
		image = open_interfaces.IBadgeClass(badge).image
		filename = os.path.basename(image)
		possible_ntiid = os.path.splitext(filename)[0] if filename else None
		if possible_ntiid in badge_type_ntiids:
			result.append(badge.name)
	return result

def get_course_badges(course_ntiid, badge_types=course_badge_types):
	result = []
	names = get_course_badge_names(course_ntiid, badge_types)
	for name in names:
		badge = get_badge(name)
		if badge is not None:
			result.append(badge)
	return result

def show_course_badges(user):
	prefs = component.getUtility(IPreferenceGroup, name='Badges.Course')
	endInteraction()
	try:
		newInteraction(IParticipation(user))
		return prefs.show_course_badges
	finally:
		restoreInteraction()

def get_universe_of_course_badges_for_user(user):
	"""
	return the badges for the courses a user in enrolled in
	"""
	result = []
	for catalog in component.subscribers((user,), IPrincipalEnrollmentCatalog):
		for course in catalog.iter_enrollments():
			course = ICourseInstance(course)
			adapted = interfaces.ICourseBadgeCatalog(course)
			result.append((course, list(adapted.iter_badges())))
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

