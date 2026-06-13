import json
import boto3
from datetime import datetime

rekognition = boto3.client('rekognition')
dynamodb = boto3.resource('dynamodb')

table = dynamodb.Table('CelebrityDetection')

def lambda_handler(event, context):

    try:

        for record in event['Records']:

            bucket = record['s3']['bucket']['name']
            image_name = record['s3']['object']['key']

            print("Processing Image:", image_name)

            response = rekognition.recognize_celebrities(
                Image={
                    'S3Object': {
                        'Bucket': bucket,
                        'Name': image_name
                    }
                }
            )

            celebrity_faces = response['CelebrityFaces']

            # Celebrity detected
            if celebrity_faces:

                celebrity = celebrity_faces[0]

                celebrity_name = celebrity['Name']
                confidence = celebrity['MatchConfidence']

                urls = celebrity.get('Urls', [])

                if urls:
                    celebrity_url = "https://" + urls[0]
                else:
                    celebrity_url = "No URL Available"

                detection_status = "Celebrity Detected"

            # No celebrity detected
            else:

                celebrity_name = "Unknown"
                confidence = 0
                celebrity_url = "No URL Available"

                detection_status = "No Celebrity Detected"

            # Store data in DynamoDB
            table.put_item(
                Item={
                    'image_name': image_name,
                    'celebrity_name': celebrity_name,
                    'confidence': str(confidence),
                    'celebrity_url': celebrity_url,
                    'detection_status': detection_status,
                    'timestamp': str(datetime.now())
                }
            )

            print("Stored:", image_name)

        return {
            'statusCode': 200,
            'body': json.dumps('All images processed successfully')
        }

    except Exception as e:

        print("Error:", str(e))

        return {
            'statusCode': 500,
            'body': json.dumps(str(e))
        }
