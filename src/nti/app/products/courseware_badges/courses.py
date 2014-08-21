#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""
from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

import datetime

from zope import component
from zope import interface

from pyramid.threadlocal import get_current_request

from nti.app.products.badges.interfaces import IPrincipalErnableBadges
from nti.app.products.badges.interfaces import IPrincipalEarnedBadgeFilter
from nti.app.products.badges.interfaces import IPrincipalEarnableBadgeFilter

from nti.contenttypes.courses.interfaces import ICourseInstance
from nti.contenttypes.courses.interfaces import ICourseSubInstance
from nti.contenttypes.courses.interfaces import ICourseCatalogEntry

from nti.dataserver.interfaces import IUser

from .interfaces import ICourseBadgeCatalog

from . import get_course_badges
from . import show_course_badges
from . import get_course_badges_for_user
from . import get_catalog_entry_for_badge

@interface.implementer(ICourseBadgeCatalog)
class _CourseBadgeCatalog(object):

	def __init__(self, course):
		self.course = ICourseInstance(course)

	def iter_badges(self):
		result = []
		entry = ICourseCatalogEntry(self.course)
		result.extend(get_course_badges(entry.ntiid))
		if not result and ICourseSubInstance.providedBy(self.course):
			# if no badges for subinstance then check main course
			entry = ICourseCatalogEntry(self.course.__parent__.__parent__)
			result.extend(get_course_badges(entry.ntiid))
		# for legacy badges scan the content packages
		if not result:
			for pack in self.course.ContentPackageBundle.ContentPackages:
				result.extend(get_course_badges(pack.ntiid))
		return result

@component.adapter(IUser)
@interface.implementer(IPrincipalErnableBadges)
class _CourseErnableBadges(object):

	def __init__(self, user):
		self.user = user

	def iter_badges(self):
		result = []
		request = get_current_request()
		username = request.authenticated_userid if request else None
		if self.user.username == username:
			result.extend(get_course_badges_for_user(self.user))
		return result

@component.adapter(IUser)
@interface.implementer(IPrincipalEarnedBadgeFilter)
class _CoursePrincipalEarnedBadgeFilter(object):

	def __init__(self, *args):
		pass

	def allow_badge(self, user, badge):
		result = False
		req = get_current_request()
		if req is not None:
			if req.authenticated_userid == user.username:
				result = True
			elif get_catalog_entry_for_badge(badge) is not None and \
				 show_course_badges(user):
				result = True
		return result

@component.adapter(IUser)
@interface.implementer(IPrincipalEarnableBadgeFilter)
class _CoursePrincipalEarnableBadgeFilter(object):

	def __init__(self, *args):
		pass

	def allow_badge(self, user, badge):
		result = True
		entry = get_catalog_entry_for_badge(badge)
		if entry is not None:
			now = datetime.datetime.utcnow()
			result = (entry.StartDate and now >= entry.StartDate) and \
				     (not entry.EndDate or now <= entry.EndDate)
		return result

