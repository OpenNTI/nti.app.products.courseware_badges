#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

import os
import re
import six
from collections import Mapping

from zope import component

from zope.proxy import ProxyBase

from zope.traversing.api import traverse

from pyramid.compat import is_nonstr_iter

from nti.app.products.courseware_badges import get_all_badges

from nti.app.products.courseware_badges.interfaces import COURSE_COMPLETION
from nti.app.products.courseware_badges.interfaces import COURSE_BADGE_TYPES

from nti.badges.openbadges.interfaces import IBadgeClass

from nti.contentlibrary.interfaces import IRenderableContentPackage

from nti.contenttypes.courses import get_course_vendor_info

from nti.contenttypes.courses.common import get_course_packages

from nti.contenttypes.courses.interfaces import ICourseCatalog
from nti.contenttypes.courses.interfaces import ICourseInstance
from nti.contenttypes.courses.interfaces import ICourseSubInstance
from nti.contenttypes.courses.interfaces import ICourseCatalogEntry

from nti.contenttypes.courses.utils import get_parent_course

from nti.ntiids.ntiids import get_parts
from nti.ntiids.ntiids import make_ntiid
from nti.ntiids.ntiids import is_valid_ntiid_string
from nti.ntiids.ntiids import find_object_with_ntiid

ROOT = "tag:nextthought.com,2011-10:"
SAFE_ROOT = ROOT.replace(':', '_').replace(',', '_')


def base_root_ntiid(ntiid):
    """
    return the 'root' ntiid of a source ntiid. That is, we remove from the NTIID-source
    specific part anything after the first period (.)  so from
    tag:nextthought.com,2011-10:OU-HTML-CLC3403_LawAndJustice.clc_3403_law_and_justice
    we get tag:nextthought.com,2011-10:OU-HTML-CLC3403_LawAndJustice
    """
    if ntiid and is_valid_ntiid_string(ntiid):
        parts = get_parts(ntiid)
        specfic = parts.specific.split('.')[0]
        result = make_ntiid(provider=parts.provider,
                            nttype=parts.nttype,
                            specific=specfic,
                            base=parts.date)
        return result
    return None


def get_base_image_filename(badge):
    """
    return the image file name w/ no ext
    """
    image = IBadgeClass(badge).image
    filename = os.path.basename(image) if image else None
    if filename and filename.lower().endswith('.png'):
        filename = os.path.splitext(filename)[0]
        if not filename.startswith(SAFE_ROOT):
            filename = SAFE_ROOT + filename
    return filename

type_pattern = re.compile("course_(.+)_badge", re.I | re.U)


def get_badge_type_from_filename(filename):
    """
    return if the badge type using the file name
    """
    m = type_pattern.match(filename)
    if m is not None:
        result = m.groups()[0].lower()
    else:
        result = COURSE_COMPLETION
    return result


def get_badge_type(badge):
    """
    return if the type of the specfied badge using is image file name
    """
    filename = get_base_image_filename(badge)
    result = get_badge_type_from_filename(filename)
    return result

filename_pattern = re.compile("(.+\.course_.+_badge$)|(.+\.course_badge$)",
                              re.I | re.U)


def is_course_badge_filename(filename):
    """
    return if the specified filename correspond to a course badge
    """
    result = filename_pattern.match(filename) if filename else None
    return True if result else False


def is_course_badge(badge):
    """
    return if the specified badge is a couse badge using the badge image filename
    """
    filename = get_base_image_filename(badge)
    result = is_course_badge_filename(filename)
    return result

_all_badge_types = tuple('course_%s_badge' % x for x in COURSE_BADGE_TYPES) + \
                   ('course_badge',)


def find_course_badges_from_entry(context):
    """
    scan the vendor info from the specified course and return the element
    at the NTI/Badges entry
    """
    course = ICourseInstance(context, None)
    vendor_info = get_course_vendor_info(course, False) or {}
    result = traverse(vendor_info, 'NTI/Badges', default=None)
    return result


class CourseBadgeProxy(ProxyBase):

    SourceNTIID = property(
        lambda s: s.__dict__.get('_v_catalog_source_ntiid'),
        lambda s, v: s.__dict__.__setitem__('_v_catalog_source_ntiid', v))

    def __new__(cls, base, ntiid):
        return ProxyBase.__new__(cls, base)

    def __init__(self, base, ntiid):
        ProxyBase.__init__(self, base)
        self.SourceNTIID = ntiid


