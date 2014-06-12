#!/usr/bin/env python
# -*- coding: utf-8 -*
"""
.. $Id$
"""
from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

from zope import interface
from zope.schema import vocabulary
from zope.interface.common import mapping
from zope.interface.interface import taggedValue

from nti.app.client_preferences.interfaces import TAG_EXTERNAL_PREFERENCE_GROUP

from nti.utils import schema

COURSE_COMPLETION = u'completion'
COURSE_BADGE_TYPES = (COURSE_COMPLETION,)
COURSE_BADGE_TYPES_VOCABULARY = \
    vocabulary.SimpleVocabulary([vocabulary.SimpleTerm(_x) for _x in COURSE_BADGE_TYPES])

class ICourseBadge(interface.Interface):
    name = schema.ValidTextLine(title="Badge name")
    type = schema.Choice(vocabulary=COURSE_BADGE_TYPES_VOCABULARY,
                         title='Badge type', required=True, default=COURSE_COMPLETION)

class ICourseBadgeMap(mapping.IReadMapping):
    
    def is_no_course(course):
        """
        check if the course is for no course
        """

    def mark_no_course(badge):
        """
        mark this badge name for a no course
        """

    def mark(course):
        """
        mark a course this map
        """

    def add(course, badge, kind=COURSE_COMPLETION):
        """
        register a badge name for specified course ntiid and badge kind
        """

    def get_badge_names(course):
        """
        return the badge names associated w/ the specified course ntiid
        """

    def get_course_iden(badge):
        """
        return the course iden associated w/ the specfied badge name
        """
        
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
