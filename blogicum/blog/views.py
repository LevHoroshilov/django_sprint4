import datetime

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404,redirect
from django.core.paginator import Paginator
from django.views.generic import ListView, CreateView#, DeleteView, UpdateView, DetailView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin,UserPassesTestMixin

from blog.models import Post, Category
from blog.forms import PostForm
from users.forms import User

def index(request):
    template = 'blog/index.html'
    post_list = Post.objects.order_by('pub_date',)
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'page_obj': page_obj}
    return render(request, template, context)


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
    profile =User.objects.filter(username=username)
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