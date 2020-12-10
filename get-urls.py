#!/usr/bin/python3

import urllib3
import re
import os
import sys
import untangle

# set the main sitemap url here
main_sitemap = 'ref/sitemap-home.xml' # 1


def parse_xml_links(url, struct):
    '''
        Takes in xml site map and
        xml structure and
        returns a list of urls
    '''
    urls = []
    obj = untangle.parse(url)

    if (struct == 1):
        page = obj.sitemapindex.sitemap
    else:
        page = obj.urlset.url

    for addr in page:
        urls.append(addr.children[0].cdata)

    return urls

def log_err(data):
    '''
        Writes the data <dict> to
        the errorlog
    '''
    report_info = str.encode(data['url'] + ',' + data['pageurl'] + ',' +
        data['emsg'] + '\n')
    fin = os.open('report_error.log', os.O_CREAT|os.O_WRONLY|os.O_APPEND)
    os.write(fin, report_info)
    os.close(fin)


def log_404(data):
    '''
        Writes the data <dict> to
        the 404 log
    '''
    report_info = str.encode(data['url'] + ',' + data['pageurl'] + ',' +
        str(data['code']) + '\n')
    fin = os.open('report_404.log', os.O_CREAT|os.O_WRONLY|os.O_APPEND)
    os.write(fin, report_info)
    os.close(fin)


# def get_urls(html_page):
#     '''
#         Scans a page and extracts
#         all of the urls from href
#         attributes. Returns a list
#         of urls from the page or nothing.
#     '''
#     # check for a bad status
#     page_data = get_response(html_page)




#     if stat != 404:
#         href_pat = r'href=\".*?\"'
#         results = re.findall(href_pat, html_page)
#     else:
#         # report a 404 or error
#         if stat == 404:
#             pass
#         else:
#             pass


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

    return response_data;


def check_response(resp_info):
    if resp_info['code'] == 404:
        response_type = '404'
    elif resp_info['err'] == 1:
        response_type = 'err'
    else:
        response_type = 'ok'

    return response_type


def main():
    # parse the main xml sitemap and store the links
    site_links = parse_xml_links(main_sitemap, 1)
    url_set = parse_xml_links(site_links[0], 2)

    page_url_in = url_set[0]

    print(page_url_in)

# TODO get urls from page
# parse the page and check each url
# write to the report or error report or pass (good url)
#####

    # url_in = 'https://www.thefire.org/resources/spotlight/reports/spotlight-on-speech-codes-2021/'

    # # scan each one at a time and write to report

    # # move onto the next page


    # url_data = {
    #     'page': page_url_in,
    #     'link': url_in
    # }

    # resp_info = get_response(url_data)
    # response_type = check_response(resp_info)
    # print(resp_info)


    # if response_type == '404':
    #     log_404(resp_info)
    # elif response_type == 'err':
    #     log_err(resp_info)
    # else:
    #     pass



if __name__ == '__main__':
    main()




# new_url = url_in.replace('href="', '').strip('"')




'''
FIRE site map home: https://www.thefire.org/sitemap_index.xml

website crawler to get 404s

run something like python url-crawler <arg>
<arg> is the site map page like: https://www.thefire.org/post-sitemap1.xml

use this regex to get a link from a page: href=".*?"

- create flatfile to store report

- parse the xml site map to get each page url
    - get an http response for each url found on the page (one at a time) -- use urllib3
        - parse the page from the url on the site map
        - find a url on the page and get a response
            - if the response == 404
                log the url visited (page from the site map)
                    - write to the flatfile
                log the url fetched from the response
                    - write to the flatfile
                log the response code
                    - write to the flatfile
            - else move onto the next url
        - if no urls found, move to the next page
    - if no more page urls exit the script

- log errors to an error log flatfile as well

the report flatfile should look like:
<url fetched>, <current page>, <response code (404)>
'''