from django.conf import settings
from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.tokens import RefreshToken
from reviews.models import Category, Genre, Title
from users.models import User

from .filters import TitleFilter
from .mixins import CreateListDestroyViewSet
from .permissions import AuthorOrReadOnly, IsAdmin, IsAdminOrReadOnly
from .serializers import (AuthSerializer, AuthTokenSerializer,
                          CategorySerializer, CommentSerializer,
                          GenreSerializer, ReviewSerializer,
                          TitleCreateSerializer, TitleListSerializer,
                          UserSerializer)
from .utils import get_review, get_title


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'username'
    permission_classes = [IsAuthenticated & IsAdmin]
    filter_backends = (filters.SearchFilter,)
    search_fields = (
        'username',
        'first_name',
        'last_name',
        'role'
    )

    @action(
        detail=False,
        methods=['patch', 'get'],
        permission_classes=(IsAuthenticated,)
    )
    def me(self, request):
        user = get_object_or_404(User, username=request.user.username)
        if request.method == 'GET':
            serializer = UserSerializer(instance=user)
            return Response(serializer.data, status=status.HTTP_200_OK)

        serializer = UserSerializer(
            instance=user, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        if request.user.is_superuser or request.user.is_admin:
            serializer.save()
        else:
            serializer.save(role=request.user.role)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AuthView(APIView):

    def post(self, request):
        serializer = AuthSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        confirmation_code = urlsafe_base64_encode(
            force_bytes(serializer.validated_data.get('username'))
        )
        send_mail(
            'subj',
            confirmation_code,
            settings.ADMIN_EMAIL,
            [serializer.validated_data.get('email')],
            fail_silently=True,
        )
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class AuthTokenView(APIView):

    def post(self, request):
        serializer = AuthTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data.get('username')
        user = get_object_or_404(User, username=username)
        right_code = urlsafe_base64_encode(force_bytes(username))
        if serializer.validated_data.get('confirmation_code') != right_code:
            return Response(
                serializer.validated_data, status=status.HTTP_400_BAD_REQUEST
            )

        refresh = RefreshToken.for_user(user)
        return Response(
            {'access': str(refresh.access_token)}, status=status.HTTP_200_OK
        )


class CategoryViewSet(CreateListDestroyViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(CreateListDestroyViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.prefetch_related(
        'category', 'genre').annotate(
            rating=Avg('reviews__score'))
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter
    permission_classes = [IsAdminOrReadOnly, ]

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return TitleListSerializer
        return TitleCreateSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [AuthorOrReadOnly, ]

    def get_queryset(self):
        return get_title(self).reviews.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, title=get_title(self))


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [AuthorOrReadOnly, ]

    def get_queryset(self):
        return get_review(self).comments.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, review=get_review(self))
