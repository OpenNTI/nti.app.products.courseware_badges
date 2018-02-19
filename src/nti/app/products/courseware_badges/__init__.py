#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from zope import component

from zope.catalog.interfaces import ICatalog

from zope.preference.interfaces import IPreferenceGroup

from zope.security.interfaces import IParticipation

from zope.security.management import endInteraction
from zope.security.management import newInteraction
from zope.security.management import restoreInteraction

from nti.app.products.badges import BADGES
from nti.app.products.badges import get_badge
from nti.app.products.badges import get_all_badges
from nti.app.products.badges import assertion_exists

from nti.app.products.courseware import MessageFactory

from nti.app.products.courseware_badges.index import COURSE_BADGES_CATALOG_NAME

from nti.app.products.courseware_badges.interfaces import ICourseBadgeCatalog

from nti.app.products.courseware_badges.utils import get_badge_type
from nti.app.products.courseware_badges.utils import find_course_badges_from_badges

from nti.contenttypes.courses.interfaces import ICourseInstance
from nti.contenttypes.courses.interfaces import ICourseCatalogEntry
from nti.contenttypes.courses.interfaces import IPrincipalEnrollments

#: Badged view
VIEW_BADGES = BADGES

#: Earned basges view
VIEW_EARNED_COURSE_BADGES = u'EarnedCourseBadges'

logger = __import__('logging').getLogger(__name__)


def show_course_badges(user):
    endInteraction()
    try:
        newInteraction(IParticipation(user))
        prefs = component.getUtility(IPreferenceGroup, name='Badges.Course')
        result = prefs.show_course_badges
        return result
    finally:
        restoreInteraction()


def get_universe_of_course_badges_for_user(user):
    """
    return the badges for the courses a user in enrolled in
    """
    result = []
    for enrollments in component.subscribers((user,), IPrincipalEnrollments):
        for enrollment in enrollments.iter_enrollments():
            course = ICourseInstance(enrollment)
            adapted = ICourseBadgeCatalog(course)
            # pylint: disable=too-many-function-args
            result.append((course, adapted.iter_badges()))
    return result


def get_course_badges_for_user(user):
    """
    return the badges for the courses a user in enrolled in
    """
    result = []
    for unused_course, badges in get_universe_of_course_badges_for_user(user):
        result.extend(badges)
    return result


def get_earned_course_badges(user):
    """
    return the earned course badges for a user
    """
    result = []
    for badge in get_course_badges_for_user(user):
        if assertion_exists(user, badge):
            result.append(badge)
    return result


def get_catalog_entry_for_badge(badge):
    return ICourseCatalogEntry(badge, None)


def get_course_badges_catalog():
    return component.queryUtility(ICatalog, COURSE_BADGES_CATALOG_NAME)
