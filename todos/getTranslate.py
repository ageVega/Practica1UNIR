import os
import json

from todos import decimalencoder
import boto3

dynamodb = boto3.resource('dynamodb')
translate = boto3.client('translate')
comprehend = boto3.client('comprehend')


def detect_language_task(task):
    response = comprehend.detect_dominant_language(Text = task)
    
    return response
    

def translate_task(task, source, target):
    response = translate.translate_text(
        Text = task,
        SourceLanguageCode = source,
        TargetLanguageCode = target)
    
    return response


def getTranslate(event, context):
    table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])

    # fetch todo from the database
    result = table.get_item(
        Key={
            'id': event['pathParameters']['id']
        }
    )
    
    task = result['Item']['text']
    
    source_result = detect_language_task(task)
    
    source = source_result['Languages'][0]['LanguageCode']
    
    target = event['pathParameters']['language']
    
    task_translated = translate_task(task, source, target)
    
    result['Item']['text'] = task_translated['TranslatedText']

    # create a response
    response = {
        "statusCode": 200,
        "body": json.dumps(result['Item'],
                           cls=decimalencoder.DecimalEncoder)
    }

    return response
