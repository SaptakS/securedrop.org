from unittest import TestCase, skip, mock

from bs4 import BeautifulSoup

from scanner.assets import (
    Asset,
    extract_assets,
    urls_from_css,
    urls_from_css_declarations,
)


class AssetExtractionTestCase(TestCase):
    def setUp(self):
        self.test_url = 'http://www.example.com'

    def test_should_extract_images(self):
        html = """
        <html><body><img src="image.jpg"></body></html>
        """
        soup = BeautifulSoup(html, "lxml")

        self.assertEqual([
            Asset(
                resource='image.jpg',
                kind='img-src',
                initiator=self.test_url,
            )],
            extract_assets(soup, self.test_url))

    @mock.patch('scanner.assets.requests')
    def test_should_extract_external_scripts(self, mock_requests):
        mock_requests.get.return_value = mock.Mock(
            text=''
        )
        html = """
        <html><head><script src="script.js"></head><body></body></html>
        """
        soup = BeautifulSoup(html, "lxml")

        self.assertEqual([
            Asset(
                resource='script.js',
                kind='script-src',
                initiator=self.test_url
            )],
            extract_assets(soup, self.test_url))

    def test_should_extract_embedded_scripts_with_urls(self):
        html = """
        <html><head><script>var url = 'http://www.example.org';</script></head><body></body></html>
        """
        soup = BeautifulSoup(html, "lxml")
        self.assertEqual(
            extract_assets(soup, self.test_url),
            [Asset(
                resource='http://www.example.org',
                kind='script-embed',
                initiator=self.test_url
            )],
        )

    def test_should_extract_urls_from_iframes(self):
        html = """
        <html><body><iframe src="https://www.example.org/embed.html"></iframe></body></html>
        """
        soup = BeautifulSoup(html, "lxml")

        self.assertEqual([
            Asset(
                resource='https://www.example.org/embed.html',
                kind='iframe-src',
                initiator=self.test_url,
            )],
            extract_assets(soup, self.test_url)
        )

    @mock.patch('scanner.assets.requests')
    def test_should_extract_links_to_stylesheets(self, mock_requests):
        html = """
        <html><head><link href="/media/example.css" rel="stylesheet"></head><body></body></html>
        """

        soup = BeautifulSoup(html, "lxml")

        self.assertEqual([
            Asset(
                resource='/media/example.css',
                kind='style-href',
                initiator=self.test_url
            )],
            extract_assets(soup, self.test_url)
        )

    def test_should_extract_urls_in_embedded_css(self):
        html = """<html><head><style>
        div {
          background-image: url("https://example.org/files/example.png");
        }
        </style></head><body></body></html>"""

        soup = BeautifulSoup(html, "lxml")

        self.assertEqual([
            Asset(
                resource='https://example.org/files/example.png',
                kind='style-embed',
                initiator=self.test_url,
            )],
            extract_assets(soup, self.test_url)
        )

    def test_should_extract_urls_in_inline_css(self):
        html = """<html>
        <body style="background-image: url('https://example.org/files/example.png')"></body></html>"""
        soup = BeautifulSoup(html, "lxml")
        self.assertEqual([
            Asset(
                resource='https://example.org/files/example.png',
                kind='style-resource-inline',
                initiator=self.test_url,
            )],
            extract_assets(soup, self.test_url)
        )

    @mock.patch('scanner.assets.requests')
    def test_should_extract_urls_in_linked_css(self, requests_mock):
        requests_mock.get.return_value = mock.Mock(
            text='selector { background-image: url("https://example.org/example.png") }'
        )
        html = """
        <html><head><link href="https://example.org/styles.css" rel="stylesheet"></head><body></body></html>"""
        soup = BeautifulSoup(html, "lxml")
        self.assertEqual(
            set(extract_assets(soup, self.test_url)), {
                Asset(
                    resource='https://example.org/styles.css',
                    kind='style-href',
                    initiator=self.test_url,
                ),
                Asset(
                    resource='https://example.org/example.png',
                    kind='style-resource',
                    initiator='https://example.org/styles.css',
                ),
            }
        )

    @mock.patch('scanner.assets.requests')
    def test_should_extract_urls_in_external_js(self, mock_requests):
        mock_requests.get.return_value = mock.Mock(
            text="""function makeRequest() { $.getJSON('http://example.org/', function(data) {}); }"""
        )

        html = """
        <html><head><script src="file.js""></head><body></body></html>
        """
        soup = BeautifulSoup(html, "lxml")
        self.assertEqual(
            [
                Asset(
                    resource='file.js',
                    kind='script-src',
                    initiator=self.test_url,
                ),
                Asset(
                    resource='http://example.org/',
                    kind='script-resource',
                    initiator='file.js',
                ),
            ],
            extract_assets(soup, self.test_url)
        )

    @skip
    def test_should_extract_urls_from_embedded_js(self):
        pass


class TestCssUrlExtractionFromDeclarations(TestCase):
    def test_should_extract_urls_from_css_declarations(self):
        css = 'background-image: url("http://www.example.com");'
        self.assertEqual(
            urls_from_css_declarations(css),
            ['http://www.example.com']
        )

    def test_should_extract_urls_from_multiproperty_declarations(self):
        css = "list-style: square url(http://www.example.com/redball.png);"
        self.assertEqual(urls_from_css_declarations(css),
                         ['http://www.example.com/redball.png'])


class TestCssUrlExtraction(TestCase):
    def test_should_extract_urls_from_at_import_rules(self):
        css = '@import url("thing.css");'
        self.assertEqual(urls_from_css(css), ['thing.css'])

    def test_should_extract_urls_from_multiple_selectors(self):
        css = """
              article {
                background-image: url(example.png);
              }
              section {
                background-image: url(example2.png);
              }
        """
        self.assertEqual(urls_from_css(css), ['example.png', 'example2.png'])

    def test_should_extract_urls_from_nested_at_rules(self):
        css = """
              @supports (display: flex) {
                @media screen and (min-width: 900px) {
                  article {
                    display: flex;
                    background-image: url("example.png");
                  }
                }
              }
        """
        self.assertEqual(urls_from_css(css), ['example.png'])

    def test_should_extract_urls_from_multiproperty_declarations(self):
        css = """"
              ul {
                list-style: square url(http://www.example.com/redball.png);
              }
        """
        self.assertEqual(urls_from_css(css),
                         ['http://www.example.com/redball.png'])
