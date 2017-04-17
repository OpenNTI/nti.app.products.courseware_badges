#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ACL providers for course data.

.. $Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from zope import component
from zope import interface

from zope.security.interfaces import IPrincipal

from nti.app.products.badges.interfaces import ACT_AWARD_BADGE

from nti.app.products.courseware_badges.courses import get_badge_courses

from nti.badges.interfaces import IBadgeClass

from nti.contenttypes.courses.utils import get_course_instructors

from nti.dataserver.authorization import ACT_READ

from nti.dataserver.authorization_acl import ace_allowing
from nti.dataserver.authorization_acl import acl_from_aces

from nti.dataserver.interfaces import ISupplementalACLProvider

from nti.property.property import Lazy

from nti.site.site import get_component_hierarchy_names


@component.adapter(IBadgeClass)
@interface.implementer(ISupplementalACLProvider)
class CourseBadgeSupplementalACLProvider(object):
    """
    Supplement :class:`IBadgeClass` objects with
    the acl of all courses containing refering to this badge. 
    """

    def __init__(self, context):
        self.context = context

    @Lazy
    def __acl__(self):
        instructors = set()
        courses = get_badge_courses(self.context.name,
                                    get_component_hierarchy_names())
        for course in courses:
            instructors.update(get_course_instructors(course))

        result = []
        for instructor in instructors:
            instructor = IPrincipal(instructor)
            ace_allowing(instructor, ACT_READ, type(self))
            ace_allowing(instructor, ACT_AWARD_BADGE, type(self))
        return acl_from_aces(result)
