import datetime

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404,redirect
from django.core.paginator import Paginator
from django.views.generic import ListView, CreateView, DeleteView, UpdateView, DetailView
from django.urls import reverse_lazy
from django.core.exceptions import PermissionDenied        
from django.contrib.auth.mixins import LoginRequiredMixin,UserPassesTestMixin

from blog.models import Post, Category,Comment
from blog.forms import PostForm,CommentForm
from users.forms import User

def post_detail(request, id):
    
    post = get_object_or_404(
        Post,
        pub_date__lte=datetime.datetime.now(),
        is_published=True,
        category__is_published=True,
        id=id)
    context = {'post': post}
    template = 'blog/detail.html'
    return render(request, template, context)


def category_posts(request, category_slug):
    template = 'blog/category.html'
    post_list = Post.objects.filter(
        category__slug=category_slug,
    ).order_by('id')
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True,
    )
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'category': category,
               'page_obj': page_obj}
    return render(request, template, context)

@login_required
def user_page(request, username):
    template = 'blog/profile.html'
    profile =Post.objects.filter(author__username=username)
    paginator = Paginator(profile, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'page_obj':page_obj,
               'profile':profile}
    return render(request, template, context)


class OnlyAuthorMixin(UserPassesTestMixin):

    def test_func(self):
        object = self.get_object()
        return object.author == self.request.user



class PostCreateView(OnlyAuthorMixin, LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)
    
    template_name = 'blog/create.html'
    success_url = reverse_lazy('blog:index')

@login_required
def create(request):
    template = 'blog/create.html'
    if request.method == 'POST':
        form = PostForm(request.POST or None)
        if form.is_valid():
            form.save(commit=False)
            form.instance.author = request.user
            form.save()
            return redirect('blog:index')
    else:
        form = PostForm()
    context = {'form':form}
    return render(request, template, context)



def post_edit(request, id):
    template = 'blog/create.html'
    if request.method == 'POST':
        instance = get_object_or_404(Post, pk=id)
        if instance.author != request.user:
            return redirect('blog:post_detail')
        form = PostForm(request.POST or None)
        if form.is_valid():
            form.save(commit=False)
            form.instance.author = request.user
            form.save()
            return redirect('blog:post_detail')
    else:
        return redirect('blog:post_detail')
    

def func(request, id):
    if id is not None:
        instance = get_object_or_404(Post, pk=id)
    else:
        instance = None
    form = PostForm(request.POST or None, files=request.FILES or None, instance=instance)
    context = {'form': form}
    if form.is_valid():
        form.save()
    else:
        form = PostForm()    
    return render(request, 'blog/create.html', context)


def add_comment(request,id):
    template = 'blog/comment.html'
    instance = get_object_or_404(Comment, id=id)
    form = CommentForm(request.POST or None, files=request.FILES or None,instance=instance)
    context = {'form': form}
    if form.is_valid():
        form.save()
    else:
        form = CommentForm() 
    return render(request, template, context)

def edit_comment(request,id):
    template = 'blog/comment.html'
    if id is not None:
        instance = get_object_or_404(Comment, id=id)
    else:
        instance = None
    form = CommentForm(request.POST or None, files=request.FILES or None, instance=instance)
    context = {'form': form}
    if form.is_valid():
        form.save()
    else:
        form = CommentForm()
    return render(request, template, context)


    

class PostListView(ListView):
    template_name = 'blog/index.html'
    model = Post
    queryset = Post.objects.all()
    ordering = 'id'
    paginate_by = 10

class PostDetailView(DetailView):
    model = Post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context['form'] = CongratulationForm()
        context['congratulations'] = (
            # Дополнительно подгружаем авторов комментариев,
            # чтобы избежать множества запросов к БД.
            self.object.congratulations.select_related('author')
        )
        return context

class PostDeleteView(LoginRequiredMixin, OnlyAuthorMixin, DeleteView):
    model = Comment
    template_name = 'blog/create.html'
    success_url = reverse_lazy('blog:index')

class PostUpdateView(LoginRequiredMixin, OnlyAuthorMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'
    fields = '__all__'
    
















class CommentListView(ListView):
    template_name = 'blog/comment.html'
    model = Comment
    queryset = Comment.objects.filter()
    ordering = 'id'
    paginate_by = 10


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'
    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

class CommentDeleteView(LoginRequiredMixin, OnlyAuthorMixin, DeleteView):
    model = Comment
    template_name = 'blog/comment.html'
    success_url = reverse_lazy('blog:index')

class CommentUpdateView(LoginRequiredMixin, OnlyAuthorMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'
    fields = '__all__'
    
    