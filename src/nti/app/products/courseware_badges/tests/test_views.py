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

from nti.app.products.courseware_badges.tests import CourseBadgesApplicationTestLayer

from nti.app.testing.application_webtest import ApplicationLayerTest

from nti.app.testing.decorators import WithSharedApplicationMockDS

class TestViews(ApplicationLayerTest):

	layer = CourseBadgesApplicationTestLayer

	default_origin = str('http://janux.ou.edu')
	
	@WithSharedApplicationMockDS(users=True, testapp=True)
	def test_course_badges(self):
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
