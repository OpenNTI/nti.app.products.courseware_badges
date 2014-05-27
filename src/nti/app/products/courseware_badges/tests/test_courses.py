#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

# disable: accessing protected members, too many methods
# pylint: disable=W0212,R0904

# from hamcrest import assert_that
# from hamcrest import has_property

from nti.dataserver.users import User

import nti.dataserver.tests.mock_dataserver as mock_dataserver
from nti.dataserver.tests.mock_dataserver import WithMockDSTrans

from nti.app.products.courseware_badges.tests import CourseBadgesTestCase

class TestCourses(CourseBadgesTestCase):

	def _create_user(self, username='ntiuser', password='temp001',
					 email='ntiuser@nti.com', alias='myalias',
					 home_page='http://www.foo.com',
					 about="my bio"):
		ds = mock_dataserver.current_mock_ds
		usr = User.create_user(ds, username=username, password=password,
							   external_value={'email': email, 'alias':alias,
											   'home_page':home_page,
											   'about':about})
		return usr


	@WithMockDSTrans
	def test_course_badges(self):
		pass

	@WithMockDSTrans
	def test_earnable_badges(self):
		self._create_user()
		pass
