from django.shortcuts import get_object_or_404
from rest_framework import serializers
from reviews.models import Review, Title


def is_me(value):
    if value == 'me':
        raise serializers.ValidationError(
            'Нельзя использовать зарезервированное имя "me"'
        )
    return value


def get_title(self):
    return get_object_or_404(Title, pk=self.kwargs.get('title_id'))


def get_review(self):
    return get_object_or_404(
        Review,
        pk=self.kwargs.get("review_id"),
        title=get_title(self)
    )
