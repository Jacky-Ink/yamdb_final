from django.db import IntegrityError
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
# если сюда вставить пустую строку, то проект тесты не проходит, ошибка I004
# понятно, что этот файл можно внечти в игнор, но невижу смысла
from reviews.models import Category, Comment, Genre, Review, Title
from users.models import User

from .utils import is_me


class AuthSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email')

    def validate_username(self, value):
        return is_me(value)


class AuthTokenSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=200)
    confirmation_code = serializers.CharField(max_length=200)


class UserSerializer(serializers.ModelSerializer):
    role = serializers.ChoiceField(choices=User.ROLES, default=User.USER)

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'role',
            'bio'
        )

    def validate_username(self, value):
        return is_me(value)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('name', 'slug')
        model = Category
        UniqueValidator = ('slug')


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('name', 'slug')
        model = Genre
        UniqueValidator = ('slug')


class TitleListSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    rating = serializers.FloatField(read_only=True)
    genre = GenreSerializer(
        read_only=True,
        many=True
    )

    class Meta:
        fields = (
            'id',
            'name',
            'year',
            'rating',
            'description',
            'genre',
            'category'
        )
        model = Title
        read_only_fields = ('id',)


class TitleCreateSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='slug'
    )
    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(),
        slug_field='slug',
        many=True
    )
    rating = serializers.FloatField(read_only=True)

    class Meta:
        fields = '__all__'
        model = Title


class ReviewSerializer(serializers.ModelSerializer):
    author = SlugRelatedField(
        slug_field='username',
        default=serializers.CurrentUserDefault(),
        read_only=True)

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date')
        read_only_fields = ('id', 'author', 'pub_date')

    def create(self, validated_data):
        try:
            return super().create(validated_data)
        except IntegrityError:
            raise serializers.ValidationError('Ваш отзыв уже есть')


class CommentSerializer(serializers.ModelSerializer):
    author = SlugRelatedField(
        slug_field='username',
        default=serializers.CurrentUserDefault(),
        read_only=True)

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')
