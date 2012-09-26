# Amara, universalsubtitles.org
#
# Copyright (C) 2012 Participatory Culture Foundation
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see
# http://www.gnu.org/licenses/agpl-3.0.html.
"""Functionality for generating srt files."""

import xml.dom.minidom
import StringIO
from HTMLParser import HTMLParser
from libs.unilangs import unilangs

def captions_and_translations_to_srt(captions_and_translations):
    # TODO: note this loads the entire string into memory, which will not
    # scale beautifully. In future, possibly stream directly to response.
    output = StringIO.StringIO()
    for i in range(len(captions_and_translations)):
        translation_to_srt(captions_and_translations[i][1],
                           captions_and_translations[i][0],
                           i, output)
    srt = output.getvalue()
    output.close()
    return srt

def captions_to_srt(subtitles):
    # TODO: note this loads the entire string into memory, which will not
    # scale beautifully. In future, possibly stream directly to response.
    output = StringIO.StringIO()
    for i in range(len(subtitles)):
        subtitle_to_srt(subtitles[i], i, output)
    srt = output.getvalue()
    output.close()
    return srt

def translation_to_srt(translation, video_caption, index, output):
    subtitle_to_srt_impl(video_caption.caption_text if translation is None \
                         else translation.translation_text,
                         video_caption, index, output)

def subtitle_to_srt(video_caption, index, output):
    subtitle_to_srt_impl(video_caption.caption_text,
                         video_caption, index, output)

def subtitle_to_srt_impl(text, video_caption, index, output):
    output.write(str(index + 1))
    output.write("\n")
    write_srt_time_line(video_caption, output)
    output.write(text)
    output.write("\n\n")

def write_srt_time_line(video_caption, output):
    write_srt_time(video_caption.start_time, output)
    output.write(" --> ")
    write_srt_time(video_caption.end_time, output)
    output.write("\n")

def write_srt_time(seconds, output):
    seconds_int = int(seconds)
    write_padded_num((seconds_int / 3600) % 60, 2, output)
    output.write(":")
    write_padded_num((seconds_int / 60) % 60, 2, output)
    output.write(":")
    write_padded_num(seconds_int % 60, 2, output)
    output.write(",")
    write_padded_num(int(seconds * 1000) % 1000, 3, output)

def write_padded_num(num, numchars, output):
    strnum = str(num)
    numzeros = numchars - len(strnum)
    for i in range(numzeros):
        output.write("0")
    output.write(strnum)

from math import floor
import codecs

class BaseSubtitles(object):
    file_type = ''

    def __init__(self, subtitles, video=None, line_delimiter=u'\n', sl=None):
        """
        Use video for extra data in subtitles like Title
        Subtitles is list of {'text': 'text', 'start': 'seconds', 'end': 'seconds', 'id': id}
        """
        self.subtitles = subtitles
        self.video = video
        self.line_delimiter = line_delimiter
        self.sl = sl
        if video:
            self.title = sl and sl.get_title_display() or video.title
        else:
            self.title = u""

    def __unicode__(self):
        raise Exception('Should return subtitles')

    @classmethod
    def isnumber(cls, val):
        return isinstance(val, (int, long, float))

    @classmethod
    def create(cls, sv, video=None, sl=None):
        sl = sl or sv.language
        video = video or sl.video

        subtitles = []

        for item in sv.subtitles():
            subtitles.append(item.for_generator())

        return cls(subtitles, video, sl=sl)

class GenerateSubtitlesHandlerClass(dict):

    def register(self, handler, type=None):
        self[type or handler.file_type] = handler

GenerateSubtitlesHandler = GenerateSubtitlesHandlerClass()

class MGSubtitles(BaseSubtitles):

    def __unicode__(self):
        output = []

        for item in self.subtitles:
            output.append(u'[[[%s]]]' % item['id'])
            output.append(item['text'].replace(u'[[[', u'').replace(u']]]', u''))

        return u''.join(output)

GenerateSubtitlesHandler.register(MGSubtitles)

