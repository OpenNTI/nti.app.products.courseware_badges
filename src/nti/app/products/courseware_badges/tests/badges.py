#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

# disable: accessing protected members, too many methods
# pylint: disable=W0212,R0904

def generate_db(database):

	issuer_id = database.add_issuer(name=u'Janux',
									origin=u'http://janux.ou.edu',
								    org=u'http://www.ou.edu',
								    contact=u'janux@ou.edu')

	database.add_badge(name=u'tag:nextthought.com,2011-10:OU-HTML-CLC3403_LawAndJustice.completion_badge',
					   image=u'http://janux.ou.edu/bages/CLC3403_LawAndJustice_fall2013_completion_badge.png',
					   desc=u'Chemistry of beer course completion',
					   criteria=u'http://janux.ou.edu/bages/chem4970.fall2013.html',
					   issuer_id=issuer_id,
					   tags='beer,chemistry')
		
	database.add_person(email=u'sjohnson@nextthought.com',
						nickname='sjohnson@nextthought.com',
						website='http://www.nextthought.com/persons/sjohnson.htm',
						bio=u'I am Steve')

	return database
