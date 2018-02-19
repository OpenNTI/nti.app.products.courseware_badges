#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

# pylint: disable=protected-access,too-many-public-methods,arguments-differ

from hamcrest import assert_that
from hamcrest import has_entries

from nti.app.products.courseware_badges.tests import CourseBadgesApplicationTestLayer

from nti.app.testing.application_webtest import ApplicationLayerTest

from nti.app.testing.decorators import WithSharedApplicationMockDS


class TestPreferencesViews(ApplicationLayerTest):

    layer = CourseBadgesApplicationTestLayer

    @WithSharedApplicationMockDS(users=True, testapp=True)
    def test_traverse_to_my_root_prefs(self):
        res = self._fetch_user_url('/++preferences++')
        assert_that(res.json_body,
                    has_entries({'Class': 'Preference_Root',
                                 'href': '/dataserver2/users/sjohnson@nextthought.COM/++preferences++',
                                 'Badges': has_entries({'Class': 'Preference_Badges',
                                                        'MimeType': 'application/vnd.nextthought.preference.badges',
                                                        'Course': {'Class': 'Preference_Badges_Course',
                                                                   'MimeType': 'application/vnd.nextthought.preference.badges.course',
                                                                   'show_course_badges': False}})}))
