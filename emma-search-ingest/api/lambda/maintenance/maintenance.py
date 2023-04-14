"""
Displays an appropriate message and status code for an unavailable service.
"""

def lambda_handler(event, context):
    return {
        'statusCode': 503,
        'body': "The EMMA metadata service is unavailable for maintenance."
    }
