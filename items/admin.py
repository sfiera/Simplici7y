from django.contrib import admin
from .models import Item, Version, Download, Review, Screenshot, Tag


class ItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'body', 'tc', 'user', 'permalink', 'created_at', 'updated_at']


class VersionAdmin(admin.ModelAdmin):
    list_display = ['item', 'name', 'body', 'link', 'created_at', 'updated_at']


class DownloadAdmin(admin.ModelAdmin):
    list_display = ['user', 'version', 'created_at', 'updated_at']


class ReviewAdmin(admin.ModelAdmin):
    list_display = ['version', 'user', 'title', 'body', 'rating', 'created_at', 'updated_at']


class ScreenshotAdmin(admin.ModelAdmin):
    list_display = ['item', 'title', 'created_at', 'updated_at']


class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'permalink']


admin.site.register(Item, ItemAdmin)
admin.site.register(Version, VersionAdmin)
admin.site.register(Download, DownloadAdmin)
admin.site.register(Review, ReviewAdmin)
admin.site.register(Screenshot, ScreenshotAdmin)
admin.site.register(Tag, TagAdmin)