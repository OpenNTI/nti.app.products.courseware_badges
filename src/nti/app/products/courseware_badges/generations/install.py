#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

generation = 2

import zope.intid

from zope.generations.generations import SchemaManager

from ..courses import _CatalogEntryBadgeCache
from ..interfaces import ICatalogEntryBadgeCache

class _CoursewareBadgesSchemaManager(SchemaManager):
	"""
	A schema manager that we can register as a utility in ZCML.
	"""
	def __init__(self):
		super(_CoursewareBadgesSchemaManager, self).__init__(
									generation=generation,
									minimum_generation=generation,
									package_name='nti.app.products.courseware_badges.generations')
def evolve(context):
	install_course_badge_cache(context)

def install_course_badge_cache(context):
	conn = context.connection
	root = conn.root()
	
	dataserver_folder = root['nti.dataserver']
	lsm = dataserver_folder.getSiteManager()
	cache = lsm.queryUtility(ICatalogEntryBadgeCache)
	if cache is None:
		intids = lsm.getUtility(zope.intid.IIntIds)
		cache = _CatalogEntryBadgeCache()
		cache.__parent__ = dataserver_folder
		cache.__name__ = '++etc++course++badge++cache'
		intids.register(cache)
		lsm.registerUtility(cache, provided=ICatalogEntryBadgeCache)
	return cache
