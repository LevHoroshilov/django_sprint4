from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator

from blog.models import Post

def user_page(request, username):
    template = 'blog/user.html'
    profile = get_object_or_404(
        Post,
        username=username
    )
    paginator = Paginator(profile, 10)
    page_number = request.POST.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'page_obj':page_obj}
    return render(request, template, context)