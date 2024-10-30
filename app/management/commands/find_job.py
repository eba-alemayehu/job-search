from django.core.management.base import BaseCommand, CommandError
import requests
from job.search import find_job


class Command(BaseCommand):
    help = 'Get servers current out going ip'

    def handle(self, *args, **options):
        find_job()



