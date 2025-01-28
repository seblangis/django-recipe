from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe, Tag
from recipe.serializers import (
    RecipeSerializer,
    RecipeDetailSerializer,
)

RECIPES_URL = reverse('recipe:recipe-list')


def detail_url(recipe_id):
    return reverse('recipe:recipe-detail', args=[recipe_id])


def create_recipe(user, **params):
    defaults = {
        'title': 'Default recipe',
        'time_minutes': 10,
        'price': Decimal('15.40'),
        'description': 'Default recipe description',
        'link': 'https://www.example.com/recipe',
    }
    defaults.update(params)

    return Recipe.objects.create(user=user, **defaults)


class PublicRecipeApiTests(TestCase):
    """Test unauthenticated recipe API access"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test that authentication is required"""
        res = self.client.get(RECIPES_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email='user@example.com',
            password='password123',
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_recipes_return_HTTP_OK(self):
        res = self.client.get(RECIPES_URL)

        self.assertEquals(res.status_code, status.HTTP_200_OK)

    def test_retrieve_empty_recipe_list(self):
        res = self.client.get(RECIPES_URL)

        self.assertEqual(0, len(res.data))

    def test_retrieve_recipes(self):
        create_recipe(user=self.user)
        create_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.data, serializer.data)

    def test_does_not_retrieve_recipes_from_other_user(self):
        other_user = get_user_model().objects.create_user(
            'otheruser@example.com',
            'password123',
        )
        create_recipe(user=other_user)
        create_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.data, serializer.data)

    def test_get_recipe_detail(self):
        recipe = create_recipe(user=self.user)

        url = detail_url(recipe.id)
        res = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(res.data, serializer.data)

    def test_can_not_get_recipe_from_other_user(self):
        other_user = get_user_model().objects.create_user(
            'otheruser@example.com',
            'password123',
        )
        recipe = create_recipe(user=other_user)

        url = detail_url(recipe.id)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_recipe(self):
        payload = {
            'title': 'Test recipe',
            'time_minutes': 30,
            'price': Decimal('15.40'),
            'description': 'Test recipe description',
            'link': 'https://www.example.com/very-good-recipe',
        }
        self.client.post(RECIPES_URL, payload)

        recipe = Recipe.objects.first()

        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.time_minutes, payload['time_minutes'])
        self.assertEqual(recipe.price, payload['price'])
        self.assertEqual(recipe.description, payload['description'])
        self.assertEqual(recipe.link, payload['link'])
        self.assertEqual(recipe.user, self.user)

    def test_create_recipe_return_HTTP_CREATED(self):
        payload = {
            'title': 'Test recipe',
            'time_minutes': 30,
            'price': Decimal('15.40'),
        }
        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_partial_update_recipe_returns_HTTP_OK(self):
        recipe = create_recipe(
            user=self.user,
            title='Original recipe',
            link='https://www.example.com/recipe',
        )

        payload = {'title': 'Updated recipe title'}
        res = self.client.patch(detail_url(recipe.id), payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_partial_update_recipe(self):
        original_link = 'https://www.example.com/recipe'
        recipe = create_recipe(
            user=self.user,
            title='Original recipe',
            link=original_link,
        )

        payload = {'title': 'Updated recipe title'}
        self.client.patch(detail_url(recipe.id), payload)

        recipe = Recipe.objects.first()
        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.link, original_link)
        self.assertEqual(recipe.user, self.user)

    def test_complete_update_recipe_returns_HTTP_OK(self):
        recipe = create_recipe(
            user=self.user,
            title='Original recipe',
        )

        payload = {
            'title': 'Updated recipe title',
            'time_minutes': 10,
            'price': Decimal('15.40'),
            'description': 'Default recipe description',
            'link': 'https://www.example.com/recipe',
        }
        res = self.client.put(detail_url(recipe.id), payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_complete_update_recipe(self):
        recipe = create_recipe(
            user=self.user,
            title='Original recipe',
        )

        payload = {
            'title': 'Updated recipe title',
            'time_minutes': 10,
            'price': Decimal('15.40'),
            'description': 'Default recipe description',
            'link': 'https://www.example.com/recipe',
        }
        self.client.put(detail_url(recipe.id), payload)

        recipe = Recipe.objects.first()
        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.user, self.user)

    def test_update_user_returns_error(self):
        new_user = get_user_model().objects.create_user(
            'new@example.com',
            'password123',
        )

        recipe = create_recipe(
            user=self.user,
        )

        payload = {'user': new_user.id}
        self.client.patch(detail_url(recipe.id), payload)

        retrieved_recipe = Recipe.objects.first()
        self.assertEqual(retrieved_recipe.user, self.user)

    def test_delete_recipe(self):
        recipe = create_recipe(
            user=self.user,
        )

        url = detail_url(recipe.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Recipe.objects.filter(id=recipe.id).exists())

    def test_delete_other_user_recipe_returns_error(self):
        other_user = get_user_model().objects.create_user(
            'other@example.com',
            'password123',
        )

        recipe = create_recipe(
            user=other_user,
        )

        url = detail_url(recipe.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND, )
        self.assertTrue(Recipe.objects.filter(id=recipe.id).exists())

    def test_create_recipe_with_new_tags(self):
        payload = {
            'title': "Pâté chinois",
            "time_minutes": 30,
            "price": Decimal('15.40'),
            'tags': [
                {'name': 'Québecois'},
                {'name': 'Santé'},
            ]
        }

        self.client.post(RECIPES_URL, payload, format='json')

        tags = Tag.objects.all().order_by('name')
        self.assertEquals(tags[0].name, 'Québecois')
        self.assertEquals(tags[0].user, self.user)
        self.assertEquals(tags[1].name, 'Santé')

    def test_create_recipe_with_existing_tags(self):
        Tag.objects.create(user=self.user, name='Indian')

        payload = {
            'title': "Pongal",
            "time_minutes": 30,
            "price": Decimal('15.40'),
            'tags': [
                {'name': 'Indian'},
                {'name': 'Santé'},
            ]
        }

        self.client.post(RECIPES_URL, payload, format='json')

        self.assertEqual(len(Tag.objects.all()), 2)

    def test_create_tag_on_update(self):
        recipe = create_recipe(user=self.user)

        payload = {'tags': [{'name': 'Lunch'}]}
        url = detail_url(recipe.id)
        self.client.patch(url, payload, format='json')

        self.assertEqual(len(recipe.tags.all()), 1)
        self.assertEqual(recipe.tags.first().name, 'Lunch')

    def test_assign_tags_to_recipe(self):
        tag_breakfast = Tag.objects.create(user=self.user, name='Breakfast')
        recipe = create_recipe(user=self.user)
        recipe.tags.add(tag_breakfast)

        Tag.objects.create(user=self.user, name='Lunch')
        payload = {'tags': [{'name': 'Lunch'}]}
        url = detail_url(recipe.id)
        self.client.patch(url, payload, format='json')

        self.assertEqual(len(recipe.tags.all()), 1)
        self.assertEqual(recipe.tags.first().name, 'Lunch')

    def test_clear_recipe_tags(self):
        tag = Tag.objects.create(user=self.user, name='Dessert')
        recipe = create_recipe(user=self.user)
        recipe.tags.add(tag)

        payload = {'tags': []}
        url = detail_url(recipe.id)
        self.client.patch(url, payload, format='json')

        self.assertEqual(len(recipe.tags.all()), 0)
