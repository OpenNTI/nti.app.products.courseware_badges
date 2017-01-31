#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

# disable: accessing protected members, too many methods
# pylint: disable=W0212,R0904

from hamcrest import has_entry
from hamcrest import has_length
from hamcrest import assert_that

from zope import component

from zope.intid.interfaces import IIntIds

from nti.app.products.courseware_badges import get_course_badges_catalog

from nti.contenttypes.courses.interfaces import ICourseCatalog
from nti.contenttypes.courses.interfaces import ICourseInstance

from nti.app.products.courseware_badges.tests import CourseBadgesApplicationTestLayer

from nti.app.testing.application_webtest import ApplicationLayerTest

from nti.app.testing.decorators import WithSharedApplicationMockDS

from nti.dataserver.tests import mock_dataserver

class TestAdminViews(ApplicationLayerTest):

    layer = CourseBadgesApplicationTestLayer

    default_origin = b'http://janux.ou.edu'

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
