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

from nti.app.products.badges.interfaces import SC_BADGE_EARNED

from nti.app.products.courseware_badges.courses import get_badge_catalog_entries

from nti.app.products.courseware_badges.utils import base_root_ntiid
from nti.app.products.courseware_badges.utils import find_catalog_entry
from nti.app.products.courseware_badges.utils import get_base_image_filename
from nti.app.products.courseware_badges.utils import is_course_badge_filename

from nti.appserver.interfaces import ITrustedTopLevelContainerContextProvider

from nti.badges.interfaces import IBadgeClass
from nti.badges.interfaces import IBadgeAssertion

from nti.contenttypes.courses.interfaces import ICourseCatalog
from nti.contenttypes.courses.interfaces import ICourseInstance
from nti.contenttypes.courses.interfaces import ICourseCatalogEntry

from nti.dataserver.interfaces import IStreamChangeEvent

logger = __import__('logging').getLogger(__name__)


def _compare_pseudo_ntiids(a, b):
    if a and b:
        a_trx = a.replace(':', '_').replace(',', '_')
        b_trx = b.replace(':', '_').replace(',', '_')
        return a_trx == b_trx
    return False


def find_catalog_entry_from_badge(badge):
    # check directly by source
    try:
        ntiid = badge.SourceNTIID
        result = find_catalog_entry(ntiid) if ntiid else None
        if result is not None:
            return result
    except AttributeError:  # pragma: no cover
        pass

    # use index
    result = get_badge_catalog_entries(badge.name)
    if result:  # return first
        return result[0]

    # check badge file name (legacy)
    filename = get_base_image_filename(badge)
    if is_course_badge_filename(filename):
        # remove subtype from NTIID, filename is not a valid NTIID
        ntiid_root = '.'.join(filename.split('.')[0:-1])
        # search catalog entries
        catalog = component.getUtility(ICourseCatalog)
        for entry in catalog.iterCatalogEntries():
            # collect all possible matching ntiids
            ntiids = {getattr(entry, 'ntiid', None)}
            course = ICourseInstance(entry, None)
            if course is not None:
                # for legacy badges get the ntiids of the content packages
                try:
                    bld = course.ContentPackageBundle
                    ntiids.add(getattr(bld, 'ntiid', None))
                    ntiids.add(getattr(bld, 'ContentPackageNTIID', None))
                    ntiids.update(p.ntiid for p in bld.ContentPackages or ())
                except AttributeError:  # pragma: no cover
                    pass
            ntiids.discard(None)
            for ntiid in ntiids:
                if _compare_pseudo_ntiids(ntiid_root, base_root_ntiid(ntiid)):
                    return entry
    return None


@component.adapter(IBadgeClass)
@interface.implementer(ICourseCatalogEntry)
def badge_to_course_catalog_entry(badge):
    result = find_catalog_entry_from_badge(badge)
    return result


@component.adapter(IBadgeAssertion)
@interface.implementer(ITrustedTopLevelContainerContextProvider)
def _trusted_context_from_assertion(assertion):
    badge = IBadgeClass(assertion)
    catalog_entry = find_catalog_entry_from_badge(badge)
    return (catalog_entry,) if catalog_entry is not None else ()


@component.adapter(IStreamChangeEvent)
@interface.implementer(ITrustedTopLevelContainerContextProvider)
def _trusted_context_from_change(obj):
    obj_type = getattr(obj, 'type', '')
    obj = getattr(obj, 'object', None)
    if obj_type == SC_BADGE_EARNED and obj is not None:
        return _trusted_context_from_assertion(obj)
