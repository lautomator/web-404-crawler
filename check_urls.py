# -*- coding: utf-8 -*-

"""
This script is configured to specifically look for
404s on any website given and xml sitemap. The sitemap
url and other settings can be defined where indicated.

The script will write any 404 responses, errors, or
activity to the a log. The log is cleared
each time the script is called.
"""

import re
import os
import sys
import urllib3
import untangle

# ================== USER SETTINGS
# Enter sitemap url here. Ex:
# https://www.<mysite.com>/sitemap_index.xml
MAIN_SITEMAP = ''
# Enter site domain here
# without the trailing slash.
# Ex: https://www.<mysite.com>
HOST_DOMAIN = ''
# You can rename the log here
LOG_FILENAME = 'report-404.log'
# This script will always report 404s.
# You can also have it report other
# errors or always report for every link.
REPORT_SETTINGS = {
    'report_errors': False, # will report errors
    'report_activity': False # will report everything
}
# END USER SETTINGS ==============


def clear_log(fname):
    '''
        Clear the log on the initial run.
    '''
    try:
        if os.stat(fname).st_size > 0:
            # log exists and contains info
            os.truncate(fname, 0)
    except FileNotFoundError:
        # no logs were found: they will be created when needed
        print('! File not found:', fname)


def write_log(r_info, r_settings, f_name):
    '''
        Logs selected data to the 404 report
    '''
    if r_info['code'] == '404':
        can_write = True
    elif r_info['err'] == '1' and r_settings['report_errors']:
        can_write = True
    elif r_settings['report_activity']:
        can_write = True
    else:
        can_write = False

    if can_write:
        report_info = r_info['url'] + '\t' + r_info['pageurl'] + '\t' + \
            r_info['code'] + '\t' + r_info['err'] + '\t' + r_info['emsg'] + '\n'
        fin = os.open(f_name, os.O_CREAT|os.O_WRONLY|os.O_APPEND)
        os.write(fin, str.encode(report_info))
        os.close(fin)


def parse_xml_links(url):
    '''
        Takes in xml site map and
        and returns a list of urls
    '''
    urls = []

    try:
        obj = untangle.parse(url)
    except Exception as e:
        print('! [err] the link submitted to the xml parser is invalid.', e)
        sys.exit()

    page = obj.urlset.url
    for addr in page:
        urls.append(addr.children[0].cdata)

    return urls


def get_urls(html_page):
    '''
        Scans a page and extracts
        all of the urls from href
        attributes. Returns a list
        of urls from the page or
        an empty list.
    '''
    page_links = []

    # scrape the page and convert byte data to <str>
    http = urllib3.PoolManager()
    response = http.request('GET', html_page)
    page_data = response.data.decode("utf-8")

    # find all href attributes and save to results
    href_pat = r'href=\".*?\"'
    results = re.findall(href_pat, page_data)
    link = ''

    # remove the href tag and quotes and
    # add protocol and host info for
    # links that begin with '/'
    for att in results:
        link = att.replace('href="', '').strip('"')
        temp = ''

        if link[0] == '/':
            temp = link
            link = HOST_DOMAIN + temp
        elif len(link) == 1 and link[0] == '#':
            link = HOST_DOMAIN + '/'
        else:
            pass

        page_links.append(link)

    return page_links


def get_response(url_data):
    '''
        Gets the http status from the
        url_data <dict>. Returns the response
        data <dict>.
    '''
    http = urllib3.PoolManager()
    response_data = {
        'pageurl': url_data['page'],
        'url': url_data['link'],
        'code': '',
        'err': '0',
        'emsg': ''
    }

    try:
        response = http.request('GET', url_data['link'])
        stat = response.status
        response_data['code'] = str(stat)
    except Exception as e:
        response_data['err'] = '1'
        response_data['emsg'] = str(e)

    return response_data


def main():
    '''
        Calls the functions to parse
        the site map and get responses
        from the returnsed urls. 404s
        and errors are logged to reports.
    '''

    url_data = {
        'page': '',
        'link': ''
    }

    no_of_links = 0
    current_link_no = 1

    print('=> Cleared existing log.')
    clear_log(LOG_FILENAME)

    print('=> Parsing xml ...')
    print('=> Getting page links ...')

    # parse the xml sitemap and store the links
    url_set = parse_xml_links(MAIN_SITEMAP)

    print('=> Parsing xml complete')
    print('=> Looking for 404s (this may take a while) ...')

    if url_set:
        no_of_links = len(url_set)
        # check each url extracted from the sitemap
        for page_url_in in url_set:
            print(current_link_no, 'of', no_of_links, 'links')
            print('checking:', page_url_in)

            # get any urls from the page
            page_links = get_urls(page_url_in)
            print(len(page_links), 'links found\n...')

            if page_links:
                # check each link on a page
                for link in page_links:
                    url_data['page'] = page_url_in
                    url_data['link'] = link
                    resp_info = get_response(url_data)

                    if resp_info:
                        write_log(resp_info, REPORT_SETTINGS, LOG_FILENAME)

            current_link_no += 1
    else:
        print('! No urls found in this sitemap.')
        sys.exit()

    print('=> Done. See the reports for more info.')


if __name__ == '__main__':
    main()
