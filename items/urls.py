from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.urlpatterns import format_suffix_patterns
from .views import (
    DownloadViewSet,
    ItemViewSet,
    ReviewViewSet,
    ScreenshotViewSet,
    TagViewSet,
    VersionViewSet,
    about,
    item_detail,
    items,
    login_view,
    logout_view,
    reviews,
    settings,
    signup,
    submit,
    user,
    users,
    view_404,
)

router = DefaultRouter()
router.register(r"items", ItemViewSet)
router.register(r"versions", VersionViewSet)
router.register(r"downloads", DownloadViewSet)
router.register(r"reviews", ReviewViewSet)
router.register(r"screenshots", ScreenshotViewSet)
router.register(r"tags", TagViewSet)

urlpatterns = [
    path("", items, name="home"),
    path("about/", about, name="about"),
    path("api/", include(router.urls)),
    path("items/", items, name="items"),
    path("items/<str:item_permalink>/", item_detail, name="item_detail"),
    path("login/", login_view, name="login"),
    path("404/", view_404, name="view_404"),
    path("logout/", logout_view, name="logout"),
    path("reviews/", reviews, name="reviews"),
    path("settings/", settings, name="settings"),
    path("signup/", signup, name="signup"),
    path("submit/", submit, name="submit"),
    path("users/", users, name="users"),
    path("users/<str:username>/", user, name="user"),
]