class SRTSubtitles(BaseSubtitles):
    file_type = 'srt'

    def __init__(self, subtitles, video, line_delimiter=u'\r\n', sl=None):
        super(SRTSubtitles, self).__init__(subtitles, video, line_delimiter)

    def __unicode__(self):
        output = []

        parser = HTMLParser()
        i = 1
        for item in self.subtitles:
            if self.isnumber(item['start']) and self.isnumber(item['end']):
                output.append(unicode(i))
                start = self.format_time(item['start'])
                end = self.format_time(item['end'])
                output.append(u'%s --> %s' % (start, end))
                output.append(parser.unescape(item['text']).strip())
                output.append(u'')
                i += 1

        return self.line_delimiter.join(output)

    def format_time(self, time):
        hours = int(floor(time / 3600))
        if hours < 0:
            hours = 99
        minutes = int(floor(time % 3600 / 60))
        seconds = int(time % 60)
        fr_seconds = int(time % 1 * 100)
        return u'%02i:%02i:%02i,%03i' % (hours, minutes, seconds, fr_seconds)

GenerateSubtitlesHandler.register(SRTSubtitles)

class SBVSubtitles(BaseSubtitles):
    file_type = 'sbv'

    def __init__(self, subtitles, video, line_delimiter=u'\r\n', sl=None):
        super(SBVSubtitles, self).__init__(subtitles, video, line_delimiter)

    def __unicode__(self):
        output = []

        for item in self.subtitles:
            if self.isnumber(item['start']) and self.isnumber(item['end']):
                start = self.format_time(item['start'])
                end = self.format_time(item['end'])
                output.append(u'%s,%s' % (start, end))
                output.append(item['text'].strip())
                output.append(u'')

        return self.line_delimiter.join(output)

    def format_time(self, time):
        hours = int(floor(time / 3600))
        if hours < 0:
            hours = 9
        minutes = int(floor(time % 3600 / 60))
        seconds = int(time % 60)
        fr_seconds = int(time % 1 * 1000)
        return u'%01i:%02i:%02i.%03i' % (hours, minutes, seconds, fr_seconds)

GenerateSubtitlesHandler.register(SBVSubtitles)

class TXTSubtitles(BaseSubtitles):
    file_type = 'txt'

    def __init__(self, subtitles, video, line_delimiter=u'\r\n\r\n', sl=None):
        super(TXTSubtitles, self).__init__(subtitles, video, line_delimiter)

    def __unicode__(self):
        output = []
        for item in self.subtitles:
            item['text'] and output.append(item['text'].strip())

        return self.line_delimiter.join(output)

GenerateSubtitlesHandler.register(TXTSubtitles)

class SSASubtitles(BaseSubtitles):
    file_type = 'ssa'

    def __unicode__(self):
        #add BOM to fix python default behaviour, because players don't play without it
        return u''.join([unicode(codecs.BOM_UTF8, "utf8"), self._start(), self._content(), self._end()])

    def _start(self):
        ld = self.line_delimiter
        return u'[Script Info]%sTitle: %s%s' % (ld, self.title, ld)

    def _end(self):
        return u''

    def format_time(self, time):
        hours = int(floor(time / 3600))
        if hours < 0:
            hours = 9
        minutes = int(floor(time % 3600 / 60))
        seconds = int(time % 60)
        fr_seconds = int(time % 1 * 100)
        return u'%i:%02i:%02i.%02i' % (hours, minutes, seconds, fr_seconds)

    def _clean_text(self, text):
        return text.replace('\n', ' ')

    def _content(self):
        dl = self.line_delimiter
        output = []
        output.append(u'[Events]%s' % dl)
        output.append(u'Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text%s' % dl)
        tpl = u'Dialogue: 0,%s,%s,Default,,0000,0000,0000,,%s%s'
        for item in self.subtitles:
            if self.isnumber(item['start']) and self.isnumber(item['end']):
                start = self.format_time(item['start'])
                end = self.format_time(item['end'])
                text = self._clean_text(item['text'].strip())
                output.append(tpl % (start, end, text, dl))
        return ''.join(output)

GenerateSubtitlesHandler.register(SSASubtitles)

from lxml import etree
import lxml.html
import re

