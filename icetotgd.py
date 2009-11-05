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
        self.programmes = \
            [{'title': p.findtext('title'),
              'subtitle': p.findtext('sub-title'),
              'desc': p.findtext('desc'),
              'categories': [x.text for x in p.findall('category')],
              'channel': p.get('channel'),
              'rating': None,
              'start': timestamp_from_xmltv_time(p.get('start')),
              'stop': timestamp_from_xmltv_time(p.get('stop'))}
             for p in self.tree.findall('programme')]

    def tgd_channel(self, programme):
        return self.channels[programme['channel']]['lcn']

    def programme_to_tgd(self, programme):
        tgd_channel = self.tgd_channel(programme)
        tgd_start = tgd_time_from_timestamp(programme['start'])
        duration = programme['stop'] - programme['start']
        tgd_duration = tgd_duration_from_timedelta(duration)
        tgd_rating = 'X'
        short_desc = ''
        if programme['subtitle'] is not None:
            short_desc = programme['subtitle'] + ' '
        if programme['categories'] is not None \
                and len(programme['categories']) > 0 \
                and programme['categories'][0] is not None:
            short_desc += '[' + \
                '/'.join(programme['categories']) + ']'
        line = '\t'.join([str_or_empty(x)
                          for x in [tgd_channel,
                                    tgd_start,
                                    tgd_duration,
                                    programme['title'],
                                    short_desc,
                                    programme['desc'],
                                    'X',
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
    if s is not None:
        return s
    return ''

def tgd_filename_from_programme(programme):
    t = timestamp_as_localtime(programme['start'])
    return t.strftime('%Y%m%d.tgd')

if __name__=='__main__':
    filename = 'iceguide.xml'
    parser = IceToTgd()
    parser.use_xml_file(filename)
    current_tgd_filename = None
    current_tgd_file = None
    for p in parser.programmes:
        if parser.tgd_channel(p) in ('2','22','3','7','9','10','23','32','72','99','12'):
            new_tgd_filename = tgd_filename_from_programme(p)
            if new_tgd_filename != current_tgd_filename:
                current_tgd_file = open(new_tgd_filename, 'a')
            line = parser.programme_to_tgd(p).encode('UTF-8')
            current_tgd_file.write(line + '\n')
