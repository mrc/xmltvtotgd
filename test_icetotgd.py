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
	<programme start="20091105093500 +0000" stop="20091105110500 +0000" channel="32">
		<title lang="en">Suburb of the Moths</title>
                <desc lang="en">A suburb is terrorised by shrimp moths from hell.</desc>
                <credits>
                        <director>Dave Keenan</director>
                        <actor>Marvin O'Gravel Ballon-Face</actor>
                        <actor>Oliver Boliver Butt</actor>
                        <actor>Zanzibar Buck-Buck McBean</actor>
                </credits>
                <date>1996</date>
		<category lang="en">Movie</category>
		<subtitles type="teletext"/>
                <rating system="">
                        <value>M</value>
                </rating>
		<previously-shown/>
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

    def test_programme_xml_without_desc(self):
        p = self.parser.programmes[1]
        self.assertEqual(p['desc'], None)

    def test_programme_xml_with_year(self):
        p = self.parser.programmes[2]
        self.assertEqual(p['date'], '1996')

    def test_tgd_title_includes_year(self):
        p = self.parser.programmes[2]
        title = self.parser.tgd_title(p)
        self.assertEqual(title, 'Suburb of the Moths (1996)')

    def test_unrated_programmes_are_rated_x(self):
        p = self.parser.programmes[0]
        rating = self.parser.tgd_rating(p)
        self.assertEqual(rating, 'X')

    def test_can_get_programme_rating(self):
        p = self.parser.programmes[2]
        rating = self.parser.tgd_rating(p)
        self.assertEqual(rating, 'M')

    def test_description_says_subtitles_if_they_exist(self):
        p = self.parser.programmes[2]
        description = self.parser.tgd_description(p)
        self.assertTrue(description.index('[Subtitles]'))

    def test_description_doesnt_say_repeat_if_its_not_a_repeat(self):
        p = self.parser.programmes[0]
        description = self.parser.tgd_description(p)
        self.assertTrue(description.find('[Repeat]') == -1)

    def test_description_says_repeat_if_its_a_repeat(self):
        p = self.parser.programmes[2]
        description = self.parser.tgd_description(p)
        self.assertTrue(description.find('[Repeat]') != -1)

    def test_description_says_repeat_with_date_if_its_a_repeat_with_a_known_date(self):
        p = self.parser.programmes[1]
        description = self.parser.tgd_description(p)
        date = datetime.date(2009, 9, 17).strftime('%x')
        self.assertTrue(description.find('[Repeat, last shown ' + date + ']') != -1)

    def test_tgd_short_description_includes_category(self):
        p = self.parser.programmes[0]
        short_desc = self.parser.tgd_short_description(p)
        self.assertEqual(short_desc, 'The One Where Spiderman Eats Salad [News/Sport]')

    def test_programme_xml_without_desc(self):
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
