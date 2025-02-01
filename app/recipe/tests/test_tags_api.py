from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import User, Tag
from recipe.serializers import TagSerializer

TAGS_URL = reverse('recipe:tag-list')


def detail_url(tag_id):
    return reverse('recipe:tag-detail', args=[tag_id])


def create_user(email='test@example.com', password='password123'):
    return User.objects.create_user(email, password)


class PublicTagsApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(TAGS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        Tag.objects.create(user=self.user, name='Vegan')
        Tag.objects.create(user=self.user, name='Dessert')

        res = self.client.get(TAGS_URL)

        tags = Tag.objects.all().order_by('name')
        serializer = TagSerializer(tags, many=True)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_return_HTTP_OK(self):
        Tag.objects.create(user=self.user, name='Vegan')

        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_tags_limited_to_user(self):
        other_user = create_user(email='other@example.com')
        Tag.objects.create(user=other_user, name='Fruity')
        tag = Tag.objects.create(user=self.user, name='Comford Food')

        res = self.client.get(TAGS_URL)

        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)

    def test_update_tag_returns_HTTP_OK(self):
        tag = Tag.objects.create(user=self.user, name='After Dinner')

        payload = {
            'name': 'Dessert',
        }
        url = detail_url(tag.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_update_tag(self):
        tag = Tag.objects.create(user=self.user, name='After Dinner')

        payload = {
            'name': 'Dessert',
        }
        url = detail_url(tag.id)
        self.client.patch(url, payload)

        tag.refresh_from_db()
        self.assertEqual(tag.name, payload['name'])

    def test_delete_tag_returns_HTTP_NO_CONTENT(self):
        tag = Tag.objects.create(user=self.user, name='After Dinner')

        url = detail_url(tag.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_tag(self):
        tag = Tag.objects.create(user=self.user, name='After Dinner')

        url = detail_url(tag.id)
        self.client.delete(url)

        self.assertFalse(Tag.objects.filter(id=tag.id).exists())
