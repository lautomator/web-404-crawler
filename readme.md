# Web 404 Crawler

## About
This is a simple web crawler that will find and log 404 status url errors from a single web page or a collection of web pages.

The script is configured to specifically look for 404s on any website given and xml site map. Your xml site map structure looks soemthing like this:
```
...
<urlset>
    <url>
        <loc>{%url%}</loc>
        ...
    </url>
</urlset>
...

```

The script will write any 404 responses, errors, or activity to a log. The log is cleared each time the script is called.

You can configure user settings in the settings section just below the module imports. Here are the setting options and any default values:
```
MAIN_SITEMAP = '' # Enter the main sitemap for the crawler to parse
HOST_DOMAIN = '' # Enter the host domain
LOG_FILENAME = 'report-404.log' # You can rename this
REPORT_SETTINGS = {
    'report_errors': False, # Will report other connection errors
    'report_activity': False # Will report activity no matter what
}
VERBOSE = True # Will print to stdout
```

## Requirements
* Python 3

* [urllib3](https://urllib3.readthedocs.io/en/latest/): Handles the requests

* [untangle xml parser module](https://untangle.readthedocs.io/en/latest/): Parses XML

## Setup and How to use
Download, fork, or clone this repository. Enter the url of the sitemap, the host domain, and the report options in the settings area towards the top of the script. You can run this script from a server or locally. Go to the root directory: `cd` into the `web-404-crawler`. Run the script: `python3 check-urls.py`.
