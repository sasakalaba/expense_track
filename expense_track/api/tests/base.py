import json
from datetime import datetime
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from expense_trackapp.models import Expense


class BaseTestCase(TestCase):
    def setUp(self):
        # Set users.
        self.user = User.objects.create_user(
            username='foobar',
            email='foo@bar.com',
            password='foobar'
        )
        self.user2 = User.objects.create_user(
            username='foobar2',
            email='foo@bar2.com',
            password='mypassword'
        )

        # Set objects.
        self.now = datetime.now()
        self.expense = Expense.objects.create(
            amount=float(666), user=self.user, date=self.now.date(), time=self.now.time())
        self.expense2 = Expense.objects.create(
            amount=float(999), user=self.user2, date=self.now.date(), time=self.now.time())

    def assertEndpoint(
            self, url_name, method, form_data, expected_response_data,
            expected_status_code, url_kwargs=None, manual_check=[], order=False):
        """
        Custom assert for checking endpoint response values and HTTP
        status codes.
        Manual check is a list of all the values from response data that needs
        to be manually checked (like hashed passwords). If there are any
        manual check values present, they are returned as a dict.
        If specific ordering is required inside returned data for testing
        purposes, set order to True.
        """
        def sort_dict(dataset1, dataset2):
            """
            Checks the dictionaries for any lists, and sorts them.
            """
            for value1, value2 in zip(dataset1, dataset2):
                if isinstance(dataset1[value1], list):
                    dataset1[value1].sort()
                if isinstance(dataset2[value2], list):
                    dataset2[value2].sort()

        url = reverse(url_name, kwargs=url_kwargs)
        allowed_methods = {
            'get': self.client.get,
            'post': self.client.post,
            'put': self.client.put,
            'patch': self.client.patch,
            'delete': self.client.delete
        }
        if method in allowed_methods:
            response = allowed_methods[method](url, form_data)
        else:
            raise ValueError('\'%s\' is not a supported method.' % method)

        # Separate any data that we need to manually check
        manual_data = {}
        for check in manual_check:
            if check in expected_response_data:
                expected_response_data.pop(check)
            if check in response.data:
                manual_data[check] = response.data.pop(check)

        # Convert OrderedDict to dict
        response_data = json.loads(json.dumps(response.data))

        if response_data:
            # Check for pagination
            if 'results' in response_data:
                response_data = response_data['results']

            # If there are lists present, sort them
            if isinstance(response_data, list):
                response_data.sort(), expected_response_data.sort()
                for data1, data2 in zip(response_data, expected_response_data):
                    if isinstance(data1, dict) and isinstance(data2, dict):
                        sort_dict(data1, data2)
            elif isinstance(response_data, dict) and order:
                pass
            elif isinstance(response_data, dict):
                sort_dict(response_data, expected_response_data)
            else:
                raise ValueError('Response data must be a list or a dict.')

        self.assertEqual(response_data, expected_response_data)
        self.assertEqual(response.status_code, expected_status_code)

        return manual_data
