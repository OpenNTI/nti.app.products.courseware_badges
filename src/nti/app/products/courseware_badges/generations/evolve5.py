#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from zope import component
from zope import interface

from zope.catalog.interfaces import ICatalog

from zope.component.hooks import site as current_site

from zope.intid.interfaces import IIntIds

from nti.app.products.courseware_badges.index import COURSE_BADGES_CATALOG_NAME

from nti.dataserver.interfaces import IDataserver
from nti.dataserver.interfaces import IOIDResolver

generation = 5

logger = __import__('logging').getLogger(__name__)


@interface.implementer(IDataserver)
class MockDataserver(object):

    root = None

    def get_by_oid(self, oid, ignore_creator=False):
        resolver = component.queryUtility(IOIDResolver)
        if resolver is None:
            logger.warn("Using dataserver without a proper ISiteManager.")
        else:
            return resolver.get_object_by_oid(oid, ignore_creator=ignore_creator)
        return None


def do_evolve(context, generation=generation):  # pylint: disable=redefined-outer-name
    conn = context.connection
    ds_folder = conn.root()['nti.dataserver']

    mock_ds = MockDataserver()
    mock_ds.root = ds_folder
    component.provideUtility(mock_ds, IDataserver)

    with current_site(ds_folder):
        assert component.getSiteManager() == ds_folder.getSiteManager(), \
               "Hooks not installed?"

        lsm = ds_folder.getSiteManager()
        intids = lsm.getUtility(IIntIds)
        badge_catalog = lsm.queryUtility(ICatalog, name=COURSE_BADGES_CATALOG_NAME)
        if badge_catalog is not None:
            for idx in badge_catalog.values():
                intids.unregister(idx)
            lsm.unregisterUtility(provided=ICatalog, name=COURSE_BADGES_CATALOG_NAME)
            intids.unregister(badge_catalog)

    component.getGlobalSiteManager().unregisterUtility(mock_ds, IDataserver)
    logger.info('Evolution %s done.', generation)


def evolve(context):
    """
    Evolve to generation 5 by removing the badge catalog.
    """
    do_evolve(context, generation)
