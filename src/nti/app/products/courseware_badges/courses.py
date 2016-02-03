#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

import datetime
from collections import defaultdict

from zope import component
from zope import interface

from zope.container.contained import Contained

from pyramid.threadlocal import get_current_request

from nti.app.products.badges import get_badge

from nti.app.products.badges.interfaces import IOpenBadgeAdapter
from nti.app.products.badges.interfaces import IPrincipalErnableBadges
from nti.app.products.badges.interfaces import IPrincipalEarnedBadgeFilter
from nti.app.products.badges.interfaces import IPrincipalEarnableBadgeFilter

from nti.app.products.courseware_badges import get_all_badges
from nti.app.products.courseware_badges import show_course_badges
from nti.app.products.courseware_badges import get_course_badges_for_user

from nti.app.products.courseware_badges.interfaces import ICourseBadgeCatalog
from nti.app.products.courseware_badges.interfaces import ICatalogEntryBadgeCache

from nti.app.products.courseware_badges.utils import proxy
from nti.app.products.courseware_badges.utils import catalog_entry
from nti.app.products.courseware_badges.utils import find_catalog_entry
from nti.app.products.courseware_badges.utils import find_course_badges_from_badges

from nti.badges.openbadges.interfaces import IBadgeClass

from nti.common.property import Lazy
from nti.common.property import CachedProperty

from nti.contenttypes.courses.interfaces import ICourseInstance
from nti.contenttypes.courses.interfaces import ICourseSubInstance
from nti.contenttypes.courses.interfaces import ICourseCatalogEntry

from nti.contenttypes.courses.utils import get_course_packages

from nti.dataserver.dicts import LastModifiedDict

from nti.dataserver.interfaces import IUser

def get_course_badges(course_iden):
	# CS: We want to make sure we always query the badges from the DB
	# in order to return new objects all the time, so they can be
	# proxied appropriately for the course in case multiple courses
	# shared a badge
	result = find_course_badges_from_badges(course_iden, get_all_badges())
	return result

def entry_ntiid(context):
	entry = catalog_entry(context)
	result = entry.ntiid if entry is not None else None
	return result

def get_all_context_badges(context):
	result = []
	entry = catalog_entry(context)
	course = ICourseInstance(context, None)
	if entry is not None:
		result.extend(get_course_badges(entry.ntiid))
	if not result and ICourseSubInstance.providedBy(course):
		# if no badges for subinstance then check main course
		entry = ICourseCatalogEntry(course.__parent__.__parent__, None)
		if entry is not None:
			result.extend(get_course_badges(entry.ntiid))
	# for legacy badges scan the content packages
	if not result and course is not None:
		for pack in get_course_packages(course):
			result.extend(get_course_badges(pack.ntiid))
	return result

@interface.implementer(ICatalogEntryBadgeCache)
class _CatalogEntryBadgeCache(LastModifiedDict, Contained):

	@property
	def Items(self):
		result = {}
		for k, v in self.items():
			result[k] = list(v)
		return result

	@classmethod
	def get_course_badge_names(cls, context):
		badges = get_all_context_badges(context)
		result = tuple(sorted([b.name for b in badges]))
		return result

	@CachedProperty("lastModified")
	def _rev_map(self):
		result = defaultdict(set)
		for ntiid, names in self.items():
			for name in names or ():
				result[name].add(ntiid)
		return result

	def build(self, context):
		entry = ICourseCatalogEntry(context, None)
		if entry is not None:
			ntiid = entry_ntiid(entry)
			old_names = self.get(ntiid) or ()
			names = self.get_course_badge_names(entry)
			if old_names != names:
				self[ntiid] = names
				return True
		return False

	def get_badge_names(self, ntiid):
		result = self.get(ntiid) or ()
		return result

	def get_badge_catalog_entry_ntiids(self, name):
		result = self._rev_map.get(name) or ()
		return result

	def is_course_badge(self, name):
		result = name in self._rev_map
		return result
CatalogEntryBadgeCache = _CatalogEntryBadgeCache

def is_course_badge(name, cache=None):
	cache = cache if cache is not None else component.getUtility(ICatalogEntryBadgeCache)
	result = cache.is_course_badge(name)
	return result

@interface.implementer(ICourseBadgeCatalog)
class _CourseBadgeCatalog(object):

	def __init__(self, context):
		self.context = context

	@Lazy
	def cache(self):
		result = component.getUtility(ICatalogEntryBadgeCache)
		return result

	def iter_badges(self):
		result = []
		entry = catalog_entry(self.context)
		ntiid = entry_ntiid(entry) or u''
		for name in self.cache.get_badge_names(ntiid):
			badge = get_badge(name)
			if badge is not None:
				badge = proxy(badge, ntiid)
				result.append(badge)
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

	def __init__(self, *args, **kwargs):
		pass

	@Lazy
	def cache(self):
		result = component.getUtility(ICatalogEntryBadgeCache)
		return result

	def allow_badge(self, user, badge):
		result = False
		req = get_current_request()
		if req is not None:
			if req.authenticated_userid == user.username:
				result = True
			elif self.cache.is_course_badge(badge.name):
				result = show_course_badges(user)
			else:
				result = True
		return result

@component.adapter(IUser)
@interface.implementer(IPrincipalEarnableBadgeFilter)
class _CoursePrincipalEarnableBadgeFilter(object):

	def __init__(self, *args, **kwargs):
		pass

	@Lazy
	def _cache(self):
		result = component.getUtility(ICatalogEntryBadgeCache)
		return result

	def _startDate(self, entry):
		result = entry.StartDate if entry is not None else None
		return result

	def _endDate(self, entry):
		result = entry.EndDate if entry is not None else None
		return result

	def _get_entry(self, badge):
		ntiid = getattr(badge, 'SourceNTIID', None)
		result = find_catalog_entry(ntiid) if ntiid else None
		if result is None:
			ntiids = self._cache.get_badge_catalog_entry_ntiids(badge.name)
			for ntiid in ntiids:
				result = self._finder(ntiid)
				if result is not None:
					break
		result = catalog_entry(result)
		return result

	def allow_badge(self, user, badge):
		is_course_badge = self._cache.is_course_badge(badge.name)
		entry = self._get_entry(badge) if is_course_badge else None
		if is_course_badge:
			endDate = self._endDate(entry)
			startDate = self._startDate(entry)
			now = datetime.datetime.utcnow()
			result = (entry is not None) and \
					 (now >= startDate) and (not endDate or now <= endDate)
		else:
			result = True
		return result

@component.adapter(IUser)
@interface.implementer(IOpenBadgeAdapter)
class _OpenBadgeAdapter(object):

	def adapt(self, context):
		result = IBadgeClass(context, None)
		if result is not None and hasattr(context, "SourceNTIID"):
			result = proxy(result, context.SourceNTIID)
		return result
