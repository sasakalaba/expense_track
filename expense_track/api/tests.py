import json
from datetime import datetime
from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient
from expense_trackapp.models import Expense
from mock import MagicMock, call
from .permissions import IsOwnerOrReadOnly
from .views import ExpenseViewSet


class BaseTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='foobar',
            email='foo@bar.com',
            password='foobar'
        )

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


class PermissionsTest(BaseTestCase):
    def setUp(self):
        super(PermissionsTest, self).setUp()
        self.user.is_superuser = True
        self.user.save()
        self.request = MagicMock(user=self.user)
        self.view = MagicMock(kwargs={'username': 'foobar'})
        self.is_owner_or_read_only = IsOwnerOrReadOnly()

    def test_is_owner_or_read_only_has_permission(self):
        """
        has_permission test.
        """

        # Superuser check.
        self.assertTrue(
            self.is_owner_or_read_only.has_permission(self.request, self.view))

        # Allowed user check.
        self.user.is_superuser = False
        self.user.save()
        self.assertTrue(
            self.is_owner_or_read_only.has_permission(self.request, self.view))

        # Denied permission check.
        self.view.kwargs['username'] = 'wrong_user'
        self.assertFalse(
            self.is_owner_or_read_only.has_permission(self.request, self.view))

    def test_is_owner_or_read_only_has_object_permission(self):
        """
        has_object_permission test.
        """

        obj = MagicMock(user=self.user)

        # Superuser check.
        self.assertTrue(self.is_owner_or_read_only.has_object_permission(
            self.request, self.view, obj))

        # Allowed user check.
        self.user.is_superuser = False
        self.user.save()
        self.assertTrue(self.is_owner_or_read_only.has_object_permission(
            self.request, self.view, obj))

        # Denied permission check.
        obj.user = User.objects.create_user(
            username='foobar2', email='foo@bar2.com', password='mypassword'
        )
        self.assertFalse(self.is_owner_or_read_only.has_object_permission(
            self.request, self.view, obj))


class AccountTest(BaseTestCase):
    def test_login(self):
        """
        Login test.
        """

        # Log our user once so a token is generated.
        form_data = {'username': 'foobar', 'password': 'foobar'}
        self.client.post(reverse('account_login'), form_data)
        token = Token.objects.get()
        return_data = {
            'token': token.key
        }

        # Ensure that successful login will return a user token.
        self.assertEndpoint(
            'account_login', 'post', form_data, return_data, status.HTTP_200_OK)
        self.assertEqual(token.user, self.user)

        # Unsuccessful login 400 error.
        form_data = {'username': 'foobar1', 'password': 'foobar'}
        return_data = {
            'non_field_errors': ['Unable to log in with provided credentials.']
        }
        self.assertEndpoint(
            'account_login', 'post', form_data, return_data, status.HTTP_400_BAD_REQUEST)

    def test_register(self):
        """
        Register test.
        """

        # Ensure that successful register will return a user object.
        form_data = {
            'username': 'foobar1',
            'password': 'foobar1',
            'confirm_password': 'foobar1',
            'email': 'foo@bar1.com'
        }
        return_data = {
            'username': 'foobar1',
            'email': 'foo@bar1.com'
        }
        self.assertEndpoint(
            'account_register', 'post', form_data, return_data, status.HTTP_201_CREATED)

        # Register with same username/email error.
        return_data = {
            'email': ['This field must be unique.'],
            'username': ['A user with that username already exists.']
        }
        self.assertEndpoint(
            'account_register', 'post', form_data, return_data, status.HTTP_400_BAD_REQUEST)

        # Ensure that all register fields are required.
        form_data = {}
        return_data = {
            'username': ['This field is required.'],
            'email': ['This field is required.'],
            'password': ['This field is required.']
        }
        self.assertEndpoint(
            'account_register', 'post', form_data, return_data, status.HTTP_400_BAD_REQUEST)

        # Mismatching passwords error.
        form_data = {
            'username': 'foobar2',
            'password': 'foobar2',
            'confirm_password': 'foobar1',
            'email': 'foo@bar2.com'
        }
        return_data = {
            'non_field_errors': ['Passwords must match.']
        }
        self.assertEndpoint(
            'account_register', 'post', form_data, return_data, status.HTTP_400_BAD_REQUEST)


