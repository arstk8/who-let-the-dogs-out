from os import getenv


def handle(event, _):
    headers = event['headers']
    if 'cloudfront-secret' not in headers:
        print('Cloudfront secret missing from headers!')
        raise Exception('Unauthorized')

    actual_secret = headers['cloudfront-secret']
    expected_secret = getenv('CLOUDFRONT_SECRET')
    if actual_secret != expected_secret:
        print('Cloudfront secret mismatch!')
        raise Exception('Unauthorized')

    return __build_auth_response(event)


def __build_auth_response(event):
    connection_id = event['requestContext']['connectionId']

    arn = event['methodArn']
    arn_parts = arn.split('/')
    route_name = arn_parts[-1]
    all_routes_arn = arn.replace(route_name, '*')

    return {
        'principalId': connection_id,
        'policyDocument': {
            'Version': '2012-10-17',
            'Statement': [
                {
                    'Action': 'execute-api:Invoke',
                    'Effect': 'Allow',
                    'Resource': all_routes_arn
                }
            ]
        },
        'context': {
        }
    }
