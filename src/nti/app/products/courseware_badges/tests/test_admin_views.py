#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

# pylint: disable=protected-access,too-many-public-methods,arguments-differ

from hamcrest import has_entry
from hamcrest import has_length
from hamcrest import assert_that

from zope import component

from zope.intid.interfaces import IIntIds

from nti.app.products.courseware_badges import get_course_badges_catalog

from nti.app.products.courseware_badges.tests import CourseBadgesApplicationTestLayer

from nti.app.testing.application_webtest import ApplicationLayerTest

from nti.app.testing.decorators import WithSharedApplicationMockDS

from nti.contenttypes.courses.interfaces import ICourseCatalog
from nti.contenttypes.courses.interfaces import ICourseInstance

from nti.dataserver.tests import mock_dataserver


class TestAdminViews(ApplicationLayerTest):

    layer = CourseBadgesApplicationTestLayer

    default_origin = 'http://janux.ou.edu'

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

    @WithSharedApplicationMockDS(users=True, testapp=True)
    def test_views(self):
        # Since we plug our badges in after course layer is synced, we
        # need to rebuild our cache here.
        self._populate_cache()

        get_path = '/dataserver2/BadgeAdmin/CourseBadgeCache'
        res = self.testapp.get(get_path)
        assert_that(res.json_body, has_entry('Items', has_length(3)))

        rebuild_path = '/dataserver2/BadgeAdmin/RebuildCourseBadgeCache'
        self.testapp.post(rebuild_path, status=204)

        get_path = '/dataserver2/BadgeAdmin/CourseBadgeCache'
        res = self.testapp.get(get_path)
        assert_that(res.json_body, has_entry('Items', has_length(3)))
