#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from zope import interface
from zope import component

from nti.badges.interfaces import IBadgeClass

from nti.contenttypes.courses.interfaces import ICourseInstance

from nti.dataserver.links import Link

from nti.externalization.singleton import SingletonDecorator
from nti.externalization.interfaces import StandardExternalFields
from nti.externalization.interfaces import IExternalObjectDecorator
from nti.externalization.interfaces import IExternalMappingDecorator

from . import VIEW_BADGES

from .courses import is_course_badge

LINKS = StandardExternalFields.LINKS

@component.adapter(ICourseInstance)
@interface.implementer(IExternalMappingDecorator)
class _CourseInstanceLinkDecorator(object):

	__metaclass__ = SingletonDecorator

	def decorateExternalMapping(self, context, result):
		_links = result.setdefault(LINKS, [])
		_links.append(Link(context, elements=(VIEW_BADGES,), rel=VIEW_BADGES))

@component.adapter(IBadgeClass)
@interface.implementer(IExternalObjectDecorator)
class _BadgeTypeAdder(object):

	__metaclass__ = SingletonDecorator

	def decorateExternalObject(self, context, mapping):
		if is_course_badge(context.name):
			mapping['Type'] = 'Course'
