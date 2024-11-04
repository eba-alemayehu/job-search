from django.contrib import admin
from django.urls import path
from django.shortcuts import render
from django.shortcuts import redirect
from boto3.dynamodb.conditions import Attr
from django.contrib.humanize.templatetags import humanize
import boto3, datetime
from job.jobs import models
from job.search import find_job


def delete_dynamodb_item(table_name, item_id):
    models.JobListing.objects.filter(id=item_id).delete()

def update_dynamodb_item(table_name, item_id, update_data):
    return models.JobListing.objects.filter(id=item_id).update(**update_data)


def map_items(item):
    parsed_date = datetime.datetime.strptime(item['date'], "%Y-%m-%d %H:%M:%S")
    item['date'] = humanize.naturaltime(parsed_date)
    return item


def get_all_items(key, applid, saved=None, is_filtered=False, is_remote=None):
    jobs = models.JobListing.objects

    if key is not None:
        jobs = jobs.filter(company__icontains = key.lower())

    if applid is not None:
        jobs = jobs.filter(is_applied=True)

    if saved is not None:
        jobs = jobs.filter(is_saved=True)

    if is_filtered is True:
        jobs = jobs.filter(job_filter__isnull=True)

    if is_remote is True:
        jobs = jobs.filter(is_remote=True)

    jobs = jobs.order_by('-created_at')

    return jobs


def jobs_view(request):
    key = request.GET.get('key', None)
    applied = request.GET.get('applied', None)
    search_keys = models.JobSearch.objects.all()
    filter_keys = models.JobFilter.objects.all()
    context = {
        "jobs": get_all_items(key, applied, is_filtered=True, is_remote=True),
        "key": key,
        "applied": applied,
        "search_keys": search_keys,
        "filter_keys": filter_keys
    }
    return render(request, 'job.html', context)


def all_jobs(request):
    key = request.GET.get('key', None)
    applied = request.GET.get('applied', None)
    search_keys = models.JobSearch.objects.all()
    filter_keys = models.JobFilter.objects.all()
    context = {
        "jobs": get_all_items(key, applied, is_filtered=False),
        "key": key,
        "applied": applied,
        "search_keys": search_keys,
        "filter_keys": filter_keys
    }
    return render(request, 'job.html', context)


def jobs_applied(request):
    key = request.GET.get('key', None)
    context = {
        "jobs": get_all_items(key, True),
        "key": key,
        "applied": True
    }
    return render(request, 'job.html', context)


def jobs_saved(request):
    key = request.GET.get('key', None)
    context = {
        "jobs": get_all_items(key, None, True),
        "key": key,
        "is_saved": True
    }
    return render(request, 'job.html', context)


def query_dynamodb(partition_key_value):
    # Initialize a session using Amazon DynamoDB
    dynamodb = boto3.resource('dynamodb')

    # Select your DynamoDB table
    table = dynamodb.Table('YourTableName')

    # Query the table
    try:
        response = table.query(
            KeyConditionExpression= Key('partitionKeyName').eq(partition_key_value)
        )
        return response['Items']
    except Exception as e:
        print(f"Error querying DynamoDB: {e}")
        return None


# Usage

def apply(request, id):
    print(update_dynamodb_item("jobs", id, {"is_applied": True}))
    return redirect('home')


def delete(request, id):
    print(delete_dynamodb_item("jobs", id))
    return redirect('home')


def save(request, id):
    print(update_dynamodb_item("jobs", id, {"is_saved": True}))
    return redirect('home')


def add_job_search_key(request):
    key = request.POST.get('job_search_key', None)
    job_search = models.JobSearch.objects.create(key_word=key)
    return redirect('home')

def add_job_filter_key(request):
    key = request.POST.get('job_filter_key', None)
    filter_type = request.POST.get('filter_type', None)
    job_search = models.JobFilter.objects.create(key_word=key, filter_type=filter_type)
    return redirect('home')

def delete_key_word(request, id):
    job_search = models.JobSearch.objects.get(id=id)
    job_search.delete()
    return redirect('home')


def delete_filter_key_word(request, id):
    job_search = models.JobFilter.objects.get(id=id)
    job_search.delete()
    return redirect('home')


def _find_job(request):
    find_job()
    return redirect('home')


urlpatterns = [
    path('admin/', admin.site.urls),
    path('apply/<str:id>', apply),
    path('delete/<str:id>', delete),
    path('delete_key_word/<str:id>', delete_key_word),
    path('delete_filter_key_word/<str:id>', delete_filter_key_word),
    path('save/<str:id>', save),
    path('saved', jobs_saved),
    path('applied', jobs_applied),
    path('add_job_search_key', add_job_search_key),
    path('add_job_filter_key', add_job_filter_key),
    path('find_job', _find_job),
    path('all', all_jobs, name="all"),
    path('', jobs_view, name="home"),
    path('', jobs_view),
]
