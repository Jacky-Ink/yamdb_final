from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from users.models import User


class Category(models.Model):
    name = models.CharField(max_length=256, verbose_name='Имя категории')
    slug = models.SlugField(
        max_length=50,
        unique=True,
        verbose_name='Слаг категории',
    )

    class Meta:
        ordering = ('name',)

    def __str__(self) -> str:
        return self.slug


class Genre(models.Model):
    name = models.CharField(max_length=256, verbose_name='Имя жанра')
    slug = models.SlugField(
        max_length=50,
        unique=True,
        verbose_name='Слаг жанра'
    )

    class Meta:
        ordering = ('name',)

    def __str__(self) -> str:
        return self.slug


class Title(models.Model):
    name = models.CharField(max_length=256)
    year = models.IntegerField(
        verbose_name='Дата создания произведения',
    )
    description = models.TextField(
        verbose_name='Описание произведения',
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name='title',
        blank=True,
        null=True,
        verbose_name='Жанр произведения',
    )
    genre = models.ManyToManyField(
        Genre,
        related_name='title',
        blank=True,
        verbose_name='Категория произведения',
    )

    class Meta:
        ordering = ('year',)

    def __str__(self) -> str:
        return self.name


class Review(models.Model):
    text = models.TextField('Отзыв')
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Произведение',
        blank=True
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Автор произведения'
    )
    pub_date = models.DateTimeField('Дата создания', auto_now_add=True)
    score = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1, 'Минимальная оценка 1.'),
            MaxValueValidator(10, 'Максимальная оценка 10.')
        ],
        verbose_name='Рейтинг'
    )

    class Meta:
        ordering = ('pub_date',)
        verbose_name = 'review'
        verbose_name_plural = 'reviews'
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'title'],
                name='unique_author_review'
            )
        ]


class Comment(models.Model):
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Отзыв',
        null=True
    )
    text = models.TextField(
        'Текст комментария'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор комментария'
    )
    pub_date = models.DateTimeField('Дата создания', auto_now_add=True)

    class Meta:
        ordering = ('pub_date',)
        verbose_name = 'comment'
        verbose_name_plural = 'comments'
