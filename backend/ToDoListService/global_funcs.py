from rest_framework import status
from rest_framework.response import Response
import hashlib
import time

def generate_custom_id():
    
    raw = f"{time.time_ns()}".encode()
    return hashlib.sha256(raw).hexdigest()[:16]


def standard_response(data=None, message=None, status_code=status.HTTP_200_OK, errors=None):
    response = {
        'status': 'success' if status_code < 400 else 'error',
        'message': message,
        'data': data,
        'errors': errors
    }
    return Response(response, status=status_code)