DUMMY_RESPONSE = {
    200: {'description': 'Success', 'content': {'application/json': {'example': {'status': 'SUCCESS', 'data': {'id': '1', 'name': 'John Doe', 'email': 'test@gmail.com'}}}}},
    302: {'description': 'The item was moved', 'content': {'application/json': {'example': {'status': 'FAIL', 'errorData': {'errorCode': 302, 'message': 'error message'}}}}},
    403: {'description': 'Not enough privileges', 'content': {'application/json': {'example': {'status': 'FAIL', 'errorData': {'errorCode': 403, 'message': 'error message'}}}}},
    404: {'description': 'Item not found', 'content': {'application/json': {'example': {'status': 'FAIL', 'errorData': {'errorCode': 404, 'message': 'error message'}}}}},
}
