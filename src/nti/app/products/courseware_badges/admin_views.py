#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from requests.structures import CaseInsensitiveDict

from zope import component

from zope.intid.interfaces import IIntIds

from pyramid import httpexceptions as hexc

from pyramid.view import view_config
from pyramid.view import view_defaults

from nti.app.base.abstract_views import AbstractAuthenticatedView

from nti.app.externalization.error import raise_json_error

from nti.app.products.badges.views import BadgeAdminPathAdapter

from nti.app.products.courseware_badges import MessageFactory as _
from nti.app.products.courseware_badges import get_course_badges_catalog
from nti.app.products.courseware_badges import get_universe_of_course_badges_for_user

from nti.app.products.courseware_badges.courses import course_badge_cache

from nti.badges.openbadges.interfaces import IBadgeClass

from nti.contenttypes.courses.interfaces import ICourseCatalog
from nti.contenttypes.courses.interfaces import ICourseInstance
from nti.contenttypes.courses.interfaces import ICourseCatalogEntry

from nti.dataserver import authorization as nauth

from nti.dataserver.users.users import User

from nti.externalization.externalization import to_external_object

from nti.externalization.interfaces import LocatedExternalDict
from nti.externalization.interfaces import StandardExternalFields

from nti.site.hostpolicy import run_job_in_all_host_sites

ITEMS = StandardExternalFields.ITEMS
TOTAL = StandardExternalFields.TOTAL
ITEM_COUNT = StandardExternalFields.ITEM_COUNT

logger = __import__('logging').getLogger(__name__)


@view_config(name="CourseBadgeCache")
@view_config(name="course_badge_cache")
@view_defaults(route_name='objects.generic.traversal',
               context=BadgeAdminPathAdapter,
               request_method='GET',
               permission=nauth.ACT_NTI_ADMIN,
               renderer='rest')
class CourseBadgeCacheView(AbstractAuthenticatedView):

    def __call__(self):
        result = LocatedExternalDict()
        result[ITEMS] = course_badge_cache()
        result.__parent__ = self.request.context
        result.__name__ = self.request.view_name
        return result


@view_config(name='RebuildCourseBadgeCache')
@view_config(name='rebuild_course_badge_cache')
@view_defaults(route_name='objects.generic.traversal',
               context=BadgeAdminPathAdapter,
               request_method='POST',
               permission=nauth.ACT_NTI_ADMIN,
               renderer='rest')
class RebuildCourseBadgeCacheView(AbstractAuthenticatedView):

    def __call__(self):
        seen = set()
        intids = component.getUtility(IIntIds)
        badge_catalog = get_course_badges_catalog()
        for index in list(badge_catalog.values()):
            index.clear()

        def _builder():
            catalog = component.queryUtility(ICourseCatalog)
            if catalog is None:
                return
            for entry in catalog.iterCatalogEntries():
                course = ICourseInstance(entry, None)
                uid = intids.queryId(course)
                if uid is not None and uid not in seen:
                    seen.add(uid)
                    badge_catalog.index_doc(uid, course)
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
            raise_json_error(self.request,
                             hexc.HTTPUnprocessableEntity,
                             {
                                 'message': _(u"Must specify a username."),
                             },
                             None)

        user = User.get_user(username)
        if user is None:
            raise_json_error(self.request,
                             hexc.HTTPUnprocessableEntity,
                             {
                                 'message': _(u"User cannot be found."),
                             },
                             None)

        result = LocatedExternalDict()
        items = result[ITEMS] = {}
        universe = get_universe_of_course_badges_for_user(user)
        for course, badges in universe:
            ntiid = ICourseCatalogEntry(course).ntiid
            items[ntiid] = [to_external_object(IBadgeClass(x)) for x in badges]
        result[TOTAL] = result[ITEM_COUNT] = len(items)
        return result
