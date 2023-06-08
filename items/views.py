from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Prefetch, Sum, Count, Q, ExpressionWrapper, F, FloatField, Avg, Exists, OuterRef
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.decorators import login_required
from .models import User
from rest_framework import viewsets, permissions
from .forms import UserForm
from .models import Item, Version, Download, Review, Screenshot, Tag
from .permissions import IsOwnerOrReadOnly
from .serializers import (
    ItemSerializer,
    VersionSerializer,
    DownloadSerializer,
    ReviewSerializer,
    ScreenshotSerializer,
    TagSerializer,
)


def page_not_found_view(request, exception):
    return render(request, "404.html", status=404)


# @login_required  # Remove after go-live
def items(request):

    latest_version = Prefetch(
        "version_set",
        queryset=Version.objects.order_by("-created_at"),
        to_attr="latest_version",
    )
    random_screenshots = Prefetch(
        "screenshot_set",
        queryset=Screenshot.objects.order_by("?"),
        to_attr="random_screenshot",
    )

    items = Item.objects.annotate(has_version=Exists(Version.objects.filter(item=OuterRef('pk'))))

    items = items.filter(has_version=True).prefetch_related(
        latest_version, random_screenshots, "user"
    )

    order = request.GET.get('order')
    search = request.GET.get('search', None)

    if search:
        items = items.filter(Q(name__icontains=search) | Q(body__icontains=search))

    # Calculate the average review score and the number of reviews for each item
    # items = items.annotate(avg_rating=Avg('version__review__rating'), num_reviews=Count('version__review'))

    # Calculate a weighted score by multiplying the average rating by the number of reviews
    # items = items.annotate(
    #     weighted_score=ExpressionWrapper(
    #         F('avg_rating') * F('num_reviews'),
    #         output_field=FloatField(),
    #     )
    # )

    # apply filters and ordering
    if order == 'new':
        items = items.order_by('-created_at')
    # elif order == 'old':
    #     items = items.order_by('created_at')
    # elif order == 'reviews':
    #     items = items.order_by('-avg_rating')
    # elif order == 'best':
    #     items = items.order_by('-weighted_score')
    # elif order == 'worst':
    #     items = items.order_by('ratings_weighted_count')
    # elif order == 'popular':
    #     items = items.order_by('-downloads_count')
    # elif order == 'unpopular':
    #     items = items.order_by('downloads_count')
    # elif order == 'day':
    #     items = items.filter(downloads_day_count__gt=0).order_by('-downloads_day_count')
    # elif order == 'week':
    #     items = items.filter(downloads_week_count__gt=0).order_by('-downloads_week_count')
    # elif order == 'month':
    #     items = items.filter(downloads_month_count__gt=0).order_by('-downloads_month_count')
    # elif order == 'loud':
    #     items = items.filter(review_set__count__gt=0).order_by('-reviews_count')
    # elif order == 'quiet':
    #     items = items.order_by('review_set__count')
    else:  # Default to new
        items = items.order_by('-created_at')

    paginator = Paginator(items, 20)

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(request, "items.html", {"page_obj": page_obj})


# @login_required  # Remove after go-live
def item_detail(request, item_permalink):
    item = get_object_or_404(
        Item.objects.annotate(total_downloads=Count("version__download")),
        permalink=item_permalink,
    )
    # item.prefetch_related('version_set', 'screenshot_set', 'review_set')
    item_version = item.find_version()
    item_screenshots = Screenshot.objects.filter(item=item).order_by('created_at').all()
    item_reviews = Review.objects.filter(version__item=item).order_by('-created_at').all()

    return render(
        request,
        "item_detail.html",
        {
            "item": item,
            "screenshots": item_screenshots,
            "version": item_version,
            "reviews": item_reviews,
        },
    )


class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]


class VersionViewSet(viewsets.ModelViewSet):
    queryset = Version.objects.all()
    serializer_class = VersionSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]


class DownloadViewSet(viewsets.ModelViewSet):
    queryset = Download.objects.all()
    serializer_class = DownloadSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]


class ScreenshotViewSet(viewsets.ModelViewSet):
    queryset = Screenshot.objects.all()
    serializer_class = ScreenshotSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


# @login_required  # Remove after go-live
def reviews(request):
    return render(request, "reviews.html")


# @login_required  # Remove after go-live
def users(request):
    return render(request, "users.html")


# @login_required
def submit(request):
    return render(request, "submit.html")


@login_required
def settings(request):
    return render(request, "settings.html")


@login_required
def logout_view(request):
    logout(request)
    return redirect("home")


@login_required  # Remove after go-live
def signup(request):
    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get("username")
            raw_password = form.cleaned_data.get("password1")
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect("items")
    else:
        form = UserForm()

    return render(request, "signup.html", {"form": form})


@login_required  # Remove after go-live
def login_view(request):
    # You would generally use Django's built-in views for this.
    pass


# @login_required  # Remove after go-live
def user(request, username):
    user = User.objects.get(username=username)
    return render(request, "user.html", {"user": user})


def view_404(request):
    return render(request, "404.html")
