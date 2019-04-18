#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from zope import component
from zope import interface

from nti.app.products.courseware_badges import VIEW_BADGES

from nti.app.products.courseware_badges.courses import is_course_badge

from nti.badges.interfaces import IBadgeClass

from nti.contenttypes.courses.interfaces import ICourseInstance

from nti.coremetadata.interfaces import IUser

from nti.externalization.interfaces import StandardExternalFields
from nti.externalization.interfaces import IExternalObjectDecorator
from nti.externalization.interfaces import IExternalMappingDecorator

from nti.externalization.singleton import Singleton

from nti.links.links import Link

LINKS = StandardExternalFields.LINKS

logger = __import__('logging').getLogger(__name__)


@component.adapter(ICourseInstance)
@interface.implementer(IExternalMappingDecorator)
class _CourseInstanceLinkDecorator(Singleton):

    def decorateExternalMapping(self, context, result):
        _links = result.setdefault(LINKS, [])
        _links.append(Link(context, elements=(VIEW_BADGES,), rel=VIEW_BADGES))


@component.adapter(IUser)
@interface.implementer(IExternalMappingDecorator)
class _UserLinkDecorator(Singleton):
    """
    Marker rel saying badges are enabled.
    """

    def decorateExternalMapping(self, context, result):
        _links = result.setdefault(LINKS, [])
        _links.append(Link(context, elements=(VIEW_BADGES,), rel=VIEW_BADGES))


@component.adapter(IBadgeClass)
@interface.implementer(IExternalObjectDecorator)
class _BadgeTypeAdder(Singleton):

    def decorateExternalObject(self, context, mapping):
        if is_course_badge(context.name):
            mapping['Type'] = 'Course'
