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

from nti.app.products.courseware.interfaces import ICourseCatalogLegacyEntry

from nti.contenttypes.courses.interfaces import ICourseInstance

from nti.dataserver.interfaces import IUser

from nti.externalization.persistence import NoPickle
from nti.externalization.externalization import WithRepr

from nti.schema.schema import EqHash
from nti.schema.field import SchemaConfigured
from nti.schema.fieldproperty import createFieldProperties

from .interfaces import ICourseBadge
from .interfaces import ICourseBadgeMap
from .interfaces import COURSE_COMPLETION
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
		entry = ICourseCatalogLegacyEntry(self.course)
		# TODO: ContentPackageNTIID will be deprecated
		result = get_course_badges(entry.ContentPackageNTIID)
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

@interface.implementer(ICourseBadge)
@WithRepr
@NoPickle
@EqHash('name',)
class CourseBadge(SchemaConfigured):
	createFieldProperties(ICourseBadge)

@interface.implementer(ICourseBadgeMap)
class CourseBadgeMap(dict):

	no_course = object()

	def __init__(self):
		super(CourseBadgeMap, self).__init__()
		self.by_name = {}

	def mark(self, course):
		self.setdefault(course, set())

	def is_no_course(self, course):
		return course == self.no_course

	def mark_no_course(self, badge):
		self.by_name[badge] = self.no_course
		
	def add(self, course, badge, kind=COURSE_COMPLETION):
		self.mark(course)
		self.by_name[badge] = course
		self[course].add(CourseBadge(name=badge, type=kind))

	def get_badge_names(self, course):
		result = self.get(course)
		if result is not None:
			result = [x.name for x in result]
		return result

	def get_course_iden(self, badge):
		result = self.by_name.get(badge)
		return result
