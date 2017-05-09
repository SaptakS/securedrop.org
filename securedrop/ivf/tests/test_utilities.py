from bs4 import BeautifulSoup
from unittest import mock

from django.test import TestCase

from ivf import utils


class VerificationUtilityTest(TestCase):
    def test_https_is_in_url(self):
        self.assertTrue(utils.validate_https('https://example.com'))

    def test_https_is_not_in_url(self):
        self.assertFalse(utils.validate_https('example.com'))

    def test_onion_link_is_in_href(self):
        test_html = "<a href='notavalidaddress.onion'>SecureDrop</a>"
        soup = BeautifulSoup(test_html, "lxml")
        self.assertFalse(utils.validate_onion_address_not_in_href(soup))

    def test_onion_link_is_not_in_href(self):
        test_html = "Go to notavalidaddress.onion and leak dem docs"
        soup = BeautifulSoup(test_html, "lxml")
        self.assertTrue(utils.validate_onion_address_not_in_href(soup))

    def test_url_does_not_have_subdomain(self):
        self.assertFalse(utils.validate_subdomain('https://example.com/securedrop'))

    def test_url_does_have_subdomain(self):
        self.assertTrue(utils.validate_subdomain('https://securedrop.example.com'))

    def test_www_url_does_not_have_subdomain(self):
        self.assertFalse(utils.validate_subdomain('https://www.example.com/securedrop'))

    def test_server_header_software_present(self):
        page = mock.Mock()
        page.headers = {'Server': 'nginx'}
        self.assertFalse(utils.validate_server_software(page))

    def test_server_header_software_not_present(self):
        page = mock.Mock()
        page.headers = {'Server': ''}
        self.assertTrue(utils.validate_server_software(page))

    def test_server_header_version_not_present(self):
        page = mock.Mock()
        page.headers = {'Server': ''}
        self.assertTrue(utils.validate_server_version(page))

    def test_server_header_version_is_present(self):
        page = mock.Mock()
        page.headers = {'Server': '6.6.6'}
        self.assertFalse(utils.validate_server_version(page))

    def test_cloudflare_headers_not_present(self):
        page = mock.Mock()
        page.headers = {'Server': ''}
        self.assertTrue(utils.validate_not_using_cdn(page))

    def test_cloudflare_headers_present(self):
        page = mock.Mock()
        page.headers = {'CF-Cache-Status': 'weeee'}
        self.assertFalse(utils.validate_not_using_cdn(page))

    def test_google_analytics_present(self):
        page = mock.Mock()
        page.content = '<script src="analytics.js"></script>'
        self.assertFalse(utils.validate_not_using_analytics(page))

    def test_google_analytics_not_present(self):
        page = mock.Mock()
        page.content = '<h1>My Good SecureDrop Landing Page</h1>'
        self.assertTrue(utils.validate_not_using_analytics(page))

    def test_csp_not_present(self):
        page = mock.Mock()
        page.headers = {'Content-Security-Policy': 'Random Crazy Value'}
        self.assertFalse(utils.validate_csp(page))

    def test_csp_present(self):
        page = mock.Mock()
        page.headers = {'Content-Security-Policy': "default-src 'self'"}
        self.assertTrue(utils.validate_csp(page))

    def test_xss_protection_not_present(self):
        page = mock.Mock()
        page.headers = {'X-XSS-Protection': 'Crazy Value'}
        self.assertFalse(utils.validate_xss_protection(page))

    def test_xss_protection_present(self):
        page = mock.Mock()
        page.headers = {'X-XSS-Protection': '1; mode=block'}
        self.assertTrue(utils.validate_xss_protection(page))

    def test_nosniff_protection_not_present(self):
        page = mock.Mock()
        page.headers = {'X-Content-Type-Options': 'Crazy Value'}
        self.assertFalse(utils.validate_no_sniff(page))

    def test_nosniff_protection_not_present(self):
        page = mock.Mock()
        page.headers = {'X-Content-Type-Options': 'nosniff'}
        self.assertTrue(utils.validate_no_sniff(page))

    def test_no_download_option_not_present(self):
        page = mock.Mock()
        page.headers = {'X-Download-Options': 'open'}
        self.assertFalse(utils.validate_download_options(page))

    def test_no_download_option_present(self):
        page = mock.Mock()
        page.headers = {'X-Download-Options': 'noopen'}
        self.assertTrue(utils.validate_download_options(page))

    def test_clickjacking_protection_not_present(self):
        page = mock.Mock()
        page.headers = {'X-Frame-Options': 'ALLOW'}
        self.assertFalse(utils.validate_clickjacking_protection(page))

    def test_clickjacking_protection_present(self):
        page = mock.Mock()
        page.headers = {'X-Frame-Options': 'DENY'}
        self.assertTrue(utils.validate_clickjacking_protection(page))

    def test_cross_domain_policy_not_set_properly(self):
        page = mock.Mock()
        page.headers = {'X-Permitted-Cross-Domain-Policies': 'Crazy'}
        self.assertFalse(utils.validate_cross_domain_policy(page))

    def test_cross_domain_policy_set_properly(self):
        page = mock.Mock()
        page.headers = {'X-Permitted-Cross-Domain-Policies': 'master-only'}
        self.assertTrue(utils.validate_cross_domain_policy(page))

    def test_pragma_header_not_disabling_caching(self):
        page = mock.Mock()
        page.headers = {'Pragma': 'so-much-cache'}
        self.assertFalse(utils.validate_pragma(page))

    def test_pragma_header_disabling_caching(self):
        page = mock.Mock()
        page.headers = {'Pragma': 'no-cache'}
        self.assertTrue(utils.validate_pragma(page))

    def test_expires_header_not_disabling_caching(self):
        page = mock.Mock()
        page.headers = {'Expires': '10033213'}
        self.assertFalse(utils.validate_expires(page))

    def test_expires_header_disabling_caching(self):
        page = mock.Mock()
        page.headers = {'Expires': '-1'}
        self.assertTrue(utils.validate_expires(page))

    def test_cache_control_set(self):
        page = mock.Mock()
        page.headers = {'Cache-Control': ''}
        self.assertTrue(utils.validate_cache_control_set(page))

    def test_cache_control_not_set(self):
        page = mock.Mock()
        page.headers = {'Expires': '-1'}
        self.assertFalse(utils.validate_cache_control_set(page))

    def test_cache_control_must_revalidate_set(self):
        page = mock.Mock()
        page.headers = {'Cache-Control': 'must-revalidate'}
        self.assertTrue(utils.validate_cache_must_revalidate(page))

    def test_cache_control_must_revalidate_set(self):
        page = mock.Mock()
        page.headers = {'Cache-Control': 'must-not-revalidate'}
        self.assertFalse(utils.validate_cache_must_revalidate(page))

    def test_cache_control_validate_nocache_set(self):
        page = mock.Mock()
        page.headers = {'Cache-Control': 'no-cache'}
        self.assertTrue(utils.validate_nocache(page))

    def test_cache_control_validate_nocache_not_set(self):
        page = mock.Mock()
        page.headers = {'Cache-Control': 'cache'}
        self.assertFalse(utils.validate_nocache(page))

    def test_cache_control_validate_notransform_set(self):
        page = mock.Mock()
        page.headers = {'Cache-Control': 'no-transform'}
        self.assertTrue(utils.validate_notransform(page))

    def test_cache_control_validate_notransform_not_set(self):
        page = mock.Mock()
        page.headers = {'Cache-Control': 'transform'}
        self.assertFalse(utils.validate_notransform(page))

    def test_cache_control_validate_nostore_set(self):
        page = mock.Mock()
        page.headers = {'Cache-Control': 'no-store'}
        self.assertTrue(utils.validate_nostore(page))

    def test_cache_control_validate_nostore_not_set(self):
        page = mock.Mock()
        page.headers = {'Cache-Control': 'store'}
        self.assertFalse(utils.validate_nostore(page))

    def test_cache_control_validate_nostore_set(self):
        page = mock.Mock()
        page.headers = {'Cache-Control': 'private'}
        self.assertTrue(utils.validate_private(page))

    def test_cache_control_validate_nostore_not_set(self):
        page = mock.Mock()
        page.headers = {'Cache-Control': 'public'}
        self.assertFalse(utils.validate_private(page))

    @mock.patch('requests.get')
    def test_results_return_if_failed_to_get_page(self, get):
        page = utils.LandingPage('https://example.org')
        results = page.request_and_scrape_page()
        self.assertEqual(results['no_cdn'], None)
