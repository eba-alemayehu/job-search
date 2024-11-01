import csv, math, datetime
from django.utils import timezone
from jobspy import scrape_jobs
import boto3
from decimal import Decimal
import yaml
from django.db.models import Q
from boto3.dynamodb.conditions import Key
from boto3.dynamodb.conditions import Attr
from zappa.asynchronous import task

from job.jobs.models import JobListing


# @task
def search(config, title):
    jobs = scrape_jobs(
        site_name=["indeed", "linkedin", "zip_recruiter", "glassdoor"],
        search_term=title,
        results_wanted=10,
        hours_old=2,
        country_indeed='USA',
        is_remote=True
    )
    print(f"Found {len(jobs)} jobs")
    jobs = jobs.to_dict(orient='records')
    for company in config['excluded_companies']:
        jobs = list(filter(lambda e: company != e['company'] and e['is_remote'] is True, jobs))

    dynamodb = boto3.resource('dynamodb', region_name='us-west-2')

    for job in jobs:
        job['date'] = datetime.datetime.now()
        job['_date'] = job['date'].timestamp()
        job['pk'] = f"{job['date_posted']}-{job['company']}-{job['title']}"
        # print(job['date'])
        print(job['title'].lower())
        print(list(map(lambda e: e.lower(), config['title'])))
        print("####################")
        if len(list(filter(lambda e: e.lower() in job['title'].lower(), config['title']))) == 0:
            print("Title not found")
            continue
        if ('hybrid' in str(job['description']).lower() or
                'citizen' in str(job['description']).lower() or
                'security clearance' in str(job['description']).lower()):
            continue

        print("*******************")
        job['company'] = str(job['company']).lower()
        job['_date_posted'] = datetime.datetime.combine(job['date_posted'], datetime.datetime.min.time()).timestamp()

        for x in job:
            if isinstance(job[x], float):
                job[x] = Decimal(str(job[x]))
                if math.isnan(job[x]):
                    job[x] = None
            elif isinstance(job[x], datetime.date):
                job[x] = job[x].strftime("%Y-%m-%d %H:%M:%S")

        print(job)
        if not JobListing.objects.filter(primary_key=job['pk']).exists():
            del job['pk']
            del job['_date']
            del job['_date_posted']
            del job['company_revenue']
            if job.get('id') is not None:
                job['job_id'] = job.pop('id')
            job['date'] = datetime.datetime.strptime(job.pop('date'), '%Y-%m-%d %H:%M:%S')
            job['date_posted'] = datetime.datetime.strptime(job.pop('date_posted'), '%Y-%m-%d %H:%M:%S')

            print(job.get('id'))
            job_listing = JobListing.objects.create(**job)
    return jobs


def find_job():
    with open('job/config.yaml', 'r') as file:
        config = yaml.safe_load(file)

    jobs = []
    for title in config['title']:
        jobs += search(config, title)

    print("Item inserted successfully!")


def create_table():
    dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
    table_name = 'jobs'
    table = dynamodb.create_table(
        TableName=table_name,
        KeySchema=[
            {
                'AttributeName': 'id',
                'KeyType': 'HASH'  # Partition key
            },
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'id',
                'AttributeType': 'S'  # String type
            },
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 5,
            'WriteCapacityUnits': 5
        }
    )

    # Wait until the table exists
    table.wait_until_exists()

    print(f"Table {table_name} created successfully!")


def delete_all_items(table_name):
    dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
    table = dynamodb.Table(table_name)

    # Scan the table
    response = table.scan()
    data = response['Items']

    # Loop through all items and delete them
    while 'LastEvaluatedKey' in response:
        for item in data:
            # Delete each item
            table.delete_item(
                Key={
                    'id': item['id']  # Replace 'id' with your table's primary key
                }
            )
        # Continue scanning
        response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        data = response['Items']

    # Delete remaining items
    for item in data:
        table.delete_item(
            Key={
                'id': item['id']  # Replace 'id' with your table's primary key
            }
        )

    print("All items deleted successfully.")
