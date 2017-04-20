from datetime import timedelta
from django.core.urlresolvers import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient
from expense_trackapp.models import Expense
from .base import BaseTestCase


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
            'username': 'foobar3',
            'password': 'foobar3',
            'confirm_password': 'foobar1',
            'email': 'foo@bar3.com'
        }
        return_data = {
            'non_field_errors': ['Passwords must match.']
        }
        self.assertEndpoint(
            'account_register', 'post', form_data, return_data, status.HTTP_400_BAD_REQUEST)


class ExpensesTest(BaseTestCase):
    def setUp(self):
        super(ExpensesTest, self).setUp()

        # Set authorization.
        self.token = Token.objects.create(user=self.user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        # Set url kwargs.
        self.user1_url_kwargs = {
            'username': self.user.username,
            'pk': self.expense.pk
        }
        self.user2_url_kwargs = {
            'username': self.user2.username,
            'pk': self.expense2.pk
        }

        # Create new expense for self.user.
        self.expense3 = Expense.objects.create(
            amount=float(333),
            user=self.user,
            date=self.now.date() - timedelta(days=1),
            time=self.now.time()
        )

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

        self.expense3_return_data = {
            'amount': '333.00',
            'comment': '',
            'date': str(self.now.date() - timedelta(days=1)),
            'description': '',
            'pk': self.expense3.pk,
            'time': str(self.now.time()),
            'user': 'foobar'
        }

    def test_list(self):
        """
        List of expenses test.
        """

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

    def test_list_filter_date(self):
        """
        Filtered expense list test.
        """

        form_data = {}
        return_data = [self.expense_return_data, self.expense3_return_data]

        # Set url kwargs.
        self.user1_url_kwargs.pop('pk')
        self.user2_url_kwargs.pop('pk')

        # Set query parameters.
        query_params = {
            'date_0': str(self.now.date() - timedelta(days=2)),
            'date_1': str(self.now.date())
        }

        # Filter all todays and yesterdays dates.
        self.assertEndpoint(
            'expense_list',
            'get',
            form_data,
            return_data,
            status.HTTP_200_OK,
            url_kwargs=self.user1_url_kwargs,
            query_params=query_params
        )

        # Filter only yesterdays dates.
        query_params = {
            'date_0': str(self.now.date() - timedelta(days=2)),
            'date_1': str(self.now.date() - timedelta(days=1))
        }
        return_data = [self.expense3_return_data, ]

        self.assertEndpoint(
            'expense_list',
            'get',
            form_data,
            return_data,
            status.HTTP_200_OK,
            url_kwargs=self.user1_url_kwargs,
            query_params=query_params
        )

    def test_list_filter_time(self):
        """
        Filtered expense list test.
        """

        form_data = {}
        return_data = [self.expense_return_data, self.expense3_return_data]
        new_time = (self.now - timedelta(hours=2)).time()
        self.expense3.time = new_time
        self.expense3.save()
        self.expense3_return_data['time'] = str(new_time)

        # Set url kwargs.
        self.user1_url_kwargs.pop('pk')
        self.user2_url_kwargs.pop('pk')

        # Set query parameters.
        query_params = {
            'time_0': str((self.now - timedelta(hours=3)).time()),
            'time_1': str(self.now.time())
        }

        # Filter all times.
        self.assertEndpoint(
            'expense_list',
            'get',
            form_data,
            return_data,
            status.HTTP_200_OK,
            url_kwargs=self.user1_url_kwargs,
            query_params=query_params
        )

        # Filter only time from an hour ago.
        query_params = {
            'time_0': str((self.now - timedelta(hours=1)).time()),
            'time_1': str(self.now.time())
        }
        return_data = [self.expense_return_data, ]

        self.assertEndpoint(
            'expense_list',
            'get',
            form_data,
            return_data,
            status.HTTP_200_OK,
            url_kwargs=self.user1_url_kwargs,
            query_params=query_params
        )

    def test_list_filter_amount(self):
        """
        Filtered expense list test.
        """

        form_data = {}
        return_data = [self.expense_return_data, self.expense3_return_data]

        # Set url kwargs.
        self.user1_url_kwargs.pop('pk')
        self.user2_url_kwargs.pop('pk')

        # Set query parameters.
        query_params = {
            'amount_0': '300.00',
            'amount_1': '700.00'
        }

        # Filter all amounts.
        self.assertEndpoint(
            'expense_list',
            'get',
            form_data,
            return_data,
            status.HTTP_200_OK,
            url_kwargs=self.user1_url_kwargs,
            query_params=query_params
        )

        # Filter only amounts below 600.
        query_params = {
            'amount_0': '300.00',
            'amount_1': '600.00'
        }
        return_data = [self.expense3_return_data, ]

        self.assertEndpoint(
            'expense_list',
            'get',
            form_data,
            return_data,
            status.HTTP_200_OK,
            url_kwargs=self.user1_url_kwargs,
            query_params=query_params
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

        # Required fields.
        form_data = {}
        self.assertEndpoint(
            'expense_list',
            'post',
            form_data,
            {'amount': ['This field is required.']},
            status.HTTP_400_BAD_REQUEST,
            url_kwargs=self.user1_url_kwargs,
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

        # Required fields.
        form_data = {}
        self.assertEndpoint(
            'expense_detail',
            'put',
            form_data,
            {'amount': ['This field is required.']},
            status.HTTP_400_BAD_REQUEST,
            url_kwargs=self.user1_url_kwargs,
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
