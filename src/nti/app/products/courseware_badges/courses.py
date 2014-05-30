#!/usr/bin/env python
# -*- coding: utf-8 -*
"""
.. $Id$
"""
from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from zope import component
from zope import interface

from pyramid.threadlocal import get_current_request

from nti.app.products.badges.interfaces import IPrincipalErnableBadges
from nti.app.products.badges.interfaces import IPrincipalEarnedBadgeFilter

from nti.app.products.courseware.interfaces import ILegacyCommunityBasedCourseInstance

from nti.contenttypes.courses.interfaces import ICourseInstance

from nti.dataserver import interfaces as nti_interfaces

from . import interfaces
from . import is_course_badge
from . import get_course_badges
from . import show_course_badges
from . import get_course_badges_for_user

@interface.implementer(interfaces.ICourseBadgeCatalog)
class _CourseBadgeCatalog(object):

    def __init__(self, course):
        self.course = ICourseInstance(course)

    def iter_badges(self):
        return ()

@interface.implementer(interfaces.ICourseBadgeCatalog)
class _LegacyCourseBadgeCatalog(object):

    def __init__(self, course):
        self.course = ILegacyCommunityBasedCourseInstance(course)

    def iter_badges(self):
        result = get_course_badges(self.course.ContentPackageNTIID)
        return result

@component.adapter(nti_interfaces.IUser)
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

@component.adapter(nti_interfaces.IUser)
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
            elif is_course_badge(badge) and show_course_badges(user):
                result = True
        return result
