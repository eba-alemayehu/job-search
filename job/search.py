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

from job.jobs.models import JobListing, JobSearch, JobFilter


# @task
def search(config, title, job_search, filters):
    jobs = scrape_jobs(
        site_name=["indeed", "linkedin", "zip_recruiter", "glassdoor"],
        search_term=title,
        results_wanted=10,
        hours_old=3,
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
        job['job_search'] = job_search
        job['job_id'] = f"{job['date_posted']}-{job['company']}-{job['title']}"
        job['company'] = str(job['company']).lower()

        for x in job:
            if isinstance(job[x], float):
                job[x] = Decimal(str(job[x]))
                if math.isnan(job[x]):
                    job[x] = None
            elif isinstance(job[x], datetime.date):
                job[x] = job[x].strftime("%Y-%m-%d %H:%M:%S")

        if not JobListing.objects.filter(job_id=job['job_id']).exists():
            del job['id']
            del job['company_revenue']

            job['date'] = datetime.datetime.strptime(job.pop('date'), '%Y-%m-%d %H:%M:%S')
            job['date_posted'] = datetime.datetime.strptime(job.pop('date_posted'), '%Y-%m-%d %H:%M:%S')

            job['job_filter'] = None
            for f in filters:
                if f.filter_type == 'IGNOR_ALL' and job.get('title') and f.key_word.lower() in job['title'].lower() or \
                        job.get('description') and f.key_word.lower() in job['description'].lower():
                    job['job_filter'] = f
                elif f.filter_type == 'IGNOR_FROM_TITLE' and job.get('title') and f.key_word.lower() in job['title'].lower():
                    job['job_filter'] = f
                elif f.filter_type == 'IGNOR_FROM_DESCRIPTION' and job.get('description') and f.key_word.lower() in job['description'].lower():
                    job['job_filter'] = f
                elif f.filter_type == 'COMPANY_NAME' and job.get('company') and f.key_word.lower() in job['company'].lower():
                    job['job_filter'] = f
                elif f.filter_type == 'KEY_WORD_NOT_IN_TITLE' and job.get('title') is not None and title.lower() not in job['title'].lower():
                    job['job_filter'] = f

            job_listing = JobListing.objects.create(**job)
            print(job_listing)
    return jobs


def find_job():
    with open('job/config.yaml', 'r') as file:
        config = yaml.safe_load(file)

    jobs = []
    filters = JobFilter.objects.all()
    for job_search in JobSearch.objects.all():
        jobs += search(config, job_search.key_word, job_search, filters)

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
