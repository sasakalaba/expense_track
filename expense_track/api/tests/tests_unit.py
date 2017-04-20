from .base import BaseTestCase
from ..permissions import IsOwnerOrReadOnly
from ..views import ExpenseViewSet
from django.contrib.auth.models import User
from mock import MagicMock, call


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
            username='foobar3', email='foo@bar3.com', password='mypassword'
        )
        self.assertFalse(self.is_owner_or_read_only.has_object_permission(
            self.request, self.view, obj))


class ExpenseViewSetTest(BaseTestCase):
    def setUp(self):
        super(ExpenseViewSetTest, self).setUp()
        self.user.is_superuser = True
        self.user.save()
        self.request = MagicMock(user=self.user)
        self.expense_view = ExpenseViewSet(request=self.request)
        self.serializer = MagicMock(initial_data={'user': self.user2})

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
