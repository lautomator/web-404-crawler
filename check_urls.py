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
# verbose mode prints to stdout
VERBOSE = True
# END USER SETTINGS ==============


stats = {
    'pages crawled': 0,
    'urls checked': 0,
    '404s found': 0,
    'errors': 0
}


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
        stats['urls checked'] += 1
        can_write = True
    elif r_info['err'] == '1' and r_settings['report_errors']:
        stats['errors'] += 1
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
        and returns a list of urls.
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
        an empty list. Will not
        include the head if BODY_ONLY
        is set to True.
    '''
    page_links = []

    # scrape the page and convert byte data to <str>
    http = urllib3.PoolManager()
    response = http.request('GET', html_page)
    page_data = response.data.decode("utf-8")
    href_pat = r'href=\".*?\"'
    link = ''

    results = re.findall(href_pat, page_data)

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

def check_for_dup_link(url_to_check, list_of_urls):
    '''
        Verifys the current url being
        checked dhas not already been
        checked by the crawler. Returns
        True if checked or False.
    '''
    is_dup = False

    if url_to_check in list_of_urls:
        is_dup = True

    return is_dup

def show_stats():
    '''
        Prints to stdout the number
        of links checked, the number
        of 404s found, and the number
        of errors found.
    '''
    pages_crawled = stats['pages crawled']
    urls_checked = stats['urls checked']
    e_404_amt = stats['404s found']
    error_amt = stats['errors']

    print('========\n REPORT\n========')
    print(pages_crawled, 'pages crawled')
    print(urls_checked, 'urls checked')
    print(e_404_amt, '404 errors found')
    print(error_amt, 'http errors found')
    print('...')

    if e_404_amt or error_amt > 0:
        print('See the report', LOG_FILENAME, 'for more info.')


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
    link_list = []

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
            # get any urls from the page
            page_links = get_urls(page_url_in)

            if VERBOSE:
                print(current_link_no, 'of', no_of_links, 'links')
                print('page url:', page_url_in)
                print(len(page_links), 'links found\n...')

            if page_links:
                # check each link on a page
                for link in page_links:
                    if not check_for_dup_link(link, link_list):
                        if VERBOSE:
                            print(' > checking: ' + link)

                        url_data['page'] = page_url_in
                        url_data['link'] = link
                        resp_info = get_response(url_data)

                    # generates the initial link list
                    if current_link_no == 1:
                        link_list.append(link)

                    # report
                    stats['urls checked'] += 1

                    if resp_info:
                        write_log(resp_info, REPORT_SETTINGS, LOG_FILENAME)

            current_link_no += 1

        stats['pages crawled'] = no_of_links
    else:
        print('! No urls found in this sitemap.')
        sys.exit()

    print('=> Done.')
    show_stats()


if __name__ == '__main__':
    main()
