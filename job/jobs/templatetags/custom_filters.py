# your_app/templatetags/custom_filters.py

from django import template
from urllib.parse import urlparse

register = template.Library()

@register.filter
def get_domain(url):
    parsed_url = urlparse(url)
    return parsed_url.netloc  # Returns only the domain part