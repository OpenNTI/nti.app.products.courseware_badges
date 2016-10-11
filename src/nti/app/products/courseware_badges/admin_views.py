#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from zope import component

from zope.intid.interfaces import IIntIds

from pyramid import httpexceptions as hexc

from pyramid.view import view_config
from pyramid.view import view_defaults

from nti.app.base.abstract_views import AbstractAuthenticatedView

from nti.app.products.badges.views import BadgeAdminPathAdapter

from nti.app.products.courseware_badges import get_universe_of_course_badges_for_user

from nti.app.products.courseware_badges.interfaces import ICatalogEntryBadgeCache

from nti.badges.openbadges.interfaces import IBadgeClass

from nti.common.maps import CaseInsensitiveDict

from nti.contenttypes.courses.interfaces import ICourseCatalog, ICourseInstance
from nti.contenttypes.courses.interfaces import ICourseCatalogEntry

from nti.dataserver import authorization as nauth

from nti.dataserver.users import User

from nti.externalization.externalization import to_external_object

from nti.externalization.interfaces import LocatedExternalDict
from nti.externalization.interfaces import StandardExternalFields

from nti.site.hostpolicy import run_job_in_all_host_sites

ITEMS = StandardExternalFields.ITEMS

@view_config(name="CourseBadgeCache")
@view_config(name="course_badge_cache")
@view_defaults(route_name='objects.generic.traversal',
			   context=BadgeAdminPathAdapter,
			   request_method='GET',
			   permission=nauth.ACT_NTI_ADMIN,
			   renderer='rest')
class CourseBadgeCacheView(AbstractAuthenticatedView):

	def __call__(self):
		cache = component.getUtility(ICatalogEntryBadgeCache)
		result = LocatedExternalDict()
		result[ITEMS] = cache.Items
		result.__parent__ = self.request.context
		result.__name__ = self.request.view_name
		self.request.response.last_modified = cache.lastModified
		return result

@view_config(name='ResetCourseBadgeCache')
@view_config(name='reset_course_badge_cache')
@view_defaults(route_name='objects.generic.traversal',
			   context=BadgeAdminPathAdapter,
			   request_method='POST',
			   permission=nauth.ACT_NTI_ADMIN,
				renderer='rest')
class ResetCourseBadgeCacheView(AbstractAuthenticatedView):

	def __call__(self):
		cache = component.getUtility(ICatalogEntryBadgeCache)
		cache.clear()
		return hexc.HTTPNoContent()

@view_config(name='RebuildCourseBadgeCache')
@view_config(name='rebuild_course_badge_cache')
@view_defaults(route_name='objects.generic.traversal',
			   context=BadgeAdminPathAdapter,
			   request_method='POST',
			   permission=nauth.ACT_NTI_ADMIN,
			   renderer='rest')
class RebuildCourseBadgeCacheView(AbstractAuthenticatedView):

	def __call__(self):
		intids = component.getUtility(IIntIds)
		cache = component.getUtility(ICatalogEntryBadgeCache)
		cache.clear()
		seen = set()
		def _builder():
			catalog = component.queryUtility(ICourseCatalog)
			if catalog is None:
				return
			for entry in catalog.iterCatalogEntries():
				course = ICourseInstance(entry, None)
				uid = intids.queryId(course)
				if uid is not None and uid not in seen:
					seen.add(uid)
					cache.build(entry)
		run_job_in_all_host_sites(_builder)
		return hexc.HTTPNoContent()

@view_config(name="UserCourseBadges")
@view_config(name="user_course_badges")
@view_defaults(route_name='objects.generic.traversal',
			   context=BadgeAdminPathAdapter,
			   request_method='GET',
			   permission=nauth.ACT_NTI_ADMIN,
			   renderer='rest')
class UserCourseBadgesView(AbstractAuthenticatedView):

	def __call__(self):
		values = CaseInsensitiveDict(**self.request.params)
		username = values.get('username')
		if not username:
			raise hexc.HTTPUnprocessableEntity("Must specify a username")

		user = User.get_user(username)
		if user is None:
			raise hexc.HTTPUnprocessableEntity("User cannot be found")

		result = LocatedExternalDict()
		items = result[ITEMS] = {}
		universe = get_universe_of_course_badges_for_user(user)
		for course, badges in universe:
			ntiid = ICourseCatalogEntry(course).ntiid
			items[ntiid] = [to_external_object(IBadgeClass(x)) for x in badges]
		result['Total'] = result['ItemCount'] = len(items)
		return result
