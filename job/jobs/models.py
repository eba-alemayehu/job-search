from urllib.parse import urlparse

from django.db import models
from model_utils import Choices
from django.utils.translation import gettext as _


class JobFilter(models.Model):
    FILTER_TYPE = Choices(
        ('IGNOR_ALL', _('IGNOR_ALL')),
        ('IGNOR_FROM_TITLE', _('IGNOR_FROM_TITLE')),
        ('IGNOR_FROM_DESCRIPTION', _('IGNOR_FROM_DESCRIPTION')),
        ('COMPANY_NAME', _('COMPANY_NAME')),
        ('KEY_WORD_NOT_IN_TITLE', _('KEY_WORD_NOT_IN_TITLE'))
    )

    key_word = models.CharField(max_length=255)
    filter_type = models.CharField(choices=FILTER_TYPE, max_length=255)

    def __str__(self):
        return "{} - {}".format(self.key_word, self.filter_type)


class JobSearch(models.Model):
    key_word = models.CharField(max_length=255)

    def __str__(self):
        return self.key_word


class JobListing(models.Model):
    primary_key = models.CharField(max_length=100)
    job_search = models.ForeignKey(JobSearch, on_delete=models.CASCADE, null=True, blank=True)
    job_filter = models.ForeignKey(JobFilter, on_delete=models.CASCADE, null=True, blank=True)
    job_id = models.CharField(max_length=20, null=True, blank=True, default=None)
    site = models.CharField(max_length=50)
    job_url = models.URLField()
    job_url_direct = models.URLField(null=True, blank=True)
    title = models.CharField(max_length=100)
    company = models.CharField(max_length=100)
    location = models.CharField(max_length=100, null=True, blank=True)
    job_type = models.CharField(max_length=50, null=True, blank=True)
    date_posted = models.DateTimeField()
    salary_source = models.CharField(max_length=50, null=True, blank=True)
    interval = models.CharField(max_length=20, null=True, blank=True)
    min_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    max_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=10, null=True, blank=True)
    is_remote = models.BooleanField(default=False)
    is_saved = models.BooleanField(default=False)
    is_applied = models.BooleanField(default=False)
    job_level = models.CharField(max_length=50, null=True, blank=True)
    job_function = models.CharField(max_length=50, null=True, blank=True)
    company_industry = models.CharField(max_length=100, null=True, blank=True)
    listing_type = models.CharField(max_length=50, null=True, blank=True)
    emails = models.EmailField(null=True, blank=True)
    description = models.TextField()
    company_url = models.URLField(null=True, blank=True)
    company_url_direct = models.URLField(null=True, blank=True)
    company_addresses = models.TextField(null=True, blank=True)
    company_num_employees = models.CharField(max_length=100, null=True, blank=True)
    company_revenue = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    company_description = models.TextField(null=True, blank=True)
    logo_photo_url = models.URLField(null=True, blank=True)
    banner_photo_url = models.URLField(null=True, blank=True)
    ceo_name = models.CharField(max_length=100, null=True, blank=True)
    ceo_photo_url = models.URLField(null=True, blank=True)
    date = models.DateTimeField()
    date_posted = models.DateTimeField()
    created_at = models.DateTimeField(auto_now=True)

    @property
    def get_logo(self):
        parsed_url = urlparse(self.job_url)
        domain = parsed_url.netloc

        if domain == 'www.indeed.com':
            return 'https://upload.wikimedia.org/wikipedia/commons/thumb/f/fa/Indeed_logo.png/800px-Indeed_logo.png'
        elif domain == 'www.glassdoor.com':
            return 'https://careers.toaglobal.com/wp-content/uploads/2024/05/Glassdoor-Logo-1-1024x328.webp'
        elif domain == 'www.linkedin.com':
            return 'https://www.vhv.rs/dpng/d/405-4051803_linkedin-logo-png-linkedin-logo-2020-png-transparent.png'

    def __str__(self):
        return f"{self.title} at {self.company}"