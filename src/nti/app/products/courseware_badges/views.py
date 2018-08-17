#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from pyramid.view import view_config

from nti.app.base.abstract_views import AbstractAuthenticatedView

from nti.app.products.courseware_badges import VIEW_BADGES
from nti.app.products.courseware_badges import VIEW_EARNED_COURSE_BADGES

from nti.app.products.courseware_badges import show_course_badges
from nti.app.products.courseware_badges import get_earned_course_badges

from nti.app.products.courseware_badges.interfaces import ICourseBadgeCatalog

from nti.badges.openbadges.interfaces import IBadgeClass

from nti.contenttypes.courses.interfaces import ICourseInstance
from nti.contenttypes.courses.interfaces import ICourseCatalogEntry

from nti.dataserver import authorization as nauth

from nti.dataserver.interfaces import IUser

from nti.externalization.interfaces import LocatedExternalDict
from nti.externalization.interfaces import StandardExternalFields

ITEMS = StandardExternalFields.ITEMS
TOTAL = StandardExternalFields.TOTAL
ITEM_COUNT = StandardExternalFields.ITEM_COUNT

logger = __import__('logging').getLogger(__name__)


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
        # query course badge catalog
        course = ICourseInstance(self.context)
        badge_catalog = ICourseBadgeCatalog(course, None)
        if badge_catalog is not None:
            # pylint: disable=too-many-function-args
            items.extend(IBadgeClass(b) for b in badge_catalog.iter_badges())
        result[TOTAL] = result[ITEM_COUNT] = len(items)
        # pylint: disable=no-member
        self.request.response.last_modified = self.context.lastModified
        return result


@view_config(route_name='objects.generic.traversal',
             context=ICourseCatalogEntry,
             request_method='GET',
             permission=nauth.ACT_READ,
             renderer='rest',
             name=VIEW_BADGES)
class CatalogEntryBadgesView(CourseBadgesView):
    pass


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
        # pylint: disable=no-member
        if     self.remoteUser.username == self.context.username \
            or show_course_badges(self.context):
            badges = get_earned_course_badges(self.context)
            items.extend(IBadgeClass(b) for b in badges)
        result[TOTAL] = result[ITEM_COUNT] = len(items)
        return result
