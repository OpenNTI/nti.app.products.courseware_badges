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

from nti.app.products.badges.interfaces import IPrincipalErnableBadges

from nti.app.products.courseware.interfaces import IPrincipalEnrollmentCatalog
from nti.app.products.courseware.interfaces import ILegacyCommunityBasedCourseInstance

from nti.contenttypes.courses.interfaces import ICourseInstance

from nti.dataserver import interfaces as nti_interfaces

from . import interfaces
from . import get_course_badges

@interface.implementer(interfaces.ICourseBadgeCatalog)
class _CourseBadgeCatalog(object):

    __slots__ = ('course',)

    def __init__(self, course):
        self.course = ICourseInstance(course)

    def iter_badges(self):
        return ()

@component.adapter(nti_interfaces.IUser)
@interface.implementer(interfaces.ICourseBadgeCatalog)
class _LegacyCourseBadgeCatalog(object):

    __slots__ = ('course',)

    def __init__(self, course):
        self.course = ILegacyCommunityBasedCourseInstance(course)

    def iter_badges(self):
        result = get_course_badges(self.course.ContentPackageNTIID)
        return result

@component.adapter(nti_interfaces.IUser)
@interface.implementer(IPrincipalErnableBadges)
class _CourseErnableBadges(object):

    __slots__ = ('user')

    def __init__(self, user):
        self.user = user

    def iter_badges(self):
        result = []
        for catalog in component.subscribers((self.user,), IPrincipalEnrollmentCatalog):
            for course in catalog.iter_enrollments():
                adapted = interfaces.ICourseBadgeCatalog(course)
                result.extend(adapted.iter_badges())
        return result
