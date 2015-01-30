#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

# disable: accessing protected members, too many methods
# pylint: disable=I0011,W0212,R0904

from hamcrest import none
from hamcrest import is_not
from hamcrest import has_item
from hamcrest import has_entry
from hamcrest import has_length
from hamcrest import assert_that
from hamcrest import has_entries

from zope import component

from nti.badges.interfaces import IBadgeClass

from nti.app.products.courseware_badges.courses import get_course_badges
from nti.app.products.courseware_badges.interfaces import ICatalogEntryBadgeCache

from nti.contenttypes.courses.interfaces import ICourseCatalog

from nti.app.products.courseware_badges.tests import CourseBadgesApplicationTestLayer

from nti.app.testing.application_webtest import ApplicationLayerTest

from nti.app.testing.decorators import WithSharedApplicationMockDS

import nti.dataserver.tests.mock_dataserver as mock_dataserver
from nti.dataserver.tests.mock_dataserver import WithMockDSTrans

class TestCourses(ApplicationLayerTest):

	layer = CourseBadgesApplicationTestLayer
	
	default_origin = str('http://janux.ou.edu')
	
	enrolled_courses_href =  '/dataserver2/users/sjohnson@nextthought.com/Courses/EnrolledCourses'
	
	def _populate_cache(self):
		with mock_dataserver.mock_db_trans(self.ds, site_name='platform.ou.edu'):
			catalog = component.getUtility(ICourseCatalog)
			for entry in catalog.iterCatalogEntries():
				cache = component.getUtility(ICatalogEntryBadgeCache)
				cache.build(entry)
				
	@WithMockDSTrans
	def test_get_course_badges(self):
		courseId = 'tag:nextthought.com,2011-10:OU-HTML-CLC3403_LawAndJustice.clc_3403_law_and_justice'
		badges = get_course_badges(courseId)
		assert_that(badges, has_length(1))

	@WithSharedApplicationMockDS(users=True, testapp=True)
	def test_course_earnable_badges(self):
				
		self._populate_cache()
			
		self.testapp.post_json(self.enrolled_courses_href, 'CLC 3403', status=201)
	
		earned_badges_path = '/dataserver2/users/sjohnson%40nextthought.com/Badges/EarnableBadges'
		res = self.testapp.get(earned_badges_path,
						  	   status=200)
		assert_that(res.json_body, 
					has_entry(u'Items', has_item(has_entries('Class', 'Badge',
															 'Type', 'Course'))) )

		ntiid = 'tag:nextthought.com,2011-10:OU-HTML-CLC3403_LawAndJustice.clc_3403_law_and_justice'
		badges = get_course_badges(ntiid)
		assert_that(badges, has_length(1))

		cp = IBadgeClass(badges[0], None)
		assert_that(cp, is_not(none()))
