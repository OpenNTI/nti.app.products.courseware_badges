#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

# disable: accessing protected members, too many methods
# pylint: disable=W0212,R0904

from hamcrest import has_entry
from hamcrest import has_length
from hamcrest import assert_that

from zope import component

from nti.app.products.courseware_badges.interfaces import ICatalogEntryBadgeCache

from nti.contenttypes.courses.interfaces import ICourseCatalog

from nti.app.products.courseware_badges.tests import CourseBadgesApplicationTestLayer

from nti.app.testing.application_webtest import ApplicationLayerTest

import nti.dataserver.tests.mock_dataserver as mock_dataserver
from nti.app.testing.decorators import WithSharedApplicationMockDS

class TestAdminViews(ApplicationLayerTest):

	layer = CourseBadgesApplicationTestLayer

	def _populate_cache(self):
		with mock_dataserver.mock_db_trans(self.ds, site_name='platform.ou.edu'):
			catalog = component.getUtility(ICourseCatalog)
			for entry in catalog.iterCatalogEntries():
				cache = component.getUtility(ICatalogEntryBadgeCache)
				cache.build(entry)
				
	@WithSharedApplicationMockDS(users=True, testapp=True)
	def test_views(self):
		# populate cache because badges are loaded after the library 
		self._populate_cache()
	
		get_path = '/dataserver2/BadgeAdmin/CourseBadgeCache'
		res = self.testapp.get(get_path)
		assert_that(res.json_body, has_entry('Items', has_length(3)))

		reset_path = '/dataserver2/BadgeAdmin/ResetCourseBadgeCache'
		self.testapp.post_json(reset_path, status=204 )
		
		get_path = '/dataserver2/BadgeAdmin/CourseBadgeCache'
		res = self.testapp.get(get_path)
		assert_that(res.json_body, has_entry('Items', has_length(0)))
