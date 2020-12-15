# -*- coding: utf-8 -*-

"""
This script is configured to specifically look for
404s on any website given and xml site map. The structure
of the xml and other parameters are defined in settings
below the module imports.

The script will write any 404 responses to the
report-404.log. Any response errors are reported to
the report-error.log. The activity log is used for
development or can be configured to be used in
tandem with the other logs. All logs are created
when the script needs them. The logs are cleared
each time the script is called.
"""

import re
import os
import sys
import urllib3
import untangle

# ================== USER SETTINGS
MAIN_SITEMAP = 'ref/sitemap-url-set.xml' #TODO this will com from uinput
HOST_DOMAIN = 'https://thefire.org' #TODO this will com from parsing uinput
all_logs = ['activity.log', 'report-404.log', 'report-error.log']
# END USER SETTINGS ==============
# MAIN_SITEMAP = input('Enter the full address of the sitemap: ')


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
        'code': None,
        'err': 0,
        'emsg': ''
    }

    try:
        response = http.request('GET', url_data['link'])
        stat = response.status
        response_data['code'] = stat
    except Exception as e:
        response_data['err'] = 1
        response_data['emsg'] = str(e)

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
        Calls the functions to parse
        the site map and get responses
        from the returnsed urls. 404s
        and errors are logged to reports.
    '''

    url_data = {
        'page': '',
        'link': ''
    }

    print('=> Clearing logs ...')
    clear_logs(all_logs)

    print('=> Parsing xml ...')
    print('=> Getting page links ...')

    # parse the xml sitemap and store the links
    url_set = parse_xml_links(MAIN_SITEMAP)

    print('=> Parsing xml complete')
    print('=> Looking for 404s (this may take a while) ...')

    if url_set:
        # check each url extracted from the sitemap
        for page_url_in in url_set:
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
                    response_type = check_response(resp_info)

                    if response_type == '404':
                        log_404(resp_info)
                    elif response_type == 'err':
                        log_err(resp_info)
                    else:
                        pass
            else:
                print(page_url_in, '=> no links on the page.')
    else:
        print('! No urls found in this sitemap.')
        sys.exit()

    print('=> Done. See the reports for more info.')


if __name__ == '__main__':
    main()
