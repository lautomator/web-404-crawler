# Web 404 Crawler

## About
This is a simple web crawler that will find and log 404 status urls in a single web page or a collection of web pages.

The script is configured to specifically look for 404s on any website given and xml site map. The structure of the xml and other parameters are defined in settings below the module imports.

Your xml site map structure might look soemthing like this:
```
<urlset>
    <url>
        <loc>{%url%}</loc>
        ...
    </url>
</urlset>
...

```

The script will write any 404 responses, errors, or activity to the a log. The log is cleared each time the script is called.

## Requirements
* Python 3

* [urllib3](https://urllib3.readthedocs.io/en/latest/)

* [untangle xml parser module](https://untangle.readthedocs.io/en/latest/)

## Setup and How to use
Download, fork, or clone this repository. Enter the url of the sitemap, the host domain, and the report options in the settings area towards the top of the script. You can run this script from a server or locally. Go to the root directory: `cd` into the `web-404-crawler`. Run the script: `python3 check-urls.py.
