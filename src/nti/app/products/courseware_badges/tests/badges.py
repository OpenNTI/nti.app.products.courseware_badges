#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

# disable: accessing protected members, too many methods
# pylint: disable=W0212,R0904

def generate_db(database):

	issuer_id = database.add_issuer(name=u'Janux',
									origin=u'https://janux.ou.edu',
								    org=u'http://www.ou.edu',
								    contact=u'janux@ou.edu')

	database.add_badge(name=u'Law and Justice',
					   image=u'tag_nextthought.com_2011-10_OU-HTML-CLC3403_LawAndJustice.course_badge.png',
					   desc=u'Law and Justice',
					   criteria=u'http://janux.ou.edu/bages/CLC3403.fall2013.html',
					   issuer_id=issuer_id,
					   tags='law,justice')

	database.add_badge(name=u'Chemistry of Beer',
					   image=u'tag_nextthought.com_2011-10_OU-HTML-CHEM4970_Chemistry_of_Beer.course_badge.png',
					   desc=u'Chemistry of Beer',
					   criteria=u'http://janux.ou.edu/bages/CHEM4970.Spring2014.html',
					   issuer_id=issuer_id,
					   tags='beer,chemistry')
		
	database.add_badge(name=u'Power and Elegance of Computational Thinking',
					   image=u'tag_nextthought.com_2011-10_OU-HTML-CS1300_Power_and_Elegance_of_Computational_Thinking.course_badge.png',
					   desc=u'Power and Elegance of Computational Thinking',
					   criteria=u'https://janux.ou.edu/course.cs1300.html',
					   issuer_id=issuer_id,
					   tags='programming,computers,control')

	database.add_badge(name=u'History of Science',
					   image=u'tag_nextthought.com_2011-10_OU-HTML-HSCI3013_History_of_Science.course_badge.png',
					   desc=u'History of Science',
					   criteria=u'https://janux.ou.edu/course.hsci3013.html',
					   issuer_id=issuer_id,
					   tags='history,science')

	database.add_badge(name=u'Hydraulic Fracturing',
					   image=u'tag_nextthought.com_2011-10_OU-HTML-GEOG3890_Hydraulic_Fracturing_and_Water_Resources.course_badge.png',
					   desc=u'Hydraulic Fracturing and Water Resources',
					   criteria=u'https://janux.ou.edu/course.geog3890.html',
					   issuer_id=issuer_id,
					   tags='fracturing,hydraulic,water')

	database.add_person(email=u'sjohnson@nextthought.com',
						nickname='sjohnson@nextthought.com',
						website='http://www.nextthought.com/persons/sjohnson.htm',
						bio=u'I am Steve')

	return database


