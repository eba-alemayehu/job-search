from django.contrib import admin
from django.urls import path
from django.shortcuts import render
from django.shortcuts import redirect
from boto3.dynamodb.conditions import Attr
from django.contrib.humanize.templatetags import humanize
import boto3, datetime


def delete_dynamodb_item(table_name, item_id):
    dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
    table = dynamodb.Table(table_name)

    try:
        # Perform the delete operation
        response = table.delete_item(
            Key={'id': item_id},  # Replace 'id' with the name of your partition key
            ReturnValues="ALL_OLD"  # Return the deleted item attributes
        )
        return response.get('Attributes', {})  # Return the deleted item attributes if any

    except Exception as e:
        return {'error': str(e)}  # Return error message if any exception occurs


def update_dynamodb_item(table_name, item_id, update_data):
    dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
    table = dynamodb.Table(table_name)

    # Construct UpdateExpression and ExpressionAttributeValues
    update_expression = "SET " + ", ".join(f"#{k} = :{k}" for k in update_data.keys())
    expression_attribute_names = {f"#{k}": k for k in update_data.keys()}
    expression_attribute_values = {f":{k}": v for k, v in update_data.items()}

    try:
        # Perform the update operation
        response = table.update_item(
            Key={'id': item_id},
            UpdateExpression=update_expression,
            ExpressionAttributeNames=expression_attribute_names,
            ExpressionAttributeValues=expression_attribute_values,
            ReturnValues="UPDATED_NEW"
        )
        return response.get('Attributes', {})  # Return updated attributes

    except Exception as e:
        return {'error': str(e)}  # Return error message


def map_items(item):
    parsed_date = datetime.datetime.strptime(item['date'], "%Y-%m-%d %H:%M:%S")
    item['date'] = humanize.naturaltime(parsed_date)
    return item


def get_all_items(key, applid, saved=None):
    dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
    table = dynamodb.Table('jobs')
    filter = None

    if key is not None:
        filter = Attr('company').contains(key.lower())

    if applid is not None:
        if filter is not None:
            filter = filter | Attr('is_applied').eq(True)
        else:
            filter = Attr('is_applied').eq(True)

    if saved is not None:
        if filter is not None:
            filter = filter | Attr('is_saved').eq(True)
        else:
            filter = Attr('is_saved').eq(True)

    if filter is not None:
        response = table.scan(
                FilterExpression=filter
        )
    else:
        response = table.scan()

    items = response.get('Items', [])
    items = sorted(items, key=lambda x: x['_date'], reverse=True)

    while 'LastEvaluatedKey' in response:
        response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        items.extend(response.get('Items', []))
    items = list(map(lambda e: map_items(e), items))
    print(items)
    return items


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
