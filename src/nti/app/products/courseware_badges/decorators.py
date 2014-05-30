#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
$Id$
"""
from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from zope import interface
from zope import component

from pyramid.threadlocal import get_current_request

from nti.contenttypes.courses.interfaces import ICourseInstance

from nti.dataserver import interfaces as nti_interfaces

from nti.dataserver.links import Link

from nti.externalization.singleton import SingletonDecorator
from nti.externalization.interfaces import StandardExternalFields
from nti.externalization.interfaces import IExternalMappingDecorator

from . import show_course_badges

from . import VIEW_BADGES
from . import VIEW_EARNED_COURSE_BADGES

LINKS = StandardExternalFields.LINKS

@component.adapter(ICourseInstance)
@interface.implementer(IExternalMappingDecorator)
class _CourseInstanceLinkDecorator(object):

    __metaclass__ = SingletonDecorator

    def decorateExternalMapping(self, context, result):
        _links = result.setdefault(LINKS, [])
        _links.append(Link(context, elements=(VIEW_BADGES,), rel=VIEW_BADGES))


@component.adapter(nti_interfaces.IUser)
@interface.implementer(IExternalMappingDecorator)
class _UserCourseEarnedBadgesLinkDecorator(object):

    __metaclass__ = SingletonDecorator
            
    def decorateExternalMapping(self, context, result):
        req = get_current_request()
        if  req is None or req.authenticated_userid is None or \
            req.authenticated_userid == context.username or \
            not show_course_badges(context):
            return
        
        _links = result.setdefault(LINKS, [])
        _links.append(Link(context, elements=(VIEW_EARNED_COURSE_BADGES,),
                           rel=VIEW_EARNED_COURSE_BADGES))
