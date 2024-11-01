from django.contrib import admin
from django.urls import path
from django.shortcuts import render
from django.shortcuts import redirect
from boto3.dynamodb.conditions import Attr
from django.contrib.humanize.templatetags import humanize
import boto3, datetime
from job.jobs import models


def delete_dynamodb_item(table_name, item_id):
    models.JobListing.objects.filter(id=item_id).delete()

def update_dynamodb_item(table_name, item_id, update_data):
    return models.JobListing.objects.filter(id=item_id).update(**update_data)


def map_items(item):
    parsed_date = datetime.datetime.strptime(item['date'], "%Y-%m-%d %H:%M:%S")
    item['date'] = humanize.naturaltime(parsed_date)
    return item


def get_all_items(key, applid, saved=None):
    jobs = models.JobListing.objects

    if key is not None:
        jobs = jobs.filter(company__icontains = key.lower())

    if applid is not None:
        jobs = jobs.filter(is_applied=True)

    if saved is not None:
        jobs = jobs.filter(is_saved=True)

    jobs = jobs.order_by('-date')

    return jobs


def jobs_view(request):
    key = request.GET.get('key', None)
    applied = request.GET.get('applied', None)
    context = {
        "jobs": get_all_items(key, applied),
        "key": key,
        "applied": applied
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


urlpatterns = [
    path('admin/', admin.site.urls),
    path('apply/<str:id>', apply),
    path('delete/<str:id>', delete),
    path('save/<str:id>', save),
    path('saved', jobs_saved),
    path('applied', jobs_applied),
    path('', jobs_view, name="home"),
    path('', jobs_view),
]
