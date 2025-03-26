import datetime

from django.shortcuts import render, get_object_or_404,redirect
from django.views.generic import ListView, CreateView, DeleteView, UpdateView, DetailView
from django.urls import reverse_lazy,reverse
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required

from blogicum.blog.models import Post, Category, Comment
from blog.forms import PostForm, CommentForm
from blog.utils import comment_count
from users.forms import User, CustomUserCreationForm


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
        form = CommentForm()
        context['form'] = form
        comments = Comment.objects.filter(post__id=self.kwargs['pk'])
        #context['post.comment_count'] = comment_count(comments)
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

    def author(self):
        return get_object_or_404(User, username=self.kwargs['username'])

    def get_queryset(self):
        username = self.kwargs['username']
        return Post.objects.filter(author__username=username).select_related('author')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = User.objects.filter(username=self.kwargs['username'])
        return context


class OnlyAuthorMixin(UserPassesTestMixin):

    def test_func(self):
        object = self.get_object()
        return object.author == self.request.user

class UserUpdateView(OnlyAuthorMixin, UpdateView):
    model = User
    form_class = CustomUserCreationForm
    username = 'username'
    template_name = 'blog/user.html'

    def form_valid(self, form):
        #username = get_object_or_404(User, username=self.kwargs['username'])
        form.save()
        return super().form_valid(form)

    def get_object(self, queryset=None):
        return User.objects.get(name=self.kwargs['username'])
    
    def get_success_url(self):
        return redirect('blog:profile', kwargs={'username': self.request.user})



@login_required
def edit_profile(request, username):
    '''if request.user.username != username:
        return reverse('blog:profile')'''
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('blog:profile', username=username)
    else:
        form = CustomUserCreationForm(instance=request.user)
    return render(request, 'blog/edit_profile.html', {'form': form})


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


class PostDeleteView(OnlyAuthorMixin, DeleteView):
    model = Post
    #form_class = PostForm
    template_name = 'blog/create.html'
    success_url = reverse_lazy('blog:index')
    context_object_name = 'form'

    def get_object(self, queryset=None):
        return Post.objects.get(pk=self.kwargs['pk'])

    '''def get_object(self, queryset=None):
        return Post.objects.filter(pk=self.kwargs['pk'])'''
    
    '''def get_queryset(self):
        return Post.objects.filter(pk=self.kwargs['pk'])
    

    def get_success_url(self):
        return reverse('blog:index')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PostForm(instance=self.request.user)
        #context['user'] = self.request.user
        return context
'''

class PostUpdateView(OnlyAuthorMixin, UpdateView):
    form_class = PostForm
    model = Post
    template_name = 'blog/create.html'
    success_url = reverse_lazy('blog:index')

    def get_object(self, queryset=None):
        return Post.objects.get(pk=self.kwargs.get('pk'))





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


class CommentUpdateView(OnlyAuthorMixin,UpdateView):#commentauthormixin
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'
    success_url = 'post_detail'

    def get_object(self, queryset=None):
        comment_id = self.kwargs.get('comment_id')
        return Comment.objects.get(pk=comment_id)
    
    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'pk': self.object.post.pk})
    