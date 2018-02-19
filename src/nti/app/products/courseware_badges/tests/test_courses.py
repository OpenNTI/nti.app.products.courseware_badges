#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

# pylint: disable=protected-access,too-many-public-methods,arguments-differ

from hamcrest import none
from hamcrest import is_not
from hamcrest import has_item
from hamcrest import has_entry
from hamcrest import has_length
from hamcrest import assert_that
from hamcrest import has_entries

from zope import component

from zope.intid.interfaces import IIntIds

from nti.app.products.courseware_badges import get_course_badges_catalog

from nti.app.products.courseware_badges.utils import get_course_badges

from nti.app.products.courseware_badges.tests import CourseBadgesApplicationTestLayer

from nti.app.testing.application_webtest import ApplicationLayerTest

from nti.app.testing.decorators import WithSharedApplicationMockDS

from nti.badges.interfaces import IBadgeClass

from nti.contenttypes.courses.interfaces import ICourseCatalog
from nti.contenttypes.courses.interfaces import ICourseInstance

from nti.dataserver.tests import mock_dataserver

from nti.dataserver.tests.mock_dataserver import WithMockDSTrans


class TestCourses(ApplicationLayerTest):

    layer = CourseBadgesApplicationTestLayer

    default_origin = 'http://janux.ou.edu'

    enrolled_courses_href = '/dataserver2/users/sjohnson@nextthought.com/Courses/EnrolledCourses'

    def _populate_cache(self):
        with mock_dataserver.mock_db_trans(self.ds, site_name='platform.ou.edu'):
            catalog = component.getUtility(ICourseCatalog)
            intids = component.getUtility(IIntIds)
            badges_catalog = get_course_badges_catalog()
            for entry in catalog.iterCatalogEntries():
                course = ICourseInstance(entry)
                doc_id = intids.queryId(course)
                if doc_id is not None:
                    badges_catalog.index_doc(doc_id, course)

    @WithMockDSTrans
    def test_get_course_badges(self):
        courseId = 'tag:nextthought.com,2011-10:OU-HTML-CLC3403_LawAndJustice.clc_3403_law_and_justice'
        badges = get_course_badges(courseId)
        assert_that(badges, has_length(1))

    @WithSharedApplicationMockDS(users=True, testapp=True)
    def test_course_earnable_badges(self):

        self._populate_cache()

        self.testapp.post_json(self.enrolled_courses_href,
                               'tag:nextthought.com,2011-10:NTI-CourseInfo-Fall2013_CLC3403_LawAndJustice',
                               status=201)

        earned_badges_path = '/dataserver2/users/sjohnson%40nextthought.com/Badges/EarnableBadges'
        res = self.testapp.get(earned_badges_path,
                               status=200)
        assert_that(res.json_body,
                    has_entry('Items', has_item(has_entries('Class', 'Badge',
                                                            'Type', 'Course'))))

        ntiid = 'tag:nextthought.com,2011-10:OU-HTML-CLC3403_LawAndJustice.clc_3403_law_and_justice'
        badges = get_course_badges(ntiid)
        assert_that(badges, has_length(1))

        cp = IBadgeClass(badges[0], None)
        assert_that(cp, is_not(none()))
