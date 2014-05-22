#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

# disable: accessing protected members, too many methods
# pylint: disable=W0212,R0904

from hamcrest import assert_that
from hamcrest import has_property

from nti.dataserver.users import User

from nti.badges.tahrir import interfaces as tahrir_interfaces
from nti.badges.openbadges import interfaces as open_interfaces

import nti.dataserver.tests.mock_dataserver as mock_dataserver
from nti.dataserver.tests.mock_dataserver import WithMockDSTrans

from nti.app.products.badges.tests import NTIBadgesTestCase

class TestAdapters(NTIBadgesTestCase):

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
	def test_user_to_io(self):
		user = self._create_user()
		io = open_interfaces.IIdentityObject(user)
		assert_that(io, has_property('identity', 'ntiuser'))

	@WithMockDSTrans
	def test_user_2_person_2_io(self):
		user = self._create_user()
		person = tahrir_interfaces.IPerson(user)
		assert_that(person, has_property('email', 'ntiuser'))
		assert_that(person, has_property('nickname', 'ntiuser'))
		assert_that(person, has_property('bio', 'my bio'))
		assert_that(person, has_property('website', 'http://www.foo.com'))

		io = open_interfaces.IIdentityObject(person)
		assert_that(io, has_property('identity', u'ntiuser'))
