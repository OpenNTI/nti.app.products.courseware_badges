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
					   desc=u'Law and Justice Course Completion',
					   criteria=u'http://janux.ou.edu/bages/CLC3403.fall2013.html',
					   issuer_id=issuer_id,
					   tags='law,justice')

	database.add_badge(name=u'tag:nextthought.com,2011-10:OU-HTML-CHEM4970_Chemistry_of_Beer.completion_badge',
					   image=u'http://pngimg.com/upload/beer_PNG2390.png',
					   desc=u'Chemistry of Beer Course Completion',
					   criteria=u'http://janux.ou.edu/bages/CHEM4970.Spring2014.html',
					   issuer_id=issuer_id,
					   tags='beer,chemistry')
		
	database.add_person(email=u'sjohnson@nextthought.com',
						nickname='sjohnson@nextthought.com',
						website='http://www.nextthought.com/persons/sjohnson.htm',
						bio=u'I am Steve')

	return database