class ExpenseViewSetTest(BaseTestCase):
    def setUp(self):
        super(ExpenseViewSetTest, self).setUp()
        self.user.is_superuser = True
        self.user.save()
        self.request = MagicMock(user=self.user)
        self.expense_view = ExpenseViewSet(request=self.request)
        self.user2 = User.objects.create_user(
            username='foobar2',
            email='foo@bar2.com',
            password='mypassword'
        )
        self.serializer = MagicMock(initial_data={'user': self.user2})

        # Set objects.
        self.now = datetime.now()
        self.expense = Expense.objects.create(
            amount=float(666), user=self.user, date=self.now.date(), time=self.now.time())
        self.expense2 = Expense.objects.create(
            amount=float(999), user=self.user2, date=self.now.date(), time=self.now.time())

    def test_get_queryset(self):
        """
        get_queryset test.
        """

        # Superuser check.
        self.assertEqual(
            list(self.expense_view.get_queryset()), [self.expense, self.expense2])

        # Regular user check.
        self.user.is_superuser = False
        self.user.save()
        self.assertEqual(
            list(self.expense_view.get_queryset()), [self.expense, ])

    def test_perform_create(self):
        """
        perform_create test.
        """

        # Superuser check.
        self.expense_view.perform_create(serializer=self.serializer)
        self.assertEqual(
            self.serializer.method_calls[0], call.save(user=self.user2))

        # No initial data.
        self.serializer.initial_data = {}
        self.expense_view.perform_create(serializer=self.serializer)
        self.assertEqual(
            self.serializer.method_calls[1], call.save(user=self.user))

        # Staff user check.
        self.user.is_superuser = False
        self.user.is_staff = True
        self.user.save()
        self.assertIsNone(
            self.expense_view.perform_create(serializer=self.serializer))

        # Regular user check.
        self.user.is_staff = False
        self.user.save()
        self.expense_view.perform_create(serializer=self.serializer)
        self.assertEqual(
            self.serializer.method_calls[2], call.save(user=self.user))


