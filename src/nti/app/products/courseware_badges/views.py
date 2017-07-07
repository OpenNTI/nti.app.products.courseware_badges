#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from pyramid.view import view_config

from nti.app.base.abstract_views import AbstractAuthenticatedView

from nti.app.products.courseware_badges import VIEW_BADGES
from nti.app.products.courseware_badges import VIEW_EARNED_COURSE_BADGES

from nti.app.products.courseware_badges import show_course_badges
from nti.app.products.courseware_badges import get_earned_course_badges

from nti.app.products.courseware_badges.interfaces import ICourseBadgeCatalog

from nti.badges.openbadges.interfaces import IBadgeClass

from nti.contenttypes.courses.interfaces import ICourseInstance

from nti.dataserver import authorization as nauth

from nti.dataserver.interfaces import IUser

from nti.externalization.interfaces import LocatedExternalDict
from nti.externalization.interfaces import StandardExternalFields

ITEMS = StandardExternalFields.ITEMS
TOTAL = StandardExternalFields.TOTAL
ITEM_COUNT = StandardExternalFields.ITEM_COUNT


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
        result.__parent__ = self.context
        result.__name__ = self.request.view_name
        self.request.response.last_modified = self.context.lastModified
        badge_catalog = ICourseBadgeCatalog(self.context, None)
        if badge_catalog is not None:
            items.extend(IBadgeClass(b) for b in badge_catalog.iter_badges())
        result[TOTAL] = result[ITEM_COUNT] = len(items)
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
        result.__parent__ = self.context
        result.__name__ = self.request.view_name
        if     self.remoteUser.username == self.context.username \
            or show_course_badges(self.context):
            badges = get_earned_course_badges(self.context)
            items.extend(IBadgeClass(b) for b in badges)
        result[TOTAL] = result[ITEM_COUNT] = len(items)
        return result
