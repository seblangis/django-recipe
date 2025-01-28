"""
Tests for models.
"""
from decimal import Decimal

from django.test import TestCase
from core.models import User, Recipe, Tag


def create_user(email='test@example', password='password123'):
    return User.objects.create_user(email, password)


class UserModelTests(TestCase):
    def test_create_user_with_email_successful(self):
        email = "test@example.com"
        password = "test-password-123"
        user = User.objects.create_user(
            email=email,
            password=password,
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        sample_emails = [
            ("test1@EXAMPLE.COM", "test1@example.com"),
            ("TEST2@EXAMpLE.COM", "TEST2@example.com"),
            ("test3@example.COM", "test3@example.com"),
            ("test4@example.com", "test4@example.com"),
        ]

        for sample_email, expected_email in sample_emails:
            with self.subTest(
                    sample_email=sample_email,
                    expected_email=expected_email
            ):
                user = User.objects.create_user(
                    email=sample_email,
                    password="password123"
                )
                self.assertEqual(user.email, expected_email)

    def test_new_user_without_email_raises_error(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(email="", password="password123")

    def test_create_superuser(self):
        user = User.objects.create_superuser(
            email="test@example.com",
            password="password123",
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)


class RecipeModelTests(TestCase):
    def test_create_recipe(self):
        user = User.objects.create_user(
            'test@exampe.com',
            'testpass123',
        )

        recipe = Recipe.objects.create(
            user=user,
            title='Sample recipe',
            time_minutes=5,
            price=Decimal('5.40'),
            description='Sample recipe description',
        )

        self.assertEqual(str(recipe), 'Sample recipe')


class TagModelTest(TestCase):
    def test_create_tag(self):
        user = create_user()
        tag = Tag.objects.create(user=user, name='Tag1')

        self.assertEqual(str(tag), 'Tag1')
