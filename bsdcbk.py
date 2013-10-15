#!/usr/bin/env python
# -*- mode: python -*-
#from lxml import etree
import xml.etree.ElementTree as etree
from urllib import unquote
import sys

def fix_name(name):
    name = unquote(name)
    name = name.replace('(', '')
    name = name.replace(')', '')
    name = name.replace('.', '')
    return name

def convert_pairs_to_html(pairs):
    html = '</li>'
    current_level = -1
    for section, anchor in pairs:
        level = section.count('.')

        if level > current_level:
            # Remove </li>
            html = html[:-5]
            html += '<ul class="nav">' * (level - current_level)
        elif level < current_level:
            # Add </li>
            html += '</ul></li>' * (current_level - level)
        else: # level == current_level
            pass
        current_level = level

        html += '<li data-section="%s">%s</li>' % (section, anchor)

    level = -1
    if level < current_level:
        html += '</ul></li>' * (current_level - level)
    else: # level == current_level
        pass

    # Remove </li>
    return html[:-5]

def template_with_columns(sidebar, main):
    '''
        <div class="container">
            <div class="row">
                <div class="col-sm-3 col-sidebar">
                    <div class="panel panel-default hidden-print hidden-xs sidebar">
                        %s
                    </div><!-- .sidebar -->
                </div><!-- .col-sidebar -->
                <div class="col-sm-9 col-main" role="main">
                    %s
                    <!-- .main -->
                </div><!-- .col-main -->
            </div><!-- .row -->
        </div><!-- .container -->
    '''
    template = template_with_columns.__doc__
    return template % (sidebar, main)

def fix_sidebar(div):
    if div[0].tag == 'p':
        del div[0]
        
    for dl in div.iter('dl'):
        dl.tag = 'ul'
        dl.attrib['class'] = 'nav'
        for i, dt in enumerate(dl):
            dt.tag = 'li'
            dt[0] = dt[0][0]

def main(filename):
    tree = etree.parse(filename)

    # Fix IDs
    #for a in tree.iter('a'):
    #    if a.get('name'):
    #        name = a.attrib['name']
    #        del a.attrib['name']
    #        name = fix_name(name)
    #        a.attrib['id'] = name
    #    if a.get('href'):
    #        nameref = a.attrib['href']
    #        if nameref.startswith('#'):
    #            name = nameref[1:]
    #            name = fix_name(name)
    #            a.attrib['href'] = '#%s' % name

    # Fix Title
    #for h2 in tree.iter('h2'):
    #    a2 = h2.find('a')
    #    name = a2.get('id')
    #    name = fix_name(name)
    #    for a in tree.iter('a'):
    #        if a.get('class') and a.attrib['class'] == 'tocviewselflink':
    #            a.attrib['href'] = '#%s' % name

    # Fix Headers
    for number in xrange(1, 6):
        for hd in tree.iter('h' + str(number)):
            #print(etree.tostring(hd))
            name = None
            for a2 in hd.iter('a'):
                name = a2.get('name')
            title = etree.tostring(hd)
            title = title.split('/>')[1]
            title = title.split('</')[0]
            for child in list(hd):
                hd.remove(child)
            if hd.get('style'):
                del hd.attrib['style']
            else:
                # Increase Font Size for doc title
                hd.tag = 'h1'
            hd.attrib['id'] = name
            hd.text = title

    # Build New TOC
    sidebar_div = None
    sidebar_html = ''
    sidebar_pairs = []
    for div in tree.iter('div'):
        if div.get('class') and div.attrib['class'] == 'toc':
            fix_sidebar(div)
            sidebar_div = div
            sidebar_html = etree.tostring(div)

    # Get Main
    main_div = None
    main_html = ''
    for div in tree.iter('div'):
        for i, div_child in enumerate(div):
            if div_child.get('class') and div_child.attrib['class'] == 'toc':
                del div[i]
                main_div = div
                main_html = etree.tostring(div)

    return template_with_columns(sidebar_html, main_html)


if __name__ == '__main__':
   import sys
   out = main(sys.argv[1])
   print(out)
