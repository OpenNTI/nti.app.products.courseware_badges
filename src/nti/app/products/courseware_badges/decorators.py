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

import repoze.lru

from nti.contentlibrary import interfaces as lib_interfaces

from nti.app.products.courseware.interfaces import ICourseCatalogEntry
from nti.contenttypes.courses.interfaces import ICourseInstance

from nti.dataserver.links import Link

from nti.externalization import interfaces as ext_interfaces
from nti.externalization.singleton import SingletonDecorator
from nti.externalization.interfaces import StandardExternalFields
from nti.externalization.interfaces import IExternalMappingDecorator

from . import VIEW_BADGES
from . import base_root_ntiid

LINKS = StandardExternalFields.LINKS

@component.adapter(ICourseInstance)
@interface.implementer(IExternalMappingDecorator)
class _CourseInstanceLinkDecorator(object):

    __metaclass__ = SingletonDecorator

    def decorateExternalMapping(self, context, result):
        _links = result.setdefault(LINKS, [])
        _links.append(Link(context, elements=(VIEW_BADGES,), rel=VIEW_BADGES))

@repoze.lru.lru_cache(1000)
def get_to_content_package_ntiid(badge_ntiid):
    raw_badge_nttid = base_root_ntiid(badge_ntiid)
    library = component.queryUtility(lib_interfaces.IContentPackageLibrary)
    for cp in getattr(library, 'contentPackages', ()):
        raw_content_package_nttid = base_root_ntiid(cp.ntiid)
        if raw_content_package_nttid == raw_badge_nttid:
            return cp.ntiid

def get_content_package(badge_ntiid):
    cp_ntiid = get_to_content_package_ntiid(badge_ntiid)
    library = component.queryUtility(lib_interfaces.IContentPackageLibrary)
    if library and cp_ntiid:
        return library[cp_ntiid]
    return None

@interface.implementer(ext_interfaces.IExternalObjectDecorator)
class _BadgeTitleAdder(object):

    __metaclass__ = SingletonDecorator

    def decorateExternalObject(self, context, mapping):
        content_package = get_content_package(context.name)
        course = ICourseInstance(content_package, None)
        entry = ICourseCatalogEntry(course, None)
        if entry is not None:
            mapping['Title'] = entry.Title
