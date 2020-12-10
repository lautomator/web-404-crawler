import urllib3
import re
import os
import sys

page_url_in = 'https://www.thefire.org/report-88-of-universities-restrict-expression-and-online-classes-are-especially-dangerous-for-student-speech/'
url_in = 'https://www.thefire.org/resources/spotlight/reports/spotlight-on-speech-codes-2021/'

# http = urllib3.PoolManager()
# response = http.request('GET', url_in)

# response is in bytes
# converet to a string with decode
# data = response.data.decode("utf-8")
# stat = response.status


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


def get_urls(html_page):
    href_pat = r'href=\".*?\"'
    results = re.findall(href_pat, html_page)
    print(results)


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


def main():
    url_data = {
        'page': page_url_in,
        'link': url_in
    }

    resp_info = get_response(url_data)
    print(resp_info)

    if resp_info['code'] == 404:
        log_404(resp_info)
    elif resp_info['err'] == 1:
        log_err(resp_info)
    else:
        pass



if __name__ == '__main__':
    main()



# get_urls(url_in)

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