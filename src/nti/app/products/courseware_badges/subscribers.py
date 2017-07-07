#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from zope import component

from zope.intid.interfaces import IIntIds

from nti.app.products.courseware_badges import get_course_badges_catalog

from nti.contenttypes.courses.interfaces import ICourseInstance
from nti.contenttypes.courses.interfaces import ICourseVendorInfoSynchronized


@component.adapter(ICourseInstance, ICourseVendorInfoSynchronized)
def _course_instance_available(course, _):
    catalog = get_course_badges_catalog()
    if catalog is not None:
        intids = component.getUtility(IIntIds)
        doc_id = intids.queryId(course)
        if doc_id is not None:
            catalog.index_doc(doc_id, course)
