#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

# disable: accessing protected members, too many methods
# pylint: disable=W0212,R0904

from hamcrest import has_entry
from hamcrest import has_length
from hamcrest import assert_that
from hamcrest import greater_than

from nti.app.products.courseware_badges.tests import CourseBadgesApplicationTestLayer

from nti.app.testing.application_webtest import ApplicationLayerTest

from nti.app.testing.decorators import WithSharedApplicationMockDS

class TestCourses(ApplicationLayerTest):

	layer = CourseBadgesApplicationTestLayer

	@WithSharedApplicationMockDS(users=True, testapp=True, default_authenticate=True)
	def test_course_legacy_badges(self):

		extra_env = self.testapp.extra_environ or {}
		extra_env.update({b'HTTP_ORIGIN': b'http://janux.ou.edu'})
		self.testapp.extra_environ = extra_env

		# enroll in the course using its purchasable id
		courseId = 'tag:nextthought.com,2011-10:OU-course-CLC3403LawAndJustice'
		environ = self._make_extra_environ()
		environ[b'HTTP_ORIGIN'] = b'http://platform.ou.edu'

		path = '/dataserver2/store/enroll_course'
		data = {'courseId': courseId}
		self.testapp.post_json(path, data, extra_environ=environ)

		res = self.testapp.get('/dataserver2/users/sjohnson@nextthought.com/Courses/EnrolledCourses')
		assert_that(res.json_body, has_entry('Items', has_length(1)))

		earned_badges_path = '/dataserver2/users/sjohnson%40nextthought.com/Badges/EarnableBadges'
		res = self.testapp.get(earned_badges_path,
						  	   extra_environ=environ,
						  	   status=200)
		assert_that(res.json_body, has_entry(u'Items', has_length(greater_than(0))))
