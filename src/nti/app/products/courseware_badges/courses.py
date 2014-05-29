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

from nti.app.products.courseware.interfaces import IPrincipalEnrollmentCatalog
from nti.app.products.courseware.interfaces import ILegacyCommunityBasedCourseInstance

from nti.contenttypes.courses.interfaces import ICourseInstance

from nti.dataserver import interfaces as nti_interfaces

from . import interfaces
from . import get_course_badges

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
            for catalog in component.subscribers((self.user,), IPrincipalEnrollmentCatalog):
                for course in catalog.iter_enrollments():
                    course = ICourseInstance(course)
                    predicate = interfaces.get_course_badge_predicate_for_user(course, self.user)
                    adapted = interfaces.ICourseBadgeCatalog(course)
                    result.extend(b for b in adapted.iter_badges() if predicate(b))
        return result

@component.adapter(ICourseInstance, nti_interfaces.IUser)
@interface.implementer(interfaces.ICoursePrincipalBadgeFilter)
class _DefaultCoursePrincipalBadgeFilter(object):

    __slots__ = ()

    def __init__(self, *args):
        pass

    def allow_badge(self, course, user, bage):
        return True
