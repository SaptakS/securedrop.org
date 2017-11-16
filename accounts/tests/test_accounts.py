from time import time

from django.test import TestCase
from django.test import Client
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse_lazy
from allauth.account.models import EmailAddress
from django_otp.plugins.otp_totp.models import TOTPDevice
from landing_page_checker.tests.factories import SecuredropPageFactory
from landing_page_checker.models import SecuredropOwner


class UnauthenticatedTest(TestCase):
    def setUp(self):
        self.client = Client()

        self.unowned_sd_page = SecuredropPageFactory()

    def test_unauthenticated_is_redirected_to_login_dashboard(self):
        response = self.client.get(reverse_lazy('dashboard'), follow=True)
        # gets last address directed to and removes queries
        response_last_address = response.redirect_chain[-1][0].split('?')[0]
        self.assertEqual(response_last_address, reverse_lazy('account_login'))

    def test_unauthenticated_is_redirected_to_login_details(self):
        slug = self.unowned_sd_page.slug
        response = self.client.get(
            reverse_lazy('securedrop_detail', kwargs={'slug': slug}),
            follow=True,
        )
        response_last_address = response.redirect_chain[-1][0].split('?')[0]
        self.assertEqual(response_last_address, reverse_lazy('account_login'))


class AuthenticatedTest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.client = Client()
        self.username = "Rachel"
        self.email = "r@r.com"
        self.password = "rachel"
        self.user = User.objects.create_user(username=self.username, email=self.email, password=self.password, is_active=True)
        self.user.save()
        # Create a verified email address object for this user via allauth
        EmailAddress.objects.create(user=self.user, email=self.email, verified=True)

        self.unowned_sd_page = SecuredropPageFactory()
        self.unowned_sd_page.save()
        self.user_owned_sd_page = SecuredropPageFactory()
        self.user_owned_sd_page.save()
        SecuredropOwner(owner=self.user, page=self.user_owned_sd_page).save()
        # Login
        self.client.post(reverse_lazy('account_login'), {'login': self.email, 'password': self.password})

    def test_authenticated_login_should_redirect_to_2fa_setup(self):
        """login without setting up a device should redirect to 2FA setup page"""
        response = self.client.post(
            reverse_lazy('account_login'),
            {'login': self.email, 'password': self.password},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse_lazy('two-factor-setup'))

    def test_authenticated_user_cannot_view_dashboard(self):
        """dashboard should redirect unverified users users to the login page"""
        response = self.client.get(reverse_lazy('dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse_lazy('account_login'))


class VerifiedTest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.client = Client()
        self.username = "Rachel"
        self.email = "r@r.com"
        self.password = "rachel"
        self.user = User.objects.create_user(username=self.username, email=self.email, password=self.password, is_active=True)

        self.unowned_sd_page = SecuredropPageFactory()
        self.unowned_sd_page.save()
        self.user_owned_sd_page = SecuredropPageFactory()
        self.user_owned_sd_page.save()
        SecuredropOwner(owner=self.user, page=self.user_owned_sd_page).save()

        # Create a verified email address object for this user via allauth
        EmailAddress.objects.create(user=self.user, email=self.email, verified=True)

        # Create a device with pre-determined parameters to allow 2FA
        # token verification.  Numbers copied from django_otp unit
        # tests.
        device = TOTPDevice.objects.create(
            user=self.user,
            confirmed=True,
            key='2a2bbba1092ffdd25a328ad1a0a5f5d61d7aacc4',
            step=30,
            t0=int(time() - (30 * 3)),
            digits=6,
            tolerance=0,
            drift=0,
        )
        self.client.post(
            reverse_lazy('account_login'),
            {'login': self.email, 'password': self.password},
        )
        self.client.post(
            reverse_lazy('two-factor-authenticate'),
            # The token below corresponds to the parameters on the
            # device just created.
            {'otp_device': device.id, 'otp_token': '154567'},
        )

    def test_verified_user_can_view_dashboard(self):
        response = self.client.get(reverse_lazy('dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_verified_user_can_view_their_instances(self):
        slug = self.user_owned_sd_page.slug
        response = self.client.get(reverse_lazy('securedrop_detail', kwargs={'slug': slug}))
        self.assertEqual(response.status_code, 200)

    def test_verified_user_cannot_view_other_instances(self):
        slug = self.unowned_sd_page.slug
        response = self.client.get(reverse_lazy('securedrop_detail', kwargs={'slug': slug}))
        self.assertEqual(response.status_code, 403)

    def test_verified_user_can_edit_their_instances(self):
        new_title = 'New'
        slug = self.user_owned_sd_page.slug
        response = self.client.post(
            reverse_lazy('securedrop_detail', kwargs={'slug': slug}),
            {
                'title': new_title,
                # The autocomplete widget parses the below form values
                # as JSON, and 'null' is the least obtrusive value to
                # send.
                'languages': 'null',
                'topics': 'null',
                'countries': 'null',
            },
        )
        self.assertEqual(response.status_code, 200)

    def test_verified_user_cannot_edit_other_instances(self):
        new_title = 'New'
        slug = self.unowned_sd_page.slug
        response = self.client.post(
            reverse_lazy('securedrop_detail', kwargs={'slug': slug}),
            {
                'title': new_title,
                # The autocomplete widget parses the below form values
                # as JSON, and 'null' is the least obtrusive value to
                # send.
                'languages': 'null',
                'topics': 'null',
                'countries': 'null',
            }
        )
        self.assertEqual(response.status_code, 403)
