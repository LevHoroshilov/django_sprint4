import datetime

from django.db import models

from users.forms import User


class PostQuerySet(models.QuerySet):
    def based_filter(self):
        return self.select_related('category', 'location', 'author').filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=datetime.datetime.now(),
        )

    def all_filter(self):
        return self.all()


class PostPublishManager(models.Manager):
    def get_queryset(self):
        return PostQuerySet(self.model).based_filter()


class PostManager(models.Manager):
    def get_queryset(self):
        return PostQuerySet(self.model).all_filter()


class CommonModel(models.Model):
    """Абстрактная модель. Добaвляет флаг is_published и created_at."""

    is_published = models.BooleanField(
        verbose_name='Опубликовано',
        default=True,
        help_text='Снимите галочку, чтобы скрыть публикацию.',
    )
    created_at = models.DateTimeField(
        verbose_name='Добавлено',
        auto_now_add=True,
    )

    class Meta:
        abstract = True


class Location(CommonModel):
    name = models.CharField(verbose_name='Название места', max_length=256)

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self):
        return self.name


class Category(CommonModel):
    title = models.CharField(verbose_name='Заголовок', max_length=256)
    description = models.TextField(verbose_name='Описание',)
    slug = models.SlugField(
        verbose_name='Идентификатор',
        unique=True,
        help_text='Идентификатор страницы для URL; '
        'разрешены символы латиницы, цифры, дефис и подчёркивание.',
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.title


'''class Image(models.Model):
    image = models.ImageField(blank=True, upload_to='posts_images')'''


class Comment(models.Model):
    text = models.TextField(verbose_name='Текст', blank=False, null=True)
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации комментария',
        auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор комментария',)

    post = models.ForeignKey(
        'Post',
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )


class Post(CommonModel):

    title = models.CharField(
        verbose_name='Заголовок',
        max_length=256,
    )
    text = models.TextField(verbose_name='Текст', default='')
    pub_date = models.DateTimeField(
        verbose_name='Дата и время публикации',
        default=datetime.datetime.now,
        help_text='Если установить дату и время '
        'в будущем — можно делать отложенные публикации.',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор публикации',
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Местоположение',
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Категория',
    )
    image = models.ImageField(
        verbose_name='Фото', blank=True, upload_to='posts_images'
        )
    only_author_objects = PostManager()
    objects = PostPublishManager()

    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'

    def __str__(self):
        return self.title
