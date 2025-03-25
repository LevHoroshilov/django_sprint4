import datetime

from django.shortcuts import render, get_object_or_404,redirect
from django.views.generic import ListView, CreateView, DeleteView, UpdateView, DetailView
from django.urls import reverse_lazy,reverse
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from blog.models import Post, Category, Comment
from blog.forms import PostForm, CommentForm


class PostDetailView(DetailView):
    template_name = 'blog/detail.html'

    def get_queryset(self):
        return Post.objects.filter(
            id=self.kwargs['pk'],
            pub_date__lte=datetime.datetime.now(),
            is_published=True,
            category__is_published=True,
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = Comment.objects.filter(post__id=self.kwargs['pk'])
        return context


class CategoryPostsListView(ListView):
    template_name = 'blog/category.html'
    model = Category
    ordering = 'pub_date'
    paginate_by = 10
    
    def get_queryset(self):
        category_slug = self.kwargs['category_slug']
        return Post.objects.filter(
            category__slug=category_slug,
            ).select_related('category')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = get_object_or_404(
            Category,
            slug=self.kwargs['category_slug'],
            is_published=True
        )
        return context


class UserPageListView(LoginRequiredMixin, ListView):
    template_name = 'blog/profile.html'
    paginate_by = 10
    model = Post

    def get_queryset(self):
        username = self.kwargs['username']
        return get_object_or_404(Post.objects.filter(author__username=username).select_related('author'))
    
    '''def get_queryset(self):
        username = self.kwargs['username']
        return Post.objects.filter(author__username=username).select_related('author')
'''

class OnlyAuthorMixin(UserPassesTestMixin):

    def test_func(self):
        object = self.get_object()
        return object.author == self.request.user


class PostMixin:
    model = Post
    template_name = 'blog/create.html'
    success_url = reverse_lazy('blog:index')


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)
    
    template_name = 'blog/create.html'
    success_url = reverse_lazy('blog:index')


class PostListView(ListView):
    template_name = 'blog/index.html'
    model = Post
    queryset = Post.objects.all()
    ordering = 'id'
    paginate_by = 10


class PostDeleteView(LoginRequiredMixin, OnlyAuthorMixin, DeleteView, PostMixin):
    pass


class PostUpdateView(LoginRequiredMixin, OnlyAuthorMixin, UpdateView, PostMixin):
    form_class = PostForm





class CommentAuthorMixin(UserPassesTestMixin):

    def test_func(self):
        object = self.get_object()
        return object.post.author == self.request.user

'''
class CommentMixin:
    form_class = CommentForm

    def form_valid(self, form):
        post = get_object_or_404(Post, pk=self.kwargs['pk'])
        comment = form.save(commit=False)
        comment.post = post
        form.instance.author = self.request.user
        comment.save()
        return super().form_valid(form)
'''

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



class CommentDeleteView(LoginRequiredMixin, OnlyAuthorMixin, DeleteView, CommentAuthorMixin):
    model = Comment
    template_name = 'blog/comment.html'
    success_url = 'blog:post_detail'

    def get_object(self, queryset=None):
        comment_id = self.kwargs.get('comment_id')
        return Comment.objects.get(pk=comment_id)
    
    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'pk': self.object.post.pk})


class CommentUpdateView(LoginRequiredMixin, OnlyAuthorMixin, UpdateView, CommentAuthorMixin):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'
    success_url = 'post_detail'

    def form_valid(self, form):
        post = get_object_or_404(Post, pk=self.kwargs['pk'])
        comment = form.save(commit=False)
        comment.post = post
        form.instance.author = self.request.user
        comment.save()
        return super().form_valid(form)

    def get_object(self, queryset=None):
        comment_id = self.kwargs.get('comment_id')
        return Comment.objects.get(pk=comment_id)
    
    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'pk': self.object.post.pk})
    