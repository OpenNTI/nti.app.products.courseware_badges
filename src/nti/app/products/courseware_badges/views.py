#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from pyramid.view import view_config

from nti.app.base.abstract_views import AbstractAuthenticatedView

from nti.badges.openbadges.interfaces import IBadgeClass

from nti.contenttypes.courses.interfaces import ICourseInstance

from nti.dataserver.interfaces import IUser
from nti.dataserver import authorization as nauth

from nti.externalization.interfaces import LocatedExternalDict
from nti.externalization.interfaces import StandardExternalFields

from . import VIEW_BADGES
from . import show_course_badges
from . import get_earned_course_badges
from . import VIEW_EARNED_COURSE_BADGES

from .interfaces import ICourseBadgeCatalog

ITEMS = StandardExternalFields.ITEMS

@view_config(route_name='objects.generic.traversal',
			  context=ICourseInstance,
			  request_method='GET',
			  permission=nauth.ACT_READ,
			  renderer='rest',
			  name=VIEW_BADGES)
class CourseBadgesView(AbstractAuthenticatedView):

	def __call__(self):
		result = LocatedExternalDict()
		result[ITEMS] = items = []

		context = self.request.context
		badge_catalog = ICourseBadgeCatalog(context, None)
		badges = badge_catalog.iter_badges() if badge_catalog is not None else ()
		items.extend(IBadgeClass(b) for b in badges)

		result.__parent__ = context
		result.__name__ = self.request.view_name
		self.request.response.last_modified = context.lastModified
		return result

@view_config(route_name='objects.generic.traversal',
			  context=IUser,
			  request_method='GET',
			  permission=nauth.ACT_READ,
			  renderer='rest',
			  name=VIEW_EARNED_COURSE_BADGES)
class EarnedCourseBadgesView(AbstractAuthenticatedView):

	def __call__(self):
		result = LocatedExternalDict()
		result[ITEMS] = items = []

		context = self.request.context
		if self.remoteUser.username == context.username or show_course_badges(context):
			badges = get_earned_course_badges(context)
			items.extend(IBadgeClass(b) for b in badges)

		result.__parent__ = context
		result.__name__ = self.request.view_name
		return result
