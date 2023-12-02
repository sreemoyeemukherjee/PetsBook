from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from .models import Post
from .forms import PostForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.db.models import Q
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
def home(request):
    return render(request, 'myapp/home.html')

def user_logout(request):
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
    random_posts = Post.objects.order_by('?')[:3]  # Retrieve 3 random posts
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
    random_posts = Post.objects.order_by('?')[:3]  # Retrieve 3 random posts
    return render(request, 'myapp/registration/login.html', {'form': form, 'random_posts': random_posts})

class PostListView(LoginRequiredMixin, View):
    def get(self, request):
        query = request.GET.get('q')
        posts = self.query_db(query)
        return render(request, 'myapp/home.html', {'posts': posts, 'query': query})

    def post(self, request):
        tag_form = PostForm(request.POST)  # Create an instance of the form for handling tags
        if tag_form.is_valid():
            post_id = request.POST.get('post_id')
            # print(tag_form.cleaned_data['action'])
            if request.POST.get('action') == 'tag':
                tag = tag_form.cleaned_data['tags']
                if tag and post_id:
                    try:
                        post = Post.objects.get(id=post_id)
                        post.tags += tag
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
                Q(description__icontains=query)
            )
        else:
            posts = Post.objects.all()
        return posts

    def flag_post(self, request, post_id):
        post = get_object_or_404(Post, pk=post_id)
        if not post.is_flagged:
            post.is_flagged = True
            post.save()
            # additional actions if needed
        query = request.GET.get('q')
        posts = self.query_db(query)
        return render(request, 'myapp/home.html', {'posts': posts, 'query': query})

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