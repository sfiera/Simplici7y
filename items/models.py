from django.db import models
from django.contrib.auth.models import User


class TimeStampMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        abstract = True


class Item(TimeStampMixin):
    name = models.CharField(max_length=255)
    body = models.TextField()
    tc = models.ForeignKey("self", null=True, blank=True, on_delete=models.PROTECT)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    permalink = models.CharField(max_length=255)


class Version(TimeStampMixin):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    body = models.TextField()
    file = models.FileField(upload_to="versions/", null=True, blank=True)
    link = models.CharField(max_length=255, null=True, blank=True)


class Download(TimeStampMixin):
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    version = models.ForeignKey(Version, on_delete=models.CASCADE)


class Review(TimeStampMixin):
    version = models.ForeignKey(Version, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    body = models.TextField()
    rating = models.IntegerField()


class Screenshot(TimeStampMixin):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    file = models.ImageField(upload_to="screenshots/", null=True, blank=True)


class Tag(models.Model):
    name = models.CharField(max_length=255)
    permalink = models.CharField(max_length=255)
    items = models.ManyToManyField(Item)
