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

from zope.container.contained import Contained

from zope.deprecation import deprecated

from zope.intid.interfaces import IIntIds

from pyramid.threadlocal import get_current_request

from nti.app.products.badges import get_badge

from nti.app.products.badges.interfaces import IOpenBadgeAdapter
from nti.app.products.badges.interfaces import IPrincipalErnableBadges
from nti.app.products.badges.interfaces import IPrincipalEarnedBadgeFilter
from nti.app.products.badges.interfaces import IPrincipalEarnableBadgeFilter

from nti.app.products.courseware.utils import ZERO_DATETIME

from nti.app.products.courseware_badges import show_course_badges
from nti.app.products.courseware_badges import get_course_badges_catalog
from nti.app.products.courseware_badges import get_course_badges_for_user

from nti.app.products.courseware_badges.index import IX_SITE
from nti.app.products.courseware_badges.index import IX_BADGES

from nti.app.products.courseware_badges.interfaces import ICourseBadgeCatalog

from nti.app.products.courseware_badges.utils import proxy
from nti.app.products.courseware_badges.utils import find_catalog_entry

from nti.badges.openbadges.interfaces import IBadgeClass

from nti.contenttypes.courses.interfaces import ICourseInstance
from nti.contenttypes.courses.interfaces import ICourseCatalogEntry

from nti.dataserver.dicts import LastModifiedDict

from nti.dataserver.interfaces import IUser

from nti.site.site import get_component_hierarchy_names


def get_badge_catalog_entries(name):
    result = []
    intids = component.getUtility(IIntIds)
    badge_index = get_course_badges_catalog()[IX_BADGES]
    course_uids = badge_index.values_to_documents.get(name)
    for course_uid in course_uids or ():
        course = intids.queryObject(course_uid)
        if ICourseInstance.providedBy(course):
            entry = ICourseCatalogEntry(course, None)
            if entry is not None:
                result.append(entry)
    result.sort(key=lambda x: x.StartDate or ZERO_DATETIME, reverse=True)
    return result


def get_badge_catalog_entry_ntiids(name):
    result = get_badge_catalog_entries(name)
    return [x.ntiid for x in result]


def is_course_badge(name, *args):
    return bool(get_badge_catalog_entry_ntiids(name))


def get_badge_names(ntiid, intids=None):
    result = ()
    entry = find_catalog_entry(ntiid)
    intids = component.getUtility(IIntIds) if intids is None else intids
    if entry is not None:
        course = ICourseInstance(entry)
        course_uid = intids.queryId(course)
        badge_index = get_course_badges_catalog()[IX_BADGES]
        if course_uid is not None:
            badge_names = badge_index.documents_to_values.get(course_uid)
            result = tuple(badge_names or ())
    return result


def course_badge_cache():
    result = dict()
    sites = get_component_hierarchy_names()
    query = {IX_SITE: {'any_of': sites}}
    catalog = get_course_badges_catalog()
    intids = component.getUtility(IIntIds)
    for doc_id in catalog.apply(query) or ():
        course = intids.queryObject(doc_id)
        if ICourseInstance.providedBy(course):
            entry = ICourseCatalogEntry(course)
            badge_names = get_badge_names(entry.ntiid, intids=intids)
            if badge_names:
                result[entry.ntiid] = badge_names
    return result


@interface.implementer(ICourseBadgeCatalog)
class _CourseBadgeCatalog(object):

    __slots__ = ('context',)

    def __init__(self, context):
        self.context = context

    def iter_badges(self):
        result = []
        entry = ICourseCatalogEntry(self.context, None)
        ntiid = getattr(entry, 'ntiid', None) or u''
        for name in get_badge_names(ntiid):
            badge = get_badge(name)
            if badge is not None:
                badge = proxy(badge, ntiid)
                result.append(badge)
        return result


@component.adapter(IUser)
@interface.implementer(IPrincipalErnableBadges)
class _CourseErnableBadges(object):

    __slots__ = ('user',)

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

    __slots__ = ()

    def __init__(self, *args, **kwargs):
        pass

    def allow_badge(self, user, badge):
        result = False
        req = get_current_request()
        if req is not None:
            if req.authenticated_userid == user.username:
                result = True
            elif is_course_badge(badge.name):
                result = show_course_badges(user)
            else:
                result = True
        return result


@component.adapter(IUser)
@interface.implementer(IPrincipalEarnableBadgeFilter)
class _CoursePrincipalEarnableBadgeFilter(object):

    __slots__ = ()

    def __init__(self, *args, **kwargs):
        pass

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
            ntiids = get_badge_catalog_entry_ntiids(badge.name)
            for ntiid in ntiids or ():  # find first
                result = find_catalog_entry(ntiid)
                if result is not None:
                    break
        result = ICourseCatalogEntry(result, None)
        return result

    def allow_badge(self, user, badge):
        is_cb = is_course_badge(badge.name)
        entry = self._get_entry(badge) if is_cb else None
        if is_cb:
            endDate = self._endDate(entry)
            startDate = self._startDate(entry)
            now = datetime.datetime.utcnow()
            result =     (entry is not None) \
                     and (now >= startDate) \
                     and (not endDate or now <= endDate)
        else:
            result = True
        return result


@component.adapter(IUser)
@interface.implementer(IOpenBadgeAdapter)
class _OpenBadgeAdapter(object):

    __slots__ = ()

    def __init__(self, *args, **kwargs):
        pass

    def adapt(self, context):
        result = IBadgeClass(context, None)
        if result is not None and hasattr(context, "SourceNTIID"):
            result = proxy(result, context.SourceNTIID)
        return result


deprecated('_CatalogEntryBadgeCache', 'Use lastest index implementation')
class _CatalogEntryBadgeCache(LastModifiedDict, Contained):
    pass
