#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

# disable: accessing protected members, too many methods
# pylint: disable=W0212,R0904

from hamcrest import assert_that
from hamcrest import has_entries

from nti.app.testing.application_webtest import ApplicationLayerTest
from nti.app.testing.decorators import WithSharedApplicationMockDS

from nti.app.products.courseware_badges.tests import CourseBadgesApplicationTestLayer

class TestPreferencesViews(ApplicationLayerTest):

	layer = CourseBadgesApplicationTestLayer

	@WithSharedApplicationMockDS(users=True,testapp=True)
	def test_traverse_to_my_root_prefs(self):
		res = self._fetch_user_url( '/++preferences++' )
		assert_that( res.json_body,
					 has_entries( {'Class': 'Preference_Root',
								   'href': '/dataserver2/users/sjohnson@nextthought.COM/++preferences++',
								   'Badges': has_entries({'Class': u'Preference_Badges',
														  u'MimeType': u'application/vnd.nextthought.preference.badges',
														  u'Course': {u'Class': u'Preference_Badges_Course',
            														  u'MimeType': u'application/vnd.nextthought.preference.badges.course',
														  			  u'show_course_badges': False}})}))

