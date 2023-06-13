from django import template
from django.urls import resolve

register = template.Library()


@register.simple_tag(takes_context=True)
def url_replace(context, **kwargs):
    query = context["request"].GET.copy()
    query.update(kwargs)
    return query.urlencode()


@register.simple_tag(takes_context=True)
def pagetitle(context, default):
    view = resolve(context["request"].path_info)

    if context["request"].path == "/":
        return "Marathon Aleph One community downloads."

    if "item" in context:
        return context["item"].name

    if view.view_name == "user" and "show_user" in context:
        return context["show_user"].first_name

    if default:
        return default

    return view.view_name.capitalize()


@register.simple_tag(takes_context=True)
def subtitle(context):
    subtitle = ""
    view = resolve(context["request"].path_info)
    order = context["request"].GET.get("order")

    if view.view_name in ["home", "items"]:
        subtitle = "Items"
        if not order:
            subtitle = "Latest Updates and Submissions"
    elif view.view_name == "scenario":
        subtitle = context["scenario"].name
    elif view.view_name == "tag":
        subtitle = f"Tagged '{context['tag'].name.capitalize()}'"
    if order:
        subtitle += order_name(order)

    return subtitle


def order_name(txt):
    name = " by "
    if txt == "new":
        name += "Latest Updates"
    elif txt == "old":
        name += "Oldest Updates"
    elif txt == "best":
        name += "Best Reviewed"
    elif txt == "worst":
        name = ""
    elif txt == "popular":
        name += "Most Downloads"
    elif txt == "unpopular":
        name += "Fewest Downloads"
    # elif txt == "day":
    #     name += "Daily Downloads"
    # elif txt == "week":
    #     name += "Weekly Downloads"
    # elif txt == "month":
    #     name += "Monthly Downloads"
    elif txt == "loud":
        name += "Most Reviews"
    elif txt == "quiet":
        name += "Fewest Reviews"
    return name