class ExpensesTest(BaseTestCase):
    def setUp(self):
        super(ExpensesTest, self).setUp()
        self.user2 = User.objects.create_user(
            username='foobar2',
            email='foo@bar2.com',
            password='mypassword'
        )

        # Set authorization.
        self.token = Token.objects.create(user=self.user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        # Set objects.
        self.now = datetime.now()
        self.expense = Expense.objects.create(
            amount=float(666), user=self.user, date=self.now.date(), time=self.now.time())
        self.expense2 = Expense.objects.create(
            amount=float(999), user=self.user2, date=self.now.date(), time=self.now.time())

        # Set url kwargs.
        self.user1_url_kwargs = {
            'username': self.user.username,
            'pk': self.expense.pk
        }
        self.user2_url_kwargs = {
            'username': self.user2.username,
            'pk': self.expense2.pk
        }

        # Set return data.
        self.expense_return_data = {
            'amount': '666.00',
            'comment': '',
            'date': str(self.now.date()),
            'description': '',
            'pk': self.expense.pk,
            'time': str(self.now.time()),
            'user': 'foobar'
        }
        self.expense2_return_data = {
            'amount': '999.00',
            'comment': '',
            'date': str(self.now.date()),
            'description': '',
            'pk': self.expense2.pk,
            'time': str(self.now.time()),
            'user': 'foobar2'
        }

    def test_list(self):
        """
        List of expenses test.
        """

        # Create new expense for self.user.
        self.expense3 = Expense.objects.create(
            amount=float(333),
            user=self.user,
            date=self.now.date(),
            time=self.now.time()
        )
        self.expense3_return_data = {
            'amount': '333.00',
            'comment': '',
            'date': str(self.now.date()),
            'description': '',
            'pk': self.expense3.pk,
            'time': str(self.now.time()),
            'user': 'foobar'
        }

        form_data = {}
        return_data = [self.expense_return_data, self.expense3_return_data]

        # Set url kwargs.
        self.user1_url_kwargs.pop('pk')
        self.user2_url_kwargs.pop('pk')

        # User can GET only its own records.
        self.assertEndpoint(
            'expense_list',
            'get',
            form_data,
            return_data,
            status.HTTP_200_OK,
            url_kwargs=self.user1_url_kwargs,
        )
        self.assertEndpoint(
            'expense_list',
            'get',
            form_data,
            {'detail': 'You do not have permission to perform this action.'},
            status.HTTP_403_FORBIDDEN,
            url_kwargs=self.user2_url_kwargs
        )

        # Admin can GET everything.
        self.user.is_superuser = True
        self.user.save()
        return_data.append(self.expense2_return_data)

        self.assertEndpoint(
            'expense_list',
            'get',
            form_data,
            return_data,
            status.HTTP_200_OK,
            url_kwargs=self.user1_url_kwargs,
        )

    def test_detail(self):
        """
        Single expense test.
        """

        form_data = {}

        # User can GET only its own records.
        self.assertEndpoint(
            'expense_detail',
            'get',
            form_data,
            self.expense_return_data,
            status.HTTP_200_OK,
            url_kwargs=self.user1_url_kwargs,
        )
        self.assertEndpoint(
            'expense_detail',
            'get',
            form_data,
            {'detail': 'You do not have permission to perform this action.'},
            status.HTTP_403_FORBIDDEN,
            url_kwargs=self.user2_url_kwargs
        )

        # Admin can GET everything.
        self.user.is_superuser = True
        self.user.save()

        self.assertEndpoint(
            'expense_detail',
            'get',
            form_data,
            self.expense2_return_data,
            status.HTTP_200_OK,
            url_kwargs=self.user2_url_kwargs,
        )

    def test_create(self):
        """
        Create expense test.
        """
        form_data = {
            'amount': float(222),
            'date': str(self.now.date()),
            'time': str(self.now.time())
        }
        self.expense4_return_data = {
            'amount': '222.00',
            'comment': '',
            'date': str(self.now.date()),
            'description': '',
            'time': str(self.now.time()),
            'user': 'foobar'
        }
        # Set url kwargs.
        self.user1_url_kwargs.pop('pk')
        self.user2_url_kwargs.pop('pk')

        # User can create only its own records.
        self.assertEndpoint(
            'expense_list',
            'post',
            form_data,
            self.expense4_return_data,
            status.HTTP_201_CREATED,
            url_kwargs=self.user1_url_kwargs,
            manual_check=['pk', ]
        )
        form_data['value'] = float(999)
        self.assertEndpoint(
            'expense_list',
            'post',
            form_data,
            {'detail': 'You do not have permission to perform this action.'},
            status.HTTP_403_FORBIDDEN,
            url_kwargs=self.user2_url_kwargs
        )

        # Admin can create a record for any user.
        self.user.is_superuser = True
        self.user.save()

        # Non specified user will be the current user.
        self.assertEndpoint(
            'expense_list',
            'post',
            form_data,
            self.expense4_return_data,
            status.HTTP_201_CREATED,
            url_kwargs=self.user1_url_kwargs,
            manual_check=['pk', ]
        )

        # Specified user.
        form_data['user'] = 'foobar2'
        self.expense4_return_data['user'] = 'foobar2'
        self.assertEndpoint(
            'expense_list',
            'post',
            form_data,
            self.expense4_return_data,
            status.HTTP_201_CREATED,
            url_kwargs=self.user1_url_kwargs,
            manual_check=['pk', ]
        )

    def test_update(self):
        """
        Update expense test.
        """
        form_data = {
            'amount': float(777)
        }
        self.expense_return_data['amount'] = '777.00'

        # User can only update its own records.
        self.assertEndpoint(
            'expense_detail',
            'put',
            form_data,
            self.expense_return_data,
            status.HTTP_200_OK,
            url_kwargs=self.user1_url_kwargs,
        )
        self.assertEndpoint(
            'expense_detail',
            'put',
            form_data,
            {'detail': 'You do not have permission to perform this action.'},
            status.HTTP_403_FORBIDDEN,
            url_kwargs=self.user2_url_kwargs
        )

        # Admin can create a record for any user.
        self.user.is_superuser = True
        self.user.save()

        form_data = {
            'amount': float(888)
        }
        self.expense2_return_data['amount'] = '888.00'
        self.assertEndpoint(
            'expense_detail',
            'put',
            form_data,
            self.expense2_return_data,
            status.HTTP_200_OK,
            url_kwargs=self.user2_url_kwargs,
        )

    def test_delete(self):
        """
        Delete expense test.
        """

        form_data = {}
        # User can only delete its own records.
        self.assertEndpoint(
            'expense_detail',
            'delete',
            form_data,
            None,
            status.HTTP_204_NO_CONTENT,
            url_kwargs=self.user1_url_kwargs,
        )
        self.assertEndpoint(
            'expense_detail',
            'delete',
            form_data,
            {'detail': 'You do not have permission to perform this action.'},
            status.HTTP_403_FORBIDDEN,
            url_kwargs=self.user2_url_kwargs
        )

        # Admin can delete a record for any user.
        self.user.is_superuser = True
        self.user.save()

        self.assertEndpoint(
            'expense_detail',
            'delete',
            form_data,
            None,
            status.HTTP_204_NO_CONTENT,
            url_kwargs=self.user2_url_kwargs,
        )

    def test_bulk_delete(self):
        """
        Expense bulk delete test.
        """
        pass
