#!/usr/bin/env python
import unittest
import icetotgd
import datetime

class T(unittest.TestCase):

    fake_files = {
            'trivial.xml': '''<?xml version="1.0" encoding="ISO-8859-1"?>
<!DOCTYPE tv SYSTEM "http://iceguide.icetv.com.au/iceguide/iceguide.dtd">
<tv>
	<channel id="2300">
		<display-name>TwentyThree</display-name>
		<region-name>Melbourne</region-name>
		<lcn>23</lcn>
	</channel>
	<programme start="20091030110000 +0000" stop="20091030113000 +0000" channel="2300">
		<title lang="en">Spiderman</title>
		<sub-title lang="en">The One Where Spiderman Eats Salad</sub-title>
		<desc lang="en">Action is his reward.</desc>
		<category lang="en">News</category>
		<category lang="en">Sport</category>
		<episode-num system="icetv">169-0</episode-num>
	</programme>
	<programme start="20091104093500 +0000" stop="20091104110500 +0000" channel="32">
		<title lang="en">Soccer: UEFA Champions League</title>
		<sub-title lang="en">TBA</sub-title>
		<category lang="en">Football</category>
		<category lang="en">Soccer</category>
		<category lang="en">Sport</category>
		<episode-num system="icetv">14328-72386</episode-num>
		<previously-shown start="20090917"/>
	</programme>

</tv>
'''}

    programme = \
        {'title': 'Spiderman',
         'subtitle': 'The One Where Spiderman Eats Salad',
         'desc': 'Action is his reward.',
         'categories': ['News', 'Sport'],
         'channel': '2300',
         'start': datetime.datetime(2009, 10, 30, 11, 0),
         'stop': datetime.datetime(2009, 10, 30, 11, 30)}

    def open_fake(self, filename):
        from StringIO import StringIO
        return StringIO(self.fake_files[filename])

    def setUp(self):
        self.parser = icetotgd.IceToTgd()
        self.parser.use_xml_file(self.open_fake('trivial.xml'))

    def test_can_load_channels(self):
        self.assertEqual(self.parser.channels,
                          {'2300': {'lcn': '23',
                                    'display-name': 'TwentyThree'}})

    def test_can_load_one_programme(self):
        p = self.parser.programmes[0]
        self.assertEqual(p['title'], 'Spiderman')
        self.assertEqual(p['subtitle'], 'The One Where Spiderman Eats Salad')
        self.assertEqual(p['desc'], 'Action is his reward.')
        self.assertEqual(p['categories'], ['News', 'Sport'])
        self.assertEqual(p['channel'], '2300')
        self.assertEqual(p['rating'], None)
        self.assertEqual(p['start'], datetime.datetime(2009, 10, 30, 11, 0))
        self.assertEqual(p['stop'], datetime.datetime(2009, 10, 30, 11, 30))

    def test_time_to_tgd(self):
        start = datetime.datetime(2009, 10, 30, 11, 30)
        tgd_start = icetotgd.tgd_time_from_timestamp(start)
        self.assertEqual(tgd_start, '2009/10/30 22:30')

    def test_duration_to_tgd(self):
        start = datetime.datetime(2009, 10, 30, 11, 00)
        stop = datetime.datetime(2009, 10, 30, 11, 30)
        duration = stop - start
        tgd_duration = icetotgd.tgd_duration_from_timedelta(duration)
        self.assertEqual(tgd_duration, '30')

    def test_programme_to_tgd(self):
        tgd_line = self.parser.programme_to_tgd(self.programme)
        self.assertEqual(tgd_line,
                          '23\t2009/10/30 22:00\t30\tSpiderman\tThe One Where Spiderman Eats Salad [News/Sport]\tAction is his reward.\tX\tN')

    def test_can_parse_programme_xml_without_desc(self):
        p = self.parser.programmes[1]
        self.assertEqual(p['desc'], None)

    def test_can_convert_programme_xml_without_desc(self):
        p = self.programme.copy()
        p['desc'] = None
        tgd_line = self.parser.programme_to_tgd(p)
        self.assertEqual(tgd_line,
                          '23\t2009/10/30 22:00\t30\tSpiderman\tThe One Where Spiderman Eats Salad [News/Sport]\t\tX\tN')

    def test_str_or_empty(self):
        from icetotgd import str_or_empty
        self.assertEqual('', str_or_empty(None))
        self.assertEqual('', str_or_empty(''))
        self.assertEqual('foo', str_or_empty('foo'))

    def test_filename_from_programme(self):
        filename = icetotgd.tgd_filename_from_programme(self.programme)
        self.assertEqual(filename, '20091030.tgd')

if __name__=='__main__':
    unittest.main()
