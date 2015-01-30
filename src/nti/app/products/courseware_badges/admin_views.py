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
from pyramid import httpexceptions as hexc

from nti.app.base.abstract_views import AbstractAuthenticatedView

from nti.app.products.badges.views import BadgeAdminPathAdapter

from nti.dataserver import authorization as nauth

from nti.externalization.interfaces import LocatedExternalDict
from nti.externalization.interfaces import StandardExternalFields

from .interfaces import ICatalogEntryBadgeCache

ITEMS = StandardExternalFields.ITEMS

@view_config(route_name='objects.generic.traversal',
			  context=BadgeAdminPathAdapter,
			  request_method='GET',
			  permission=nauth.ACT_NTI_ADMIN,
			  renderer='rest',
			  name="CourseBadgeCache")
class CourseBadgeCacheView(AbstractAuthenticatedView):

	def __call__(self):
		cache = component.getUtility(ICatalogEntryBadgeCache)
		result = LocatedExternalDict()
		result[ITEMS] = cache.Items
		result.__parent__ = self.request.context
		result.__name__ = self.request.view_name
		self.request.response.last_modified = cache.lastModified
		return result

@view_config(route_name='objects.generic.traversal',
			  context=BadgeAdminPathAdapter,
			  request_method='POST',
			  permission=nauth.ACT_NTI_ADMIN,
			  renderer='rest',
			  name='ResetCourseBadgeCache')
class ResetCourseBadgeCacheView(AbstractAuthenticatedView):

	def __call__(self):
		cache = component.getUtility(ICatalogEntryBadgeCache)
		cache.clear()
		return hexc.HTTPNoContent()
