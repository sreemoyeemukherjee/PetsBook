from datetime import datetime
import pytz
from django.shortcuts import render, redirect, get_object_or_404
from django.template import Context

from .models import Post
from .forms import PostForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.db.models import Q, Count
from django.contrib.auth import authenticate, login, logout
from .forms import SignUpForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView


@login_required
def addPost(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.username = request.user.username
            post.save()
            return redirect('home')  # Change 'home' to your post listing page URL
    else:
        form = PostForm()
    return render(request, 'myapp/addPost.html', {'form': form})


@login_required
def messages(request):
    request.user.profile.has_clicked_messages = True
    request.user.profile.save()
    # new post message(s) logic
    user = request.user.profile
    posts_between_timestamps = Post.objects.filter(created_at__range=(user.last_logged_time, datetime.now(pytz.utc))).exclude(username=request.user)
    context = {'count': len(posts_between_timestamps), 'id': [], 'newposts': [], 'level': ""}
    for post in posts_between_timestamps:
        # if not post.username.__eq__(request.user):
        context['id'].append(post.id)
        context['newposts'].append({'id': post.id, 'message': "New Post: " + post.username + " posted about " + post.title})
    # Badge message logic
    count = Post.objects.filter(username=request.user).count()
    if count < 1:
        context['level'] = "You're " + str(1 - count) + (
            "post(s) away from unlocking Level 1! What are you waiting for? "
            "Post now")
    elif count < 3:
        context['level'] = "You're " + str(3 - count) + ("post(s) away from unlocking Level 2! What are you waiting "
                                                         "for?Post now")
    elif count < 6:
        context['level'] = "You're " + str(6 - count) + (
            "post(s) away from unlocking Level 3! What are you waiting for? "
            "Post now")
    elif count < 10:
        context['level'] = "You're " + str(10 - count) + (
            "post(s) away from unlocking Level 4! What are you waiting for? "
            "Post now")
    else:
        context['level'] = ("Message from Us: Thank you for being a amazing contributor. You have created 10+ "
                            "posts! Keep posting away!")
    return render(request, 'myapp/messages.html', context)


@login_required
def user_logout(request):
    # Update last_logged_out_time in  user Profile
    request.user.profile.has_clicked_messages = False
    request.user.profile.last_logged_time = datetime.now(pytz.utc)
    request.user.profile.save()
    logout(request)
    # Redirect to the home page or another page after logout
    return redirect('home')


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            # messages.success(request, 'Signup successful. Welcome!')
            return redirect('home')  # Change 'home' to your home page URL
        else:
            messages.error(request, 'Signup failed. Please correct the errors.')
    else:
        form = SignUpForm()
    random_posts = Post.objects.filter(is_flagged=False).order_by('?')[:3]  # Retrieve 3 random posts
    return render(request, 'myapp/registration/signup.html', {'form': form, 'random_posts': random_posts})


def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                return redirect('home')  # Change 'home' to your home page URL
    else:
        form = AuthenticationForm()
    random_posts = Post.objects.filter(is_flagged=False).order_by('?')[:3]  # Retrieve 3 random posts
    return render(request, 'myapp/registration/login.html', {'form': form, 'random_posts': random_posts})


@login_required
def badges(request):
    count = Post.objects.filter(username=request.user).count()
    return render(request, 'myapp/badges.html', {'count': count})


@login_required
def dashboard(request):
    context = {}
    count = Post.objects.filter(username=request.user).count()
    most_posts_user = Post.objects.values('username').annotate(post_count=Count('id')).order_by('-post_count').first()
    print(most_posts_user['post_count'])
    context['count'] = count
    context['top'] = round(100 - 100*count/most_posts_user['post_count'], 2)
    if count < 1:
        context['level'] = 0
    elif count < 3:
        context['level'] = 1
    elif count < 6:
        context['level'] = 2
    elif count < 10:
        context['level'] = 3
    else:
        context['level'] = 4
    return render(request, 'myapp/dashboard.html', context)


class PostListView(LoginRequiredMixin, View):
    def get(self, request):
        query = request.GET.get('q')
        posts = self.query_db(query)
        return render(request, 'myapp/home.html', {'posts': posts, 'query': query})

    def post(self, request):
        form = PostForm(request.POST)  # Create an instance of the form for handling tags
        if form.is_valid():
            post_id = request.POST.get('post_id')
            # print(form.cleaned_data['action'])
            if request.POST.get('action') == 'tag':
                tag = form.cleaned_data['tags']
                if tag and post_id:
                    try:
                        post = Post.objects.get(id=post_id)
                        if post.tags:
                            post.tags += tag.lower() + "; "
                        else:
                            post.tags = tag.lower() + '; '
                        post.save()
                    except Post.DoesNotExist:
                        pass
            elif request.POST.get('action') == 'flag':
                post = get_object_or_404(Post, pk=post_id)
                if not post.is_flagged:
                    post.is_flagged = True
                    post.save()
        query = request.GET.get('q')
        posts = self.query_db(query)
        return render(request, 'myapp/home.html', {'posts': posts, 'query': query})

    def query_db(self, query):
        if query:
            posts = Post.objects.filter(
                Q(username__icontains=query) |
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(tags__icontains=query)
            )
        else:
            posts = Post.objects.all()
        return posts


class CustomLoginView(LoginView):
    def get(self, request, *args, **kwargs):
        # If a custom 'next' parameter is specified in the URL, use it
        next_url = request.GET.get('next', None)
        if not next_url:
            # If 'next' is not specified, use a default URL
            next_url = ''
        return self.render_to_response(self.get_context_data(next=next_url))

    def form_valid(self, form):
        # messages.success(self.request, 'Login successful.')
        return super().form_valid(form)

# username: admin
# password: admin12345
