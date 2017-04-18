from django import forms
from django.test import TestCase, Client
from .forms import RegisterForm
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User


class FormsTest(TestCase):
    def setUp(self):
        self.register_data = {
            'username': 'foobar',
            'email': 'foo@bar.com',
            'password1': 'mypassword',
            'password2': 'mypassword',
        }
        self.register_form = RegisterForm()

        # Mock cleaned data.
        self.register_form.cleaned_data = self.register_data.copy()

    def test_register_clean_mail(self):
        """
        Register clean email field validation.
        """

        # Raise ValidationError if email already exists.
        User.objects.create_user(
            email='foo@bar.com', username='foobar', password='mypassword')
        with self.assertRaises(forms.ValidationError) as validation_error:
            self.register_form.clean_email()
        self.assertEqual(
            validation_error.exception.messages[0], 'Email already in use.')

        # Ensure that unique email will pass validation.
        User.objects.get().delete()
        self.assertEqual('foo@bar.com', self.register_form.clean_email())

    def test_register_clean(self):
        """
        Register clean validation.
        """

        # Make sure password1 and password2 arguments are properly removed and
        # a generic password argument is set.
        expected_data = {
            'username': 'foobar',
            'email': 'foo@bar.com',
            'password': 'mypassword'
        }
        self.assertEqual(self.register_form.clean(), expected_data)

        # Make sure that missing password arguments wont break our app.
        self.register_form.cleaned_data = self.register_data.copy()
        self.register_form.cleaned_data.pop('password1')
        self.register_form.cleaned_data.pop('password2')
        expected_data['password'] = None
        self.assertEqual(self.register_form.clean(), expected_data)


class ViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='foobar',
            email='foo@bar.com',
            password='mypassword'
        )

    def test_login(self):
        """
        Login test.
        """
        login_data = {
            'username': 'foobar1',
            'password': 'mypassword'
        }
        self.client.logout()

        # Login template.
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/login.html')

        # Wrong credentials.
        self.assertFalse(self.client.login(**login_data))

        # Unauthorized redirect.
        response = self.client.get(reverse('index'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/login.html')

        # Authorized redirect.
        login_data['username'] = 'foobar'
        response = self.client.post(reverse('login'), login_data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')
        self.assertTrue(self.client.login(**login_data))

    def test_logout(self):
        """
        Logout test.
        """

        # Redirect to login.
        response = self.client.get(reverse('logout'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/login.html')

    def test_register_basic(self):
        """
        Register basic functionality test.
        """

        register_data = {
            'username': 'foobar1',
            'email': 'foo@bar1.com',
            'password1': 'mypassword',
            'password2': 'mypassword',
        }

        # Register template.
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/register.html')

        # Successful registration.
        response = self.client.post(
            reverse('register'), register_data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/login.html')

    def test_register_unique_values(self):
        """
        Register unique values test.
        """

        # Raise errors by using an existing user register data.
        register_data = {
            'username': 'foobar',
            'email': 'foo@bar.com',
            'password1': 'mypassword',
            'password2': 'mypassword1',
        }

        # Registration with used email.
        response = self.client.post(reverse('register'), register_data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/register.html')
        self.assertIn('Email already in use.', response.content)

        # Register with mismatching passwords.
        self.assertIn(
            'The two password fields didn&#39;t match.', response.content)

        # Register with same username.
        self.assertIn(
            'A user with that username already exists.', response.content)

        # Registration with invalid email.
        register_data['email'] = 'foobar2.com'
        response = self.client.post(reverse('register'), register_data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/register.html')
        self.assertIn('Enter a valid email address.', response.content)

    def test_register_missing_values(self):
        """
        Register missing values test.
        """

        response = self.client.post(reverse('register'), {})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/register.html')
        self.assertEqual(response.content.count('This field is required.'), 4)
