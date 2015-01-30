#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

# disable: accessing protected members, too many methods
# pylint: disable=W0212,R0904

import os
import shutil
import tempfile

from zope import component

from nti.badges.interfaces import IBadgeManager
from nti.badges.tahrir.manager import create_badge_manager

from nti.app.products.courseware_badges.tests.badges import generate_db

from nti.testing.layers import GCLayerMixin
from nti.testing.layers import ZopeComponentLayer
from nti.testing.layers import ConfiguringLayerMixin
# 
from nti.dataserver.tests.mock_dataserver import DSInjectorMixin

import zope.testing.cleanup

def _change_ds_dir(cls):
	cls.old_data_dir = os.getenv('DATASERVER_DATA_DIR')
	cls.new_data_dir = tempfile.mkdtemp(dir="/tmp")
	os.environ['DATASERVER_DATA_DIR'] = cls.new_data_dir

def _restore_ds_dir(cls):
	shutil.rmtree(cls.new_data_dir, True)
	os.environ['DATASERVER_DATA_DIR'] = cls.old_data_dir or '/tmp'

def _register_sample(cls):
	import transaction
	with transaction.manager:
		cls.old = component.getUtility(IBadgeManager)
		bm = create_badge_manager(defaultSQLite=True)
		generate_db(bm.db)
		component.provideUtility(bm, IBadgeManager)
		
class SharedConfiguringTestLayer(ZopeComponentLayer,
								 GCLayerMixin,
								 ConfiguringLayerMixin,
								 DSInjectorMixin):

	set_up_packages = ('nti.dataserver',
					   'nti.app.client_preferences',
					   'nti.app.products.courseware_badges')

	@classmethod
	def setUp(cls):
		cls.setUpPackages()
		_change_ds_dir(cls)
		_register_sample(cls)

	@classmethod
	def tearDown(cls):
		cls.tearDownPackages()
		zope.testing.cleanup.cleanUp()
		_restore_ds_dir(cls)

	@classmethod
	def testSetUp(cls, test=None):
		cls.setUpTestDS(test)

	@classmethod
	def testTearDown(cls):
		pass

import unittest

class CourseBadgesTestCase(unittest.TestCase):
	layer = SharedConfiguringTestLayer

from nti.app.products.courseware.tests import NotInstructedCourseApplicationTestLayer

class CourseBadgesApplicationTestLayer(NotInstructedCourseApplicationTestLayer):

	_create_user = False
	
	@classmethod
	def setUp(cls):
		_change_ds_dir(cls)
		_register_sample(cls)
		
	@classmethod
	def tearDown(cls):
		_restore_ds_dir(cls)
