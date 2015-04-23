#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

# disable: accessing protected members, too many methods
# pylint: disable=W0212,R0904

from hamcrest import has_item
from hamcrest import has_entry
from hamcrest import has_length
from hamcrest import has_entries
from hamcrest import assert_that

import fudge

from zope import component

from nti.app.products.courseware_badges.interfaces import ICatalogEntryBadgeCache

from nti.contenttypes.courses.interfaces import ICourseCatalog

from nti.dataserver.users import User

from nti.app.products.courseware_badges.tests import CourseBadgesApplicationTestLayer

from nti.app.testing.application_webtest import ApplicationLayerTest

import nti.dataserver.tests.mock_dataserver as mock_dataserver
from nti.app.testing.decorators import WithSharedApplicationMockDS

class TestViews(ApplicationLayerTest):

	layer = CourseBadgesApplicationTestLayer

	default_origin = str('http://janux.ou.edu')
	enrolled_courses_href = '/dataserver2/users/sjohnson@nextthought.com/Courses/EnrolledCourses'

	def _populate_cache(self):
		with mock_dataserver.mock_db_trans(self.ds, site_name='platform.ou.edu'):
			catalog = component.getUtility(ICourseCatalog)
			for entry in catalog.iterCatalogEntries():
				cache = component.getUtility(ICatalogEntryBadgeCache)
				cache.build(entry)
				
	@WithSharedApplicationMockDS(users=True, testapp=True)
	@fudge.patch('nti.app.products.courseware_badges.views.show_course_badges')
	@fudge.patch('nti.app.products.courseware_badges.courses.show_course_badges')
	def test_course_badges(self, mock_scb_1, mock_scb_2):
		# populate cache because badges are loaded after the library 
		self._populate_cache()
		
		mock_scb_1.is_callable().with_args().returns(False)
		mock_scb_2.is_callable().with_args().returns(False)
		
		entry_href = '/dataserver2/%2B%2Betc%2B%2Bhostsites/platform.ou.edu/%2B%2Betc%2B%2Bsite/Courses/Fall2013/CLC3403_LawAndJustice/Badges'
		res = self.testapp.get(entry_href)
		assert_that(res.json_body, has_entry('Items', has_length(1)))

		item = res.json_body['Items'][0]
		assert_that(item, has_entry('Type', 'Course'))

		res = self.testapp.get('/dataserver2/%2B%2Betc%2B%2Bhostsites/platform.ou.edu/%2B%2Betc%2B%2Bsite/Courses/Fall2013/CLC3403_LawAndJustice')
		assert_that(res.json_body,
					has_entries('Class', 'CourseInstance',
								'Links', has_item(has_entries('rel', 'Badges',
															  'href', entry_href))))

		path = '/dataserver2/users/sjohnson%40nextthought.com/EarnedCourseBadges'
		res = self.testapp.get(path)
		assert_that(res.json_body, has_entry('Items', has_length(0)))

		# enroll
		self.testapp.post_json( self.enrolled_courses_href,
								'CLC 3403',
								status=201 )
		
		path = '/dataserver2/users/sjohnson%40nextthought.com/Badges/EarnableBadges'
		res = self.testapp.get(path)
		assert_that(res.json_body, has_entry('Items', has_length(1)))
		
		# and award
		name = 'Law and Justice'
		award_badge_path = '/dataserver2/BadgeAdmin/@@award'
		self.testapp.post_json(award_badge_path,
							   {"username":self.default_username,
								"badge":name},
							   status=200)

		path = '/dataserver2/users/sjohnson%40nextthought.com/EarnedCourseBadges'
		res = self.testapp.get(path)
		assert_that(res.json_body, has_entry('Items', has_length(1)))
		
		# new user
		with mock_dataserver.mock_db_trans(self.ds):
			ds = mock_dataserver.current_mock_ds
			User.create_user(ds, username="ichigo", password="temp001")
		enrolled = '/dataserver2/users/ichigo/Courses/EnrolledCourses'
		self.testapp.post_json( enrolled,
								'CLC 3403',
								status=201,
								extra_environ=self._make_extra_environ("ichigo") )
		
		# cannot see it
		path = '/dataserver2/users/sjohnson%40nextthought.com/EarnedCourseBadges'
		res = self.testapp.get(path, extra_environ=self._make_extra_environ("ichigo"))
		assert_that(res.json_body, has_entry('Items', has_length(0)))
		
		mock_scb_1.is_callable().with_args().returns(True)
		mock_scb_2.is_callable().with_args().returns(True)
		
		img_url = 'http://localhost/hosted_badge_images/tag_nextthought.com_2011-10_OU-HTML-CLC3403_LawAndJustice.course_badge.png'
		# now it can
		path = '/dataserver2/users/sjohnson%40nextthought.com/EarnedCourseBadges'
		res = self.testapp.get(path, extra_environ=self._make_extra_environ("ichigo"))
		assert_that(res.json_body, has_entry('Items', has_length(1)))
		assert_that(res.json_body, has_entry('Items', 
											 has_item(has_entry('image', img_url))))
		
		path = '/dataserver2/users/sjohnson%40nextthought.com/Badges/EarnedBadges'
		res = self.testapp.get(path, extra_environ=self._make_extra_environ("ichigo"))
		assert_that(res.json_body, has_entry('Items', has_length(1)))
		assert_that(res.json_body, has_entry('Items', 
											 has_item(has_entries('href', '/dataserver2/OpenBadges/Law%20and%20Justice',
																  'Type', 'Course',
																  'image', img_url))))
		
