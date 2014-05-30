#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""
from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from zope import component

from pyramid.view import view_config

from nti.app.base.abstract_views import AbstractAuthenticatedView

from nti.app.products.courseware.interfaces import IPrincipalEnrollmentCatalog

from nti.badges import interfaces as badge_interfaces

from nti.contenttypes.courses.interfaces import ICourseInstance

from nti.dataserver import authorization as nauth
from nti.dataserver import interfaces as nti_interfaces

from nti.externalization.interfaces import LocatedExternalDict

from . import interfaces
from . import assertion_exists
from . import show_course_badges

from . import VIEW_BADGES
from . import VIEW_EARNED_COURSE_BADGES

@view_config(route_name='objects.generic.traversal',
			  context=ICourseInstance,
			  request_method='GET',
			  permission=nauth.ACT_READ,
			  renderer='rest',
			  name=VIEW_BADGES)
class CourseBadgesView(AbstractAuthenticatedView):

	def __call__(self):
		result = LocatedExternalDict()
		result['Items'] = items = []

		context = self.request.context
		content_package_ntiid = getattr(context, 'ContentPackageNTIID', None)
		if content_package_ntiid:
			badges = interfaces.ICourseBadgeCatalog(context).iter_badges()
			items.extend(badge_interfaces.INTIBadge(b) for b in badges)

		result.__parent__ = context
		result.__name__ = self.request.view_name
		self.request.response.last_modified = context.lastModified
		return result

@view_config(route_name='objects.generic.traversal',
			  context=nti_interfaces.IUser,
			  request_method='GET',
			  permission=nauth.ACT_READ,
			  renderer='rest',
			  name=VIEW_EARNED_COURSE_BADGES)
class EarnedCourseBadgesView(AbstractAuthenticatedView):

	def __call__(self):
		result = LocatedExternalDict()
		result['Items'] = items = []

		show = True
		request = self.request
		context = self.request.context
		if 	request.authenticated_userid != context.username and \
			not show_course_badges(context):
			show = False

		if show:
			user_course_badges = []
			for catalog in component.subscribers((context,), IPrincipalEnrollmentCatalog):
				for course in catalog.iter_enrollments():
					course = ICourseInstance(course)
					adapted = interfaces.ICourseBadgeCatalog(course)
					user_course_badges.extend(adapted.iter_badges())

			for badge in user_course_badges:
				if assertion_exists(context, badge):
					items.append(badge)

		result.__parent__ = context
		result.__name__ = self.request.view_name
		self.request.response.last_modified = context.lastModified
		return result
