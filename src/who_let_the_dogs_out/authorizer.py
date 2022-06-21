from src.who_let_the_dogs_out.util.authorization_validator import AuthorizationValidator

authorization_helper = AuthorizationValidator()


def handle(event, _):
    token = event['headers']['Authorization']
    claims = authorization_helper.validate(token)

    return __build_auth_response(event, claims['username'])


def __build_auth_response(event, username):
    arn = event['methodArn']
    arn_parts = arn.split('/')
    route_name = arn_parts[-1]
    all_routes_arn = arn.replace(route_name, '*')

    return {
        'principalId': username,
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
            'username': username
        }
    }
