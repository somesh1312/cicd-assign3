import boto3
import pandas as pd


def lambda_handler(event, context):
    # Retrieve bucket names and file paths from the event
    source_bucket = event['Records'][0]['s3']['bucket']['name']
    source_key = event['Records'][0]['s3']['object']['key']
    target_bucket = 'de-doordash-target-zn'
    sns_topic_arn = 'arn:aws:sns:us-east-1:038538804832:notifyme'

    # Read JSON file into Pandas DataFrame
    s3 = boto3.client('s3')
    obj = s3.get_object(Bucket=source_bucket, Key=source_key)
    df = pd.read_json(obj['Body'])

    # Filter records where status is "delivered"
    filtered_df = df[df['status'] == 'delivered']

    # Write filtered DataFrame to S3
    target_key = 'filtered_data.json'
    s3_resource = boto3.resource('s3')
    s3_resource.Object(target_bucket, target_key).put(
        Body=filtered_df.to_json())

    # Publish success message to SNS topic
    sns = boto3.client('sns')
    sns.publish(
        TopicArn=sns_topic_arn,
        Message='Data processing completed successfully!'
    )

    return {
        'statusCode': 200,
        'body': 'Data processing completed successfully!'
    }
