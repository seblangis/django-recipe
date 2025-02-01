from rest_framework import serializers

from core.models import Recipe, Tag, Ingredient


class TagSerializer(serializers.ModelSerializer):
    """Serializer for tag objects"""

    class Meta:
        model = Tag
        fields = ['id', 'name']
        read_only_fields = ['id']


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ['id', 'name']
        read_only_fields = ['id']


class RecipeImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ['id', 'image']
        read_only_fields = ['id']
        extra_kwargs = {'image': {'required': True}}


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for recipe objects"""

    class Meta:
        model = Recipe
        fields = ['id', 'title', 'time_minutes', 'price', 'link', 'tags']
        read_only_fields = ['id']

    tags = TagSerializer(many=True, required=False)

    def create(self, validated_data):
        tags = validated_data.pop('tags', [])
        recipe = Recipe.objects.create(**validated_data)
        self._get_or_create_tags(tags, recipe)

        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags', None)

        if tags is not None:
            instance.tags.clear()
            self._get_or_create_tags(tags, instance)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance

    def _get_or_create_tags(self, tags, recipe):
        authenticated_user = self.context['request'].user
        for tag in tags:
            tag_object, _created = Tag.objects.get_or_create(
                user=authenticated_user,
                **tag
            )
            recipe.tags.add(tag_object)


class RecipeDetailSerializer(RecipeSerializer):
    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ['description', 'ingredients']

    ingredients = IngredientSerializer(many=True, required=False)

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients', [])
        recipe = super().create(validated_data)

        self._get_or_create_ingredients(ingredients, recipe)

        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients', None)

        if ingredients is not None:
            instance.ingredients.clear()
            self._get_or_create_ingredients(ingredients, instance)

        return super().update(instance, validated_data)

    def _get_or_create_ingredients(self, ingredients, recipe):
        authenticated_user = self.context['request'].user
        for ingredient in ingredients:
            ingredient_object, _created = Ingredient.objects.get_or_create(
                user=authenticated_user,
                **ingredient
            )
            recipe.ingredients.add(ingredient_object)