def proxy(badge, ntiid):
    return CourseBadgeProxy(badge, ntiid)


def catalog_entry(context):
    return ICourseCatalogEntry(context, None)


def find_catalog_entry(iden):
    result = find_object_with_ntiid(iden)
    result = ICourseCatalogEntry(result, None)
    if result is None:
        try:
            catalog = component.queryUtility(ICourseCatalog)
            result = catalog.getCatalogEntry(iden)
        except KeyError:
            result = None
    return result


def get_course_badges_map(context):
    badges = find_course_badges_from_entry(context)
    if not isinstance(badges, Mapping):
        if isinstance(badges, six.string_types):
            # a single string it's the badge name
            badges = {badges: COURSE_COMPLETION}
        elif is_nonstr_iter(badges):
            # a list of badge names
            badges = {x: COURSE_COMPLETION for x in badges}
        else:  # can't resolve
            badges = dict()
    return badges


def get_course_badges(course_iden):
    # CS: We want to make sure we always query the badges from the DB
    # in order to return new objects all the time, so they can be
    # proxied appropriately for the course in case multiple courses
    # shared a badge/
    # TODO: Change code to avoid getting all badges
    return find_course_badges_from_badges(course_iden, get_all_badges())


def entry_ntiid(context):
    entry = catalog_entry(context)
    result = entry.ntiid if entry is not None else None
    return result


def get_all_context_badges(context):
    result = []
    entry = ICourseCatalogEntry(context, None)
    course = ICourseInstance(context, None)
    if entry is not None:
        result.extend(get_course_badges(entry.ntiid))
    if not result and ICourseSubInstance.providedBy(course):
        # if no badges for subinstance then check main course
        entry = ICourseCatalogEntry(get_parent_course(course), None)
        if entry is not None:
            result.extend(get_course_badges(entry.ntiid))
    # for legacy badges scan the content packages
    if not result and course is not None:
        for pack in get_course_packages(course):
            if not IRenderableContentPackage.providedBy(pack):
                result.extend(get_course_badges(pack.ntiid))
    return result


def find_course_badges_from_badges(source_ntiid, source_badges=()):
    """
    return all course badges from the specified source ntiid from
    the badge source iterable
    """

    # 1. if the source_ntiid is a catalog entry ntiid, we look at the course
    # vendor info (e.g. NTI/Badges) to find the badge names.
    result = []
    entry = find_catalog_entry(source_ntiid)
    if entry is not None:
        badges = get_course_badges_map(entry)
        # make sure the badge ids in vendor-info are valid
        for badge in source_badges or ():
            ntiid = get_base_image_filename(badge)
            if badge.name in badges or ntiid in badges:
                result.append(proxy(badge, source_ntiid))
        if result:
            return result

    if not is_valid_ntiid_string(source_ntiid):
        return result

    # 2. otherwise we use the badge image file names to determined a course badge.
    # The image file name of a course badge is 'root' course/content package NTIID plus
    # a period (.) plus course_{type}_badge
    # e.g tag_nextthought.com_2011-10_OU-HTML-CLC3403_LawAndJustice.course_completion_badge.png
    # that is the completion badge of the
    # tag:nextthought.com,2011-10:OU-HTML-CLC3403_LawAndJustice course

    # This is LEGACY code
    # build possible ntiids based in the course entry ntiid
    badge_ntiids = set()
    parts = get_parts(source_ntiid)
    pre_specfic = '.'.join(parts.specific.split('.')[0:-1]) or parts.specific
    for subtype in _all_badge_types:
        specfic = '%s.%s' % (pre_specfic, subtype)
        name = make_ntiid(provider=parts.provider,
                          nttype=parts.nttype,
                          specific=specfic,
                          base=parts.date)
        badge_ntiids.add(name.replace(':', '_').replace(',', '_'))

    # check built ntiids against badge file name(s)
    for badge in source_badges:
        ntiid = get_base_image_filename(badge)
        if ntiid in badge_ntiids:
            result.append(proxy(badge, source_ntiid))
    return result
