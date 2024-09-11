'''
All Auxillary functions stored here to implement Snowflake UDFs
'''
import sys
import os

# Assuming the 'libs' folder is inside the zip, add it to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'libs'))

import re
from ftfy import fix_encoding
import hyperlink
import re
from typing import Union
from nameparser import HumanName
import datetime as dt

COMMON_URLS = [
    'facebook.com',
    'indiamart.com',
    'instagram.com',
    'linkedin.com',
    'yelp.com',
    'linktr.ee',
    'youtube.com',
    'bit.ly',
    'google.com',
    'twitter.com',
    'personalfinancesolution.info',
    'personalcreditsolutions.info',
    'behance.net',
    'etsy.com',
    'insuranceandfinancetips.info',
    'anchor.fm',
    'meetup.com',
    'vimeo.com',
    'your-finance.us',
    'qy.58.com',
    'vimeo.com',
    'medium.com',
    'goo.gl',
    'onlinecareer360.com',
    'fb.com',
    'github.com',
    'thetopperson.com',
    'soundcloud.com',
    'fb.me',
    'fiverr.com',
    'tinyurl.com',
    'wikepedia.org',
    'personalcreditsolutions.info',
    'open.spotify.com',
    'amazon.com',
    't.me',
    'wa.me',
    'apple.com',
    'upwork.com',
    'forms.gle',
    'about.me',
    'mailchi.mp'
]

# Global list to hold registered UDF functions
UDF_REGISTRY = []

# registers the UDF
def sf_udf(func):
    UDF_REGISTRY.append(func.__name__)
    
    # Wrapper function
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    
    return wrapper

# Function to get all registered UDFs
def get_udfs():
    return UDF_REGISTRY


def remove_protocol(url):
    if isnull(url):
        return None
    match = re.match(r"https?://(.*)", url)
    if match:
        return match.group(1)
    return url

def remove_www(url):
    if isnull(url):
        return None
    match = re.match(r"www\.(.*)", url)
    if match:
        return match.group(1)
    return url

def fix_url(url):
    if not isnull(url):
        return url.replace("%25", "%").replace("%00", "")
    return None

def clean_encoding(value):
    if not isnull(value):
        return fix_encoding(value)
    return None

def remove_query(url):
    if not isnull(url):
        return url.split("?")[0]
    return None

def remove_country_code_prefix(url):
    if re.match(r"[a-z]{2}\.", url):
        return url[3:]
    return url

def remove_extra_path(url):
    match = re.match(r"(linkedin.com/(in|company|groups|school|learning/certificates|learning)/[^/]+).*", url)
    if match:
        return match.group(1)
    return url

def clean_url(value, linkedin=False):
    if isnull(value):
        return None

    url = remove_protocol(value)
    url = remove_www(url)
    url = fix_url(url)
    url = clean_encoding(url)
    url = remove_query(url)

    if linkedin:
        url = remove_country_code_prefix(url)
        url = remove_extra_path(url)

    if isnull(url):
        return None

    try:
        return hyperlink.parse(url).normalize()
    except hyperlink._url.URLParseError as e:
        if "port must not be empty" in str(e):
            return None
        else:
            raise e


def isnull(value: Union[str, None]) -> bool:
    """
    Checks if the value is considered null.
    """
    return value is None or value in ['', '.', '-', 'nan', '--', '..', 'NONE', ',', 'null']


# Unescaping HTML if needed (not strictly necessary for most LinkedIn URLs)
def unescape_html(value):
    import html
    return html.unescape(value)


