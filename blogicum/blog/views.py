from django.shortcuts import get_object_or_404
from django.views.generic import (
    ListView, CreateView, DeleteView, UpdateView, DetailView
)
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Count
from django.shortcuts import redirect

from blog.models import Post, Category, Comment
from blog.forms import PostForm, CommentForm
from users.forms import User, UserForm


class PostDetailView(DetailView):
    template_name = 'blog/detail.html'

    def get_queryset(self):
        return Post.only_author_objects.filter(
            id=self.kwargs['pk'],
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = CommentForm()
        context['form'] = form
        comments = Comment.objects.filter(post__id=self.kwargs['pk'])
        context['comments'] = comments
        return context


class CategoryPostsListView(ListView):
    template_name = 'blog/category.html'
    model = Category
    ordering = 'pub_date'
    paginate_by = 10

    def get_queryset(self):
        category_slug = self.kwargs['category_slug']
        return Post.objects.filter(
            category__slug=category_slug).select_related(
            'category').annotate(
            comment_count=Count('comment')
        ).order_by('-pub_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = get_object_or_404(
            Category,
            slug=self.kwargs['category_slug'],
            is_published=True
        )
        return context


class UserPageListView(ListView):
    template_name = 'blog/profile.html'
    paginate_by = 10
    model = Post

    def get_queryset(self):
        username = self.kwargs['username']
        if self.request.user.username == self.kwargs['username']:
            posts = Post.only_author_objects
        else:
            posts = Post.objects

        return posts.filter(author__username=username
            ).select_related('author').annotate(
            comment_count=Count('comment')
        ).order_by('-pub_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = get_object_or_404(
            User, username=self.kwargs['username'])
        return context


class OnlyAuthorMixin(UserPassesTestMixin):

    def test_func(self):
        object = self.get_object()
        return object.author == self.request.user


class OnlyUserMixin(UserPassesTestMixin):

    def test_func(self):
        object = self.get_object()
        return object == self.request.user


class UserUpdateView(OnlyUserMixin, UpdateView):
    model = User
    form_class = UserForm
    template_name = 'blog/user.html'

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

    def get_object(self, queryset=None):
        username = self.request.user.username
        return get_object_or_404(User, username=username)

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )


class PostListView(ListView):
    template_name = 'blog/index.html'
    model = Post
    paginate_by = 10

    def get_queryset(self):
        return Post.objects.annotate(
            comment_count=Count('comment')).order_by('-pub_date')


class PostDeleteView(OnlyAuthorMixin, DeleteView):
    model = Post
    template_name = 'blog/create.html'
    success_url = reverse_lazy('blog:index')

    def get_object(self, queryset=None):
        return get_object_or_404(Post, pk=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        post = self.get_object()

        context['form'] = PostForm(instance=post)
        return context


class PostUpdateView(OnlyAuthorMixin, UpdateView):
    form_class = PostForm
    model = Post
    template_name = 'blog/create.html'

    def get_object(self, queryset=None):
        return get_object_or_404(Post, pk=self.kwargs['pk'])

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'pk': self.kwargs['pk']})

    def handle_no_permission(self):
        return redirect(reverse(
            'blog:post_detail', kwargs={'pk': self.kwargs['pk']}))


class CommentAuthorMixin(UserPassesTestMixin):

    def test_func(self):
        object = self.get_object()
        return object.post.author == self.request.user


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'
    success_url = 'blog:post_detail'

    def form_valid(self, form):
        post = get_object_or_404(Post, pk=self.kwargs['pk'])
        comment = form.save(commit=False)
        comment.post = post
        form.instance.author = self.request.user
        comment.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'pk': self.object.post.pk})


class CommentDeleteView(OnlyAuthorMixin, DeleteView):
    model = Comment
    template_name = 'blog/comment.html'
    success_url = 'blog:post_detail'

    def get_object(self, queryset=None):
        comment_id = self.kwargs.get('comment_id')
        return get_object_or_404(Comment, pk=comment_id)

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'pk': self.object.post.pk})


class CommentUpdateView(OnlyAuthorMixin, UpdateView):  # commentauthormixin
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'
    success_url = 'post_detail'

    def get_object(self, queryset=None):
        comment_id = self.kwargs.get('comment_id')
        return get_object_or_404(Comment, pk=comment_id)

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'pk': self.object.post.pk})
