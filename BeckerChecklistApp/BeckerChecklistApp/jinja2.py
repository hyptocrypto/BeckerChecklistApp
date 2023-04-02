from jinja2 import Environment
from django.urls import reverse
from django.contrib.staticfiles.storage import staticfiles_storage
from django.utils.timezone import template_localtime


def environment(**options):
    env = Environment(**options)
    env.globals.update({"static": staticfiles_storage.url, "url": reverse})
    env.filters.update(
        {
            "localtime": template_localtime,
        }
    )
    env.globals.update(
        {
            "localtime": template_localtime,
        }
    )
    return env