class TTMLSubtitles(BaseSubtitles):
    file_type = 'xml'
    remove_re = re.compile(u'[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F]')
    use_named_styles = True
    STYLES = {

        "strong": {
            'fontWeight':'bold'
        },
        'emphasis': {
            'textStyle': 'italic'
        },
        'underlined': {
            'textDecoration': 'underline'
        }
    }

    def __unicode__(self):
        node = self.xml_node()
        return node.toxml()

    def _get_attributes(self, item):
        attrib = {}
        attrib['begin'] = self.format_time(item['start'])
        attrib['dur'] = self.format_time(item['end']-item['start'])
        return attrib

    def xml_node(self):
        xmlt = """<tt xml:lang="%s" xmlns="http://www.w3.org/ns/ttml"
                      xmlns:ttp="http://www.w3.org/ns/ttml#parameter"
                      xmlns:tts="http://www.w3.org/ns/ttml#styling" >
        <head>
            <metadata/>
            <styling/>
            <layout/>
        </head>
        <body region="subtitleArea">
            <div>
            </div>
        </body>
        </tt>""" % unilangs.to_bcp47(self.sl.language)
        from xml.dom import expatbuilder
        dom = xml.dom.minidom.parseString(xmlt)
	styling = dom.getElementsByTagName('head')[0].getElementsByTagName('styling')[0]
        styling.setAttribute("xmlns:tts", "http://www.w3.org/2006/10/ttaf1#styling")

        for style_name, style_def in TTMLSubtitles.STYLES.items():
            style = dom.createElement('style')
            style.setAttribute('xml:id', style_name)
            for def_name, def_style in style_def.items():
                style.setAttribute(def_name, def_style)
            styling.appendChild(style)

	div = dom.getElementsByTagName('tt')[0].getElementsByTagName('body')[0].getElementsByTagName('div')[0]
        italic_declaration = 'tts:fontStyle="italic"' if TTMLSubtitles.use_named_styles else 'style="emphasis"'
        bold_declaration = 'tts:fontWeight="bold"' if TTMLSubtitles.use_named_styles else 'style="strong"'
        underline_declaration = 'tts:textDecoration="underline"' if TTMLSubtitles.use_named_styles else 'style="underlined"'
            
        for i,item in enumerate(self.subtitles):
            if item['text'] and self.isnumber(item['start']) and self.isnumber(item['end']):
                # as we're replacing new lines with <br>s we need to create
                # the element from a fragment,and also from the formateed <b> and <i> to
                # the correct span / style
                content = item['text'].replace(u'\n', u'<br/>').strip()
                content = content.replace(u"<b>", u'<span  %s>' % (bold_declaration)).replace(u"</b>", u'</span>')
                content = content.replace(u"<i>", u'<span  %s>' % (italic_declaration)).replace(u"</i>", u'</span>')
                content = content.replace(u"<u>", u'<span  %s>' % (underline_declaration)).replace(u"</u>", u'</span>')
                xml_str = (u'<p xml:id="sub-%s">%s</p>' % (i,content)).encode('utf-8')
        
                # we need to use this parser to make sure namespace chekcing is off
                # else the node can't be generated without the proper context
                node = expatbuilder.parseString(xml_str, namespaces=False)
                child = node.documentElement

                for k,v in self._get_attributes(item).items():
                    child.setAttribute(k,v)
                div.appendChild(child)

        return dom

    def format_time(self, time):
        hours = int(floor(time / 3600))
        if hours < 0:
            hours = 99
        minutes = int(floor(time % 3600 / 60))
        seconds = int(time % 60)
        fr_seconds = int(time % 1 * 100)
        return u'%02i:%02i:%02i.%02i' % (hours, minutes, seconds, fr_seconds)

GenerateSubtitlesHandler.register(TTMLSubtitles, 'ttml')

class DFXPSubtitles(TTMLSubtitles):
    file_type = 'dfxp'

    def _get_attributes(self, item):
        attrib = {}
        attrib['begin'] = self.format_time(item['start'])
        attrib['end'] = self.format_time(item['end'])
        return attrib

GenerateSubtitlesHandler.register(DFXPSubtitles, 'dfxp')
