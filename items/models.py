from uuid import uuid4

from django.db import models
from django.db.models import F, Max, Q
from django.db.models.functions import Coalesce
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.text import slugify
from django.contrib.auth.models import AbstractUser

from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFit


def get_model_name(instance):
    return instance.__class__.__name__.lower()


def get_upload_path(instance, filename):
    return f"{get_model_name(instance)}s/item-{instance.item.id}/{uuid4()}/{filename}"


class TimeStampMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, editable=False, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        abstract = True


class User(AbstractUser):
    # Cached / calculated fields
    items_count = models.PositiveIntegerField(default=0)
    reviews_count = models.PositiveIntegerField(default=0)

    def get_absolute_url(self):
        return reverse("user", kwargs={"username": self.username})


class Tag(models.Model):
    name = models.CharField(max_length=255)
    permalink = models.CharField(max_length=255)
    count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name


class Item(TimeStampMixin):
    name = models.CharField(max_length=255, db_index=True)
    byline = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    topnote = models.TextField(null=True, blank=True)
    body = models.TextField()
    tc = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.PROTECT, related_name="items"
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="items")
    permalink = models.SlugField(max_length=255, unique=True)
    tags = models.ManyToManyField(Tag)

    # Cached / calculated fields
    downloads_count = models.PositiveIntegerField(default=0, db_index=True)
    reviews_count = models.PositiveIntegerField(default=0, db_index=True)
    screenshots_count = models.PositiveIntegerField(default=0)
    rating_average = models.FloatField(default=0.0, db_index=True)
    rating_weighted = models.FloatField(default=0.0, db_index=True)
    version_created_at = models.DateTimeField(null=True, db_index=True)

    class Meta:
        ordering = ["-version_created_at"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        created = self.pk is None
        if created:
            self.permalink = slugify(self.name)

        super().save(*args, **kwargs)

        if created:
            User.objects.filter(pk=self.user.pk).update(
                items_count=models.F("items_count") + 1
            )

    def delete(self, *args, **kwargs):
        User.objects.filter(pk=self.user.pk).update(
            items_count=models.F("items_count") - 1
        )
        super().delete(*args, **kwargs)

    def find_version(self):
        return Version.objects.filter(item=self).latest("created_at")

    def rand_screenshot(self):
        return Screenshot.objects.order_by("?").first()

    def get_absolute_url(self):
        return reverse("item_detail", kwargs={"item_permalink": self.permalink})

    def get_byline(self):
        if self.byline:
            return self.byline
        else:
            return self.user.first_name



class Version(TimeStampMixin):
    item = models.ForeignKey(
        Item, on_delete=models.CASCADE, related_name="versions", db_index=True
    )
    name = models.CharField(max_length=255)
    body = models.TextField()
    file = models.FileField(upload_to=get_upload_path, null=True, blank=True)
    link = models.CharField(max_length=255, null=True, blank=True)

    # Cached / calculated fields
    downloads_count = models.PositiveIntegerField(default=0)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=Q(link__isnull=False) | Q(file__isnull=False),
                name="version_must_have_link_or_file",
            )
        ]

    def __str__(self):
        return f"{self.item} {self.name} by {self.item.user}"

    def download_button(self):
        url = reverse("item_download", kwargs={"item_permalink": self.item.permalink})

        if self.file:
            url = '<a href="{}" rel="nofollow" class="button down">Download</a>'.format(
                url
            )
        elif self.link:
            url = '<a href="{}" rel="nofollow" class="button next" target="_blank">Webpage</a>'.format(
                url
            )
        else:
            url = ""

        return mark_safe('<div>{}</div>'.format(url))

    def save(self, *args, **kwargs):
        created = self.pk is None
        super().save(*args, **kwargs)

        if created:
            Item.objects.filter(pk=self.item.pk).update(
                version_created_at=self.created_at
            )

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)

        Item.objects.filter(pk=self.item.pk).update(
            version_created_at=Coalesce(Max("versions__created_at"), None)
        )


class Download(TimeStampMixin):
    user = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.CASCADE, related_name="downloads"
    )
    version = models.ForeignKey(
        Version, on_delete=models.CASCADE, related_name="downloads"
    )

    def __str__(self):
        if self.user is not None:
            return f"Download by {self.user.first_name} of version {self.version.name}"

        return f"Download of version {self.version.name}"

    def save(self, *args, **kwargs):
        created = self.pk is None
        super().save(*args, **kwargs)

        if created:
            Item.objects.filter(pk=self.version.item.pk).update(
                downloads_count=models.F("downloads_count") + 1
            )

    def delete(self, *args, **kwargs):
        Item.objects.filter(pk=self.version.item.pk).update(
            downloads_count=models.F("downloads_count") - 1
        )
        super().delete(*args, **kwargs)


class Review(TimeStampMixin):
    version = models.ForeignKey(
        Version, on_delete=models.CASCADE, related_name="reviews", db_index=True
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="reviews", db_index=True
    )
    title = models.CharField(max_length=255)
    body = models.TextField()
    rating = models.IntegerField()

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(rating__gte=1, rating__lte=5), name="rating_range"
            ),
        ]

    def __str__(self):
        return f"Review by {self.user.first_name} - {self.title}"

    def get_absolute_url(self):
        return self.version.item.get_absolute_url()

    def can_be_edited_by(self, user):
        return self.user == user or user.is_superuser

    def save(self, *args, **kwargs):
        created = self.pk is None
        super().save(*args, **kwargs)

        if created:
            Item.objects.filter(pk=self.version.item.pk).update(
                reviews_count=models.F("reviews_count") + 1
            )
            User.objects.filter(pk=self.user.pk).update(
                reviews_count=models.F("reviews_count") + 1
            )

    def delete(self, *args, **kwargs):
        Item.objects.filter(pk=self.version.item.pk).update(
            reviews_count=models.F("reviews_count") - 1
        )
        User.objects.filter(pk=self.user.pk).update(
            reviews_count=models.F("reviews_count") - 1
        )
        super().delete(*args, **kwargs)


class Screenshot(TimeStampMixin):
    item = models.ForeignKey(
        Item, on_delete=models.CASCADE, related_name="screenshots", db_index=True
    )
    title = models.CharField(max_length=255, blank=True)
    file = models.ImageField(upload_to=get_upload_path)
    file_thumb = ImageSpecField(
        source="file",
        processors=[ResizeToFit(300, 400)],
        format="JPEG",
        options={"quality": 90},
    )
    file_content = ImageSpecField(
        source="file",
        processors=[ResizeToFit(920, 1600)],
        format="JPEG",
        options={"quality": 90},
    )

    def __str__(self):
        return self.title

    def label(self):
        return f'Screenshot titled "{self.title}"' or f"Screenshot"

    def save(self, *args, **kwargs):
        created = self.pk is None
        super().save(*args, **kwargs)

        if created:
            Item.objects.filter(pk=self.item.pk).update(
                screenshots_count=models.F("screenshots_count") + 1
            )

    def delete(self, *args, **kwargs):
        Item.objects.filter(pk=self.item.pk).update(
            screenshots_count=models.F("screenshots_count") - 1
        )
        super().delete(*args, **kwargs)
