from collections import deque, namedtuple
import urllib.parse

import requests
import tinycss2
from typing import List
from bs4 import BeautifulSoup

from scanner.utils import extract_strings, extract_urls


Asset = namedtuple('Asset', ['resource', 'kind', 'initiator'])


def extract_assets(soup: BeautifulSoup, site_url: str) -> List[Asset]:
    assets = []

    images = soup.find_all('img')
    for image in images:
        if 'src' in image.attrs:
            assets.append(
                Asset(
                    resource=image.attrs['src'],
                    kind='img-src',
                    initiator=site_url
                )
            )

    scripts = soup.find_all('script')
    for script in scripts:
        if 'src' in script.attrs:
            # externally loaded js
            assets.append(
                Asset(
                    resource=script.attrs['src'],
                    kind='script-src',
                    initiator=site_url,
                )
            )

            response = fetch_asset(script.attrs['src'], site_url)
            # assets in content from external js
            for text in extract_strings(response.text):
                for url in extract_urls(text):
                    assets.append(Asset(resource=url, kind='script-resource', initiator=script.attrs['src']))
        # js embedded in <script> tags
        else:
            for text in extract_strings(script.get_text()):
                for url in extract_urls(text):
                    assets.append(
                        Asset(resource=url, kind='script-embed', initiator=site_url)
                    )

    iframe_tags = soup.find_all('iframe')
    for tag in iframe_tags:
        if tag.has_attr('src'):
            assets.append(Asset(resource=tag.attrs['src'], kind='iframe-src', initiator=site_url))

    stylesheet_links = soup.find_all('link', rel='stylesheet')
    for link in stylesheet_links:
        if link.attrs.get('href'):
            response = fetch_asset(link.attrs['href'], site_url)
            # assets in content from stylesheet link
            for url in urls_from_css(response.text):
                assets.append(Asset(resource=url, kind='style-resource', initiator=link.attrs['href']))

            # stylesheet link
            assets.append(Asset(resource=link.attrs['href'], kind='style-href', initiator=site_url))

    # css embedded in <style> tags
    style_tags = soup.find_all('style')
    for tag in style_tags:
        for item in tag.contents:
            if isinstance(item, str):
                for url in urls_from_css(item):
                    assets.append(Asset(resource=url, kind='style-embed', initiator=site_url))

    # inline styles
    for tag in soup.select('[style]'):
        for url in urls_from_css_declarations(tag.attrs['style']):
            assets.append(Asset(resource=url, kind='style-resource-inline', initiator=site_url))

    return assets


def urls_from_css_declarations(css_text: str) -> List[str]:
    """Parse text consisting of one or more CSS declarations and return a
    list of urls found within.  The CSS text given should not include
    any selectors.

    """
    urls = []
    for declaration in tinycss2.parse_declaration_list(css_text):
        for token in declaration.value:
            if getattr(token, 'type', '') == 'url':
                urls.append(token.value)
    return urls


def urls_from_css(css_text: str) -> List[str]:
    """Given CSS text, parse it and return all URLs found"""
    urls = []
    nodes = tinycss2.parse_stylesheet(css_text)
    for node in descendants(nodes):
        if getattr(node, 'type', '') == 'url':
            urls.append(node.value)
    return urls


def descendants(nodes):
    """Crawl a list of tinycss2-parsed nodes and return all descendants"""
    to_crawl = deque(nodes)
    children = []
    while to_crawl:
        current = to_crawl.popleft()
        children.append(current)
        prelude = getattr(current, 'prelude', [])
        if prelude:
            to_crawl.extend(prelude)
        content = getattr(current, 'content', [])
        if content:
            to_crawl.extend(content)
    return children


def fetch_asset(asset_url: str, site_url: str) -> requests.models.Response:
    site_url = urllib.parse.urlparse(site_url)
    asset_url = urllib.parse.urlparse(asset_url)

    if not asset_url.scheme:
        asset_url = asset_url._replace(scheme=site_url.scheme)
    if not asset_url.netloc:
        asset_url = asset_url._replace(netloc=site_url.netloc)

    return requests.get(asset_url.geturl())
