
from django.urls import reverse_lazy
from django.urls import reverse
from django.views.generic import ListView, DetailView, UpdateView, CreateView, DeleteView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.detail import SingleObjectMixin
from django.shortcuts import get_object_or_404, redirect
from .models import Post
from .forms import CommentForm, PostForm
from actstream import action
# Create your views here.


class ObjectOwnerMixin:

    def get_queryset(self):
        return self.model.objects.filter(author=self.request.user)


class PublishedMixin:

    def get_queryset(self):
        return self.model.objects.filter(publish=True).order_by('-created')


class UnPublishedMixin:

    def get_queryset(self):
        return self.model.objects.filter(author=self.request.user, publish=False).order_by('-created')


class PostListView(PublishedMixin, ListView):
    model = Post
    paginate_by = 5


class PostListMyUnpulbished(UnPublishedMixin, LoginRequiredMixin, ListView):
    model = Post
    paginate_by = 5
    # template_name = 'blog/post_list_drafts.html'


class PostDetailView(DetailView):
    model = Post


class PostResultsView(DetailView):
    template_name = 'blog/results.html'


class PostUpdateView(ObjectOwnerMixin, LoginRequiredMixin, UpdateView):
    model = Post
    fields = ['title', 'text', 'publish']

    def get_success_url(self):
        return reverse('blog:detail',
                       kwargs={'pk': self.object.pk})


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    # fields = ['title', 'text']
    form_class = PostForm

    def form_valid(self, form):
        post = form.save(commit=False)
        post.author = self.request.user
        post.save()
        action.send(self.request.user, verb='created post', action_object=None, target=post)
        return super(PostCreateView, self).form_valid(form)

    def get_success_url(self):
        return reverse('blog:detail',
                       kwargs={'pk': self.object.pk})


class PublishPostView(SingleObjectMixin, View):
    model = Post

    def post(self, *args, **kwargs):
        self.object = self.get_object()
        self.object.publish = True
        self.object.save(update_fields=('publish', ))
        return redirect(to='blog:drafts')
        # return HttpResponse(status=204)


class PostDeleteView(ObjectOwnerMixin, LoginRequiredMixin, DeleteView):
    model = Post
    success_url = reverse_lazy('blog:list')


class CommentView(LoginRequiredMixin, CreateView):
    form_class = CommentForm
    template_name = 'blog/comment.html'

    def form_valid(self, form):
        comment = form.save(commit=False)

        post = get_object_or_404(Post, pk=self.kwargs['pk'])
        comment.post = post
        comment.author = self.request.user
        comment.save()
        action.send(self.request.user, verb='created comment on ', action_object=None, target=post)
        return super(CommentView, self).form_valid(form)

    def get_success_url(self):
        return reverse('blog:detail',
                       kwargs={'pk': self.object.post.pk})
