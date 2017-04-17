from django.test import TestCase
from .helpers import confirm_password
from django.core.exceptions import ValidationError


class HelperMethodsTest(TestCase):
    def test_confirm_password(self):
        """
        confirm_password test.
        """

        # Raise ValidationError if passwords do not match.
        with self.assertRaises(ValidationError) as validation_error:
            confirm_password('foo', 'bar')
        self.assertEqual(
            validation_error.exception.messages[0], 'Passwords must match.')

        # Correct match.
        confirm_password('foobar', 'foobar')
