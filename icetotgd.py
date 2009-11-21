#!/usr/bin/env python
from xml.etree import ElementTree as ET
import datetime

class IceToTgd(object):

    def use_xml_file(self, filename):
        self.tree = ET.parse(filename)
        self.load_channels()
        self.load_programmes()

    def load_channels(self):
        self.channels = dict(
            [(ch.get('id'),
              {'lcn': ch.findtext('lcn'),
               'display-name': ch.findtext('display-name')})
             for ch in self.tree.findall('channel')])

    def load_programmes(self):
        def listp(x):
            return type(x) is type([])

        def extract_list_without_none(xml, path):
            return [x for x in
                    [y.text for y in xml.findall(path)]
                    if x is not None]

        self.programmes = \
            [filter_dict
             ({'title': p.findtext('title'),
               'sub-title': p.findtext('sub-title'),
               'desc': p.findtext('desc'),
               'categories': extract_list_without_none(p, 'category'),
               'channel': p.get('channel'),
               'rating': p.findtext('rating/value'),
               'date': p.findtext('date'),
               'subtitles': p.findtext('subtitles'),
               'directors': extract_list_without_none(p, 'credits/director'),
               'actors': extract_list_without_none(p, 'credits/actor'),
               'previously-shown': None if p.find('previously-shown') is None \
                   else p.find('previously-shown').get('start', ''),
               'start': timestamp_from_xmltv_time(p.get('start')),
               'stop': timestamp_from_xmltv_time(p.get('stop'))},
              lambda k,v: v is not None and (not listp(v) or v))
             for p in self.tree.findall('programme')]

    def tgd_channel(self, programme):
        return self.channels[programme['channel']]['lcn']

    def tgd_title(self, programme):
        title = programme['title']
        if 'date' in programme:
            title += ' (%s)' % programme['date']
        return title

    def tgd_short_description(self, programme):
        sub_title = programme.get('sub-title', '')
        categories = ''
        if 'categories' in programme:
            categories += '[' + \
                '/'.join(programme['categories']) + ']'
        return ' '.join([sub_title, categories])

    def tgd_description(self, programme):
        desc = programme.get('desc', '')
        if 'subtitles' in programme:
            desc += ' [Subtitles]'
        if 'previously-shown' in programme:
            datestr = programme['previously-shown']
            if datestr == '':
                desc += ' [Repeat]'
            else:
                date = datetime.date(int(datestr[0:4]), int(datestr[4:6]), int(datestr[6:8]))
                out = date.strftime('%x')
                desc += ' [Repeat, last shown ' + out + ']'
        cast = self.tgd_cast_text(programme)
        if cast is not None:
            desc += ' ' + cast + '.'
        directors = self.tgd_director_text(programme)
        if directors is not None:
            desc += ' Dir. ' + directors + '.'
        return desc

    def tgd_rating(self, programme):
        return programme.get('rating', 'X')

    def tgd_director_text(self, programme):
        if 'directors' in programme:
            return ', '.join(programme['directors'])
        else:
            return None

    def tgd_cast_text(self, programme):
        if 'actors' in programme:
            return ', '.join(programme['actors'])
        else:
            return None

    def programme_to_tgd(self, programme):
        tgd_channel = self.tgd_channel(programme)
        tgd_start = tgd_time_from_timestamp(programme['start'])
        duration = programme['stop'] - programme['start']
        tgd_duration = tgd_duration_from_timedelta(duration)
        tgd_rating = 'X'

        line = '\t'.join([str_or_empty(x)
                          for x in [tgd_channel,
                                    tgd_start,
                                    tgd_duration,
                                    self.tgd_title(programme),
                                    self.tgd_short_description(programme),
                                    self.tgd_description(programme),
                                    self.tgd_rating(programme),
                                    'N']])
        return line

def timestamp_from_xmltv_time(timestr):
    return datetime.datetime.strptime(timestr, '%Y%m%d%H%M%S +0000')

def tgd_time_from_timestamp(timestamp):
    t = timestamp_as_localtime(timestamp)
    return t.strftime('%Y/%m/%d %H:%M')

def timestamp_as_localtime(timestamp):
    # [FUCKO]
    return timestamp + datetime.timedelta(0, 36000 + 3600, 0)

def tgd_duration_from_timedelta(duration):
    return str(duration.seconds / 60)

def str_or_empty(s):
    return s if s is not None else ''

def filter_dict(d, predicate):
    return dict([(k,v) for (k,v) in d.iteritems() if predicate(k,v)])

def tgd_filename_from_programme(programme):
    t = timestamp_as_localtime(programme['start'])
    return t.strftime('%Y%m%d.tgd')

sd_channels = ('2','22','3','7','9','10','23','32','72','99','12')

if __name__=='__main__':
    filename = 'iceguide.xml'
    parser = IceToTgd()
    parser.use_xml_file(filename)
    current_tgd_filename = None
    current_tgd_file = None
    for p in parser.programmes:
        if parser.tgd_channel(p) in sd_channels:
            new_tgd_filename = tgd_filename_from_programme(p)
            if new_tgd_filename != current_tgd_filename:
                current_tgd_file = open('out/' + new_tgd_filename, 'a')
            try:
                line = parser.programme_to_tgd(p).encode('UTF-8')
            except Exception, e:
                print 'data: "%s"' % p
                raise e
            current_tgd_file.write(line + '\r\n')
