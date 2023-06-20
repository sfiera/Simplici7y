from django.contrib.syndication.views import Feed
from markdownify.templatetags.markdownify import markdownify

from items.models import Review
from items.utils import get_filtered_items, page_size


class ItemsFeed(Feed):
    title = "Simplici7y Downloads"
    link = "http://simplici7y.com"
    description = "Latest updates and submissions to S7."

    def items(self):
        return get_filtered_items()

    def item_title(self, item):
        return item.name

    def item_description(self, item):
        return markdownify(item.body)


class ReviewsFeed(Feed):
    title = "Simplici7y Reviews"
    link = "https://simplici7y.com/reviews/"
    description = "Latest reviews on S7."

    item_guid_is_permalink = False

    def items(self):
        return Review.objects.order_by("-created_at")[:page_size]

    def item_guid(self, obj):
        return f"https://simplici7y.com/items/{obj.version.item.permalink}/reviews/{obj.id}"

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return markdownify(item.body)