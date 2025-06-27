import time
import logging
from functools import wraps
from datetime import datetime
from django.http import JsonResponse

from finance.models import UserProfile

logger = logging.getLogger(__name__)

def check_api_token(function):
    @wraps(function)
    def wrapper(request, *args, **kwargs):
        api_token = request.headers.get('Authorization', '')

        if not api_token:
            return JsonResponse({'error': 'Token not given'}, status=401)
        
        if api_token.startswith('Bearer '):
            api_token = api_token[7:]
        else:
            return JsonResponse({'error': 'Token must statr with Bearer'}, status=401)
        
        try:
            profile = UserProfile.objects.get(api_key=api_token)
            request.api_user = profile.user
        except UserProfile.DoesNotExist:
            return JsonResponse({'error': 'Invalid token'}, status=401)
        
        return function(request, *args, **kwargs)
    return wrapper


def time_logger(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = function(*args, **kwargs)
        now = datetime.now()
        formatted = now.strftime("[%d/%b/%Y %H:%M:%S]")
        logger.info(f"{formatted} Function {function.__name__} executed in {time.time() - start:.3f} seconds")
        return result
    return wrapper