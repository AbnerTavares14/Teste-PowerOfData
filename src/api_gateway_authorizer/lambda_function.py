import jwt
import os


JWT_SECRET = os.environ.get('JWT_SECRET', 'seu-segredo-super-secreto')

def lambda_handler(event, context):
    try:
        token = event['authorizationToken'].split(' ')[1]

        decoded = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])

        return generate_policy(decoded['sub'], 'Allow', event['methodArn'])

    except Exception as e:
        print(e)
        return generate_policy('user', 'Deny', event['methodArn'])

def generate_policy(principal_id, effect, resource):
    policy = {
        'principalId': principal_id,
        'policyDocument': {
            'Version': '2012-10-17',
            'Statement': [{
                'Action': 'execute-api:Invoke',
                'Effect': effect,
                'Resource': resource
            }]
        }
    }
    return policy