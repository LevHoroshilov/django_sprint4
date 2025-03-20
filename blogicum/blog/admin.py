from django.contrib import admin

from .models import Location, Category, Post

admin.site.register(Location)


class PostAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'text',
        'pub_date',
        'is_published',
        'created_at',
        'category',
        'location',
        'author',
    )
    empty_value_display = 'Не задано'


admin.site.register(Post, PostAdmin)


class PostInline(admin.TabularInline):
    model = Post
    extra = 1


class CategoryAdmin(admin.ModelAdmin):
    inlines = (PostInline,)
    list_display = ('title', 'description')


admin.site.register(Category, CategoryAdmin)
