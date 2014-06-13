#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

# disable: accessing protected members, too many methods
# pylint: disable=W0212,R0904

from hamcrest import has_length
from hamcrest import assert_that

from nti.app.products.courseware_badges import get_course_badges

from nti.app.products.courseware_badges.tests import CourseBadgesTestCase

from nti.dataserver.tests.mock_dataserver import WithMockDSTrans

class TestCoursewareBadges(CourseBadgesTestCase):

	@WithMockDSTrans
	def test_get_course_badges(self):
		courseId = 'tag:nextthought.com,2011-10:OU-HTML-CLC3403_LawAndJustice.clc_3403_law_and_justice'
		badges = get_course_badges(courseId)
		assert_that(badges, has_length(1))

