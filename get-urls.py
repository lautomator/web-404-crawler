import urllib3
import re

# url_in = 'https://www.thefire.org/report-88-of-universities-restrict-expression-and-online-classes-are-especially-dangerous-for-student-speech/'
# http = urllib3.PoolManager()
# response = http.request('GET', url_in)

# response is in bytes
# converet to a string with decode
# data = response.data.decode("utf-8")
# stat = response.status

def get_urls(html_page):
    href_pat = r'href=\".*?\"'
    results = re.findall(href_pat, html_page)
    return results

def get_response(url_in):
    http = urllib3.PoolManager()
    try:
        response = http.request('GET', url_in)
        stat = response.status

        if stat == 404:
            # write to 404 flat file function
            print('%s,%s,%s' % (url_in, stat, '<page visited>'))
        else:
            pass
    except Exception as e:
        # send to error log (write to flat file function)
        print('%s,%s,%s' % (url_in, e, '<page visited>'))

get_response('https://www.thefire.org/get-involved/')

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
<url fetched>, <response code (404)>, <current page>
'''