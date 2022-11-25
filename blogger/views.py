from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView

from taggit.models import Tag

from .models import Post, Comment
from .forms import CommentForm


class PostListView(ListView):
    """
    Generic class-based view for a list of posts.
    """
    queryset = Post.objects.all()
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'blogger/post/list.html'

def post_list(request, tag_slug=None):
    """
    Функция представления для домашней страницы сайта.
    """
    object_list = Post.objects.all()

    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        object_list = object_list.filter(tags__in=[tag])

    paginator = Paginator(object_list, 3) # 3 posts in each page
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer deliver the first page
        posts = paginator.page(1)
    except EmptyPage:
        # If page is out of range deliver last page of results
        posts = paginator.page(paginator.num_pages)
    return render(request, 'blogger/post/list.html', {'page': page, 'posts': posts, 'tag': tag})

def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post, slug=post, publish__year=year, publish__month=month, publish__day=day)
    # Список активных комментариев к этой статье
    comments = post.comments.filter(active=True)
    new_comment = None
    if request.method == 'POST':
        # Комментарий был опубликован
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            # Создать объект Comment, но пока не сохранять в базу данных
            new_comment = comment_form.save(commit=False)
            # Присвоить текущую статью комментарию
            new_comment.post = post
            # Сохранить комментарий в базе данных
            new_comment.save()
    else:
        comment_form = CommentForm()

    return render(request, 'blogger/post/detail.html', {'post': post, 'comments': comments, 'new_comment': new_comment, 'comment_form': comment_form})
