#!/usr/bin/env python
# -*- coding: utf-8 -*
"""
.. $Id$
"""
from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

from zope import component
from zope import interface
from zope.interface.interface import taggedValue

from nti.app.client_preferences.interfaces import TAG_EXTERNAL_PREFERENCE_GROUP

from nti.utils import schema

class ICourseBadgeSettings(interface.Interface):
    """
    The root of the settings tree for badges
    """
    taggedValue(TAG_EXTERNAL_PREFERENCE_GROUP, 'write')

    show_course_badges = schema.Bool(title="Enable/disable showing course badges",
                                     description="Enable/disable showing course badges",
                                     default=False)

class ICourseBadgeCatalog(interface.Interface):

    def iter_badges():
        """
        Return an iterable of badges for a course
        """

class ICoursePrincipalBadgeFilter(interface.Interface):
    """
    define subscriber course badge filter
    """

    def allow_badge(course, user, badge):
        """
        allow the specified badge
        """

def get_course_badge_predicate_for_user(course, user):
    filters = component.subscribers((course, user,), ICoursePrincipalBadgeFilter)
    filters = list(filters)
    def uber_filter(badge):
        return all((f.allow_badge(course, user, badge) for f in filters))
    return uber_filter
