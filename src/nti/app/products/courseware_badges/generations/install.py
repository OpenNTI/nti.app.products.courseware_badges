#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

generation = 1

import zope.intid

from zope.generations.generations import SchemaManager

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
	return
	conn = context.connection
	root = conn.root()

	dataserver_folder = root['nti.dataserver']
	lsm = dataserver_folder.getSiteManager()
	intids = lsm.getUtility(zope.intid.IIntIds)

	registry = object()
	registry.__parent__ = dataserver_folder
	registry.__name__ = '++etc++course++badge++cache'
	intids.register(registry)
	lsm.registerUtility(registry, provided=ICatalogEntryBadgeCache)
	return registry