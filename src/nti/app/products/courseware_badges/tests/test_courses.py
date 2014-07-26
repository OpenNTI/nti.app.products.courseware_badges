#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

# disable: accessing protected members, too many methods
# pylint: disable=W0212,R0904

from hamcrest import is_
from hamcrest import none
from hamcrest import is_not
from hamcrest import has_entry
from hamcrest import has_length
from hamcrest import assert_that
from hamcrest import greater_than

from zope import component

from nti.badges import interfaces as badge_interfaces

from nti.app.products.courseware_badges import interfaces
from nti.app.products.courseware_badges import get_course_badges
from nti.app.products.courseware_badges.tests import CourseBadgesApplicationTestLayer

from nti.app.testing.application_webtest import ApplicationLayerTest

from nti.app.testing.decorators import WithSharedApplicationMockDS

class TestCourses(ApplicationLayerTest):

	layer = CourseBadgesApplicationTestLayer

	default_origin = str('http://janux.ou.edu')

	@WithSharedApplicationMockDS(users=True, testapp=True, default_authenticate=True)
	def test_course_earnable_badges(self):
		self.testapp.post_json('/dataserver2/users/sjohnson@nextthought.com/Courses/EnrolledCourses',
							   {'ntiid': 'tag:nextthought.com,2011-10:NTI-CourseInfo-Fall2013_CLC3403_LawAndJustice'})


		earned_badges_path = '/dataserver2/users/sjohnson%40nextthought.com/Badges/EarnableBadges'
		res = self.testapp.get(earned_badges_path,
						  	   extra_environ=environ,
						  	   status=200)
		assert_that(res.json_body, has_entry(u'Items', has_length(greater_than(0))))

		ntiid = 'tag:nextthought.com,2011-10:OU-HTML-CLC3403_LawAndJustice.clc_3403_law_and_justice'
		badges = get_course_badges(ntiid)
		assert_that(badges, has_length(1))

		cp = badge_interfaces.IBadgeClass(badges[0], None)
		assert_that(cp, is_not(none()))

		badge_map = component.getUtility(interfaces.ICourseBadgeMap)
		names = badge_map.get_badge_names(ntiid)
		assert_that(names, has_length(1))

		course_iden = badge_map.get_course_iden(names[0])
		assert_that(course_iden, is_(ntiid))
