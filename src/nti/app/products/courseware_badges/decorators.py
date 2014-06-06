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

import repoze.lru

from nti.app.products.courseware import interfaces as course_interfaces

from nti.badges import interfaces as badge_interfaces

from nti.contentlibrary import interfaces as lib_interfaces

from nti.contenttypes.courses.interfaces import ICourseInstance

from nti.dataserver.links import Link

from nti.externalization.singleton import SingletonDecorator
from nti.externalization.interfaces import StandardExternalFields
from nti.externalization.interfaces import IExternalObjectDecorator
from nti.externalization.interfaces import IExternalMappingDecorator

from . import VIEW_BADGES

LINKS = StandardExternalFields.LINKS

@component.adapter(ICourseInstance)
@interface.implementer(IExternalMappingDecorator)
class _CourseInstanceLinkDecorator(object):

	__metaclass__ = SingletonDecorator

	def decorateExternalMapping(self, context, result):
		_links = result.setdefault(LINKS, [])
		_links.append(Link(context, elements=(VIEW_BADGES,), rel=VIEW_BADGES))

@repoze.lru.lru_cache(1000)
def get_course_nttid_for_badge(badge):
	unit = lib_interfaces.IContentPackage(badge, None)
	course = ICourseInstance(unit, None)
	entry = course_interfaces.ICourseCatalogEntry(course, None)
	result = getattr(entry, 'ContentPackageNTIID', None)
	return result

@component.adapter(badge_interfaces.IBadgeClass)
@interface.implementer(IExternalObjectDecorator)
class _BadgeTypeAdder(object):

	__metaclass__ = SingletonDecorator

	def decorateExternalObject(self, context, mapping):
		ntiid = get_course_nttid_for_badge(context)
		if ntiid:
			mapping['Type'] = 'Course'
