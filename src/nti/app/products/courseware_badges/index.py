#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from zope import interface

from zope.catalog.interfaces import ICatalog

from zope.intid.interfaces import IIntIds

from zope.location import locate

from nti.app.products.courseware_badges.courses import get_all_context_badges

from nti.common.string import to_unicode

from nti.contenttypes.courses.common import get_course_site

from nti.contenttypes.courses.interfaces import ICourseInstance
from nti.contenttypes.courses.interfaces import ICourseCatalogEntry

from nti.zope_catalog.catalog import Catalog

from nti.zope_catalog.index import AttributeSetIndex
from nti.zope_catalog.index import AttributeValueIndex as ValueIndex

IX_SITE = 'site'
IX_BADGES = 'badges'
IX_ENTRY = IX_COURSE = 'course'

COURSE_BADGES_CATALOG_NAME = 'nti.dataserver.++etc++course-badges-catalog'

class ValidatingCourseSiteName(object):

	__slots__ = (b'site',)

	def __init__(self, obj, default=None):
		if ICourseInstance.providedBy(obj):
			self.site = get_course_site(obj)

	def __reduce__(self):
		raise TypeError()

class CourseSiteIndex(ValueIndex):
	default_field_name = 'site'
	default_interface = ValidatingCourseSiteName

class ValidatingCatalogEntryID(object):

	__slots__ = (b'ntiid',)

	def __init__(self, obj, default=None):
		if ICourseInstance.providedBy(obj):
			entry = ICourseCatalogEntry(obj, None)
			if entry is not None:
				self.ntiid = to_unicode(entry.ntiid)

	def __reduce__(self):
		raise TypeError()

class CatalogEntryIDIndex(ValueIndex):
	default_field_name = 'ntiid'
	default_interface = ValidatingCatalogEntryID

class ValidatingCourseBadges(object):

	__slots__ = (b'badges',)

	def __init__(self, obj, default=None):
		if ICourseInstance.providedBy(obj):
			badges = get_all_context_badges( obj )
			self.badges = list((x.name for x in badges)) if badges else ()

	def __reduce__(self):
		raise TypeError()

class CourseBadgesIndex(AttributeSetIndex):
	default_field_name = 'badges'
	default_interface = ValidatingCourseBadges

@interface.implementer(ICatalog)
class CourseBadgesCatalog(Catalog):
	pass

def install_course_badges_catalog(site_manager_container, intids=None):
	lsm = site_manager_container.getSiteManager()
	intids = lsm.getUtility(IIntIds) if intids is None else intids
	catalog = lsm.queryUtility(ICatalog, name=COURSE_BADGES_CATALOG_NAME)
	if catalog is not None:
		return catalog

	catalog = CourseBadgesCatalog(family=intids.family)
	locate(catalog, site_manager_container, COURSE_BADGES_CATALOG_NAME)
	intids.register(catalog)
	lsm.registerUtility(catalog, provided=ICatalog, name=COURSE_BADGES_CATALOG_NAME)

	for name, clazz in ((IX_SITE, CourseSiteIndex),
						(IX_BADGES, CourseBadgesIndex),
						(IX_ENTRY, CatalogEntryIDIndex)):
		index = clazz(family=intids.family)
		intids.register(index)
		locate(index, catalog, name)
		catalog[name] = index
	return catalog
