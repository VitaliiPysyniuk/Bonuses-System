import json

HTTP_BAD_REQUEST = {
    'statusCode': 400,
    'headers': {
        'Content-Type': 'application/json'
    },
    'body': json.dumps({'message': 'Bad Request'})
}

HTTP_NOT_FOUND = {
    'statusCode': 404,
    'headers': {
        'Content-Type': 'application/json'
    },
    'body': json.dumps({'message': 'Not found'})
}

HTTP_NO_CONTENT = {
    'statusCode': 204,
    'headers': {
        'Content-Type': 'application/json'
    }
}


def http_ok(data):
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json'
        },
        'body': json.dumps(data)
    }


def http_created(data):
    return {
        'statusCode': 201,
        'headers': {
            'Content-Type': 'application/json'
        },
        'body': json.dumps(data)
    }
