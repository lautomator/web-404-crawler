# -*- coding: utf-8 -*-

"""
TBA
"""

import re
import os
import urllib3
import untangle

# set the main sitemap url here
MAIN_SITEMAP = 'ref/sitemap-home.xml'
HOST_DOMAIN = 'https://thefire.org'
all_logs = ['activity.log', 'report-404.log', 'report-error.log']

def clear_logs(logs):
    '''
        Clear all of the logs
        on the initial run.
    '''
    for log in logs:
        try:
            if os.stat(log).st_size > 0:
                # log exists and contains info
                os.truncate(log, 0)
            else:
                pass
        except FileNotFoundError:
            # no logs were found: they will be created when needed
            print('=> File not found:', log)


def parse_xml_links(url, struct):
    '''
        Takes in xml site map and
        xml structure and
        returns a list of urls
    '''
    urls = []
    obj = untangle.parse(url)

    if struct == 1:
        # 1
        page = obj.sitemapindex.sitemap
    else:
        # 2
        page = obj.urlset.url

    for addr in page:
        urls.append(addr.children[0].cdata)

    return urls

def log_err(data):
    '''
        Writes the data <dict> to
        the errorlog
    '''
    if data:
        report_info = str.encode(data['url'] + ',' + data['pageurl'] + ',' +
            data['emsg'] + '\n')
        fin = os.open('report-error.log', os.O_CREAT|os.O_WRONLY|os.O_APPEND)
        os.write(fin, report_info)
        os.close(fin)
    else:
        pass


def log_404(data):
    '''
        Writes the data <dict> to
        the 404 log
    '''
    if data:
        report_info = str.encode(data['url'] + ',' + data['pageurl'] + ',' +
            str(data['code']) + '\n')
        fin = os.open('report-404.log', os.O_CREAT|os.O_WRONLY|os.O_APPEND)
        os.write(fin, report_info)
        os.close(fin)
    else:
        pass


def log_activity(data):
    '''
        Records all activity
    '''
    if data:
        report_info = str.encode(data['url'] + ',' + data['pageurl'] + ',' +
            str(data['code']) + ',' + data['emsg'] + '\n')
        fin = os.open('activity.log', os.O_CREAT|os.O_WRONLY|os.O_APPEND)
        os.write(fin, report_info)
        os.close(fin)
    else:
        pass


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
        'code': None,
        'err': 0,
        'emsg': ''
    }

    try:
        response = http.request('GET', url_data['link'])
        stat = response.status
        response_data['code'] = stat
    except Exception as LocationValueError:
        response_data['err'] = 1
        response_data['emsg'] = LocationValueError.args[0]

    return response_data


def check_response(resp_info):
    '''
        Returns the response type
        as a string. Only interested
        in 404s or errors mostly.
    '''
    if resp_info['code'] == 404:
        response_type = '404'
    elif resp_info['err'] == 1:
        response_type = 'err'
    else:
        response_type = 'ok'

    return response_type


def main():
    '''
        See the settings at the top
        of the script.
    '''

    print('=> clearing logs ...')
    clear_logs(all_logs)

    print('=> parsing xml ...')

    # parse the main xml sitemap and store the links
    site_links = parse_xml_links(MAIN_SITEMAP, 1)
    url_set = parse_xml_links(site_links[0], 2)

    page_url_in = url_set[1]

    print('=> [parsing xml complete]')
    print('=> getting page links ...')

    page_links = get_urls(page_url_in)

    # this will be a loop and turn into
    # a function later
    url_data = {
        'page': page_url_in,
        'link': ''
    }

    if page_links:

        print('=> looking for 404s ...')

        for link in page_links:
            url_data['link'] = link
            resp_info = get_response(url_data)
            response_type = check_response(resp_info)

            if response_type == '404':
                log_404(resp_info)
            elif response_type == 'err':
                log_err(resp_info)
            else:
                pass
    else:
        print('=> no page links found')

    print('=> done. See the reports for more info.')


if __name__ == '__main__':
    main()
