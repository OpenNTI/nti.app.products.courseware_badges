#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

# pylint: disable=inherit-non-class,expression-not-assigned

from zope import interface

from zope.deprecation import deprecated

from zope.interface.common.mapping import IMapping

from zope.interface.interface import taggedValue

from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary

from nti.app.client_preferences.interfaces import TAG_EXTERNAL_PREFERENCE_GROUP

from nti.schema.field import Bool

COURSE_COMPLETION = u'completion'
COURSE_BADGE_TYPES = (COURSE_COMPLETION,)
COURSE_BADGE_TYPES_VOCABULARY = \
    SimpleVocabulary([SimpleTerm(_x) for _x in COURSE_BADGE_TYPES])


class ICourseBadgeSettings(interface.Interface):
    """
    The root of the settings tree for badges
    """
    taggedValue(TAG_EXTERNAL_PREFERENCE_GROUP, 'write')

    show_course_badges = Bool(title=u"Enable/disable showing course badges",
                              description=u"Enable/disable showing course badges",
                              default=False)


class ICourseBadgeCatalog(interface.Interface):

    def iter_badges():
        """
        Return an iterable of badges for a course
        """


deprecated('ICatalogEntryBadgeCache', 'Use lastest index implementation')
class ICatalogEntryBadgeCache(IMapping):
    pass
