#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from zope import component

from zope.intid.interfaces import IIntIds

from nti.app.products.courseware_badges import get_course_badges_catalog

from nti.contenttypes.courses.interfaces import ICourseInstance
from nti.contenttypes.courses.interfaces import ICourseVendorInfoSynchronized

logger = __import__('logging').getLogger(__name__)


@component.adapter(ICourseInstance, ICourseVendorInfoSynchronized)
def _course_instance_available(course, unused_event=None):
    catalog = get_course_badges_catalog()
    if catalog is not None:
        intids = component.getUtility(IIntIds)
        doc_id = intids.queryId(course)
        if doc_id is not None:
            catalog.index_doc(doc_id, course)
