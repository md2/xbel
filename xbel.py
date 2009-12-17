#!/usr/bin/python

import sys
import time
from xml.dom.minidom import getDOMImplementation


class XBEL(object):

    def __init__(self, version='1.0'):
        impl = getDOMImplementation()
        doctype = impl.createDocumentType('xbel',
                                          '+//IDN python.org//DTD XML Bookmark Exchange Language %s//EN//XML' %
                                          (version),
                                          'http://pyxml.sourceforge.net/topics/dtds/xbel-%s.dtd' %
                                          (version))
        self.doc = impl.createDocument(None, 'xbel', doctype)
        self.root = self.doc.documentElement
        self.root.setAttribute('version', version)

        self.elements = []

    def addStartElement(self, name):
        e = self.doc.createElement(name)
        if self.elements:
            self.elements[-1].appendChild(e)
        else:
            self.root.appendChild(e)
        self.elements.append(e)
        return e

    def addEndElement(self):
        self.elements.pop()

    def addTextElement(self, name, text):
        e = self.addStartElement(name)
        node = self.doc.createTextNode(text)
        e.appendChild(node)
        self.addEndElement()
        return e

    def addAttribute(self, name, value):
        e = self.elements[-1]
        e.setAttribute(name, value)

    def addEmptyElement(self, name):
        self.addStartElement(name)
        self.addEndElement()

    def writexml(self, outfile, **kw):
        self.doc.writexml(outfile, **kw)

    def formatDateTime(self, secs):
        return '%04d%02d%02d' % time.localtime(secs)[:3]

    def loadOpera(self, infile):
        title = infile.readline().rstrip('\r\n')
        self.addTextElement('title', title)
        self.addStartElement('info')
        self.addStartElement('metadata')
        self.addAttribute('owner', 'Mozilla')
        self.addAttribute('SyncPlaces', 'true')
        self.addAttribute('BookmarksToolbarFolder', 'default')
        self.addEndElement()
        self.addEndElement()
        self.addStartElement('folder')
        self.addAttribute('id', 'default')
        self.addEndElement()

        def generator():
            for id in xrange(sys.maxint):
                yield 'id%d' % (id)
        id = generator()

        bookmark = False
        folder = 0

        for line in infile:
            line = line.rstrip('\r\n')
            if line.startswith('\t'):
                line = line.lstrip('\t')
                key, value = line.split('=', 1)
                if bookmark:
                    if key == 'NAME':
                        self.addTextElement('title', value)
                    elif key == 'URL':
                        self.addAttribute('href', value if value != '' else 'http://')
                    elif key == 'DESCRIPTION':
                        self.addTextElement('desc', value.replace('\x02', ' '))
                    elif key == 'CREATED':
                        secs = int(value)
                        self.addAttribute('added', self.formatDateTime(secs))
                    elif key == 'VISITED':
                        secs = int(value)
                        self.addAttribute('visited', self.formatDateTime(secs))
                elif folder:
                    if key == 'NAME':
                        self.addTextElement('title', value)
                    elif key == 'DESCRIPTION':
                        self.addTextElement('desc', value.replace('\x02', ' '))
                    elif key == 'CREATED':
                        secs = int(value)
                        self.addAttribute('added', self.formatDateTime(secs))
            else:
                if bookmark:
                    self.addEndElement()
                    bookmark = False
                if line == '#FOLDER':
                    self.addStartElement('folder')
                    self.addAttribute('id', id.next())
                    folder += 1
                elif line == '#URL':
                    self.addStartElement('bookmark')
                    self.addAttribute('id', id.next())
                    bookmark = True
                elif line == '-':
                    self.addEndElement()
                    folder -= 1


if __name__ == '__main__':

    xbel = XBEL()
    xbel.loadOpera(sys.stdin)
    xbel.writexml(sys.stdout, encoding='UTF-8')

# vim: ts=4 sw=4 et tw=79 sts=4 ai si
# EOF
