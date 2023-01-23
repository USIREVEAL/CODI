import time
import traceback

from rest_framework import status
from rest_framework.response import Response


def error_handling(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            error = {'error': str(e)}
            traceback.print_exc()

            return Response(status=status.HTTP_400_BAD_REQUEST, data=error)
    return inner


def measure_time(func):
    def inner(*args, **kwargs):
        start = time.time()
        res = func(*args, **kwargs)
        stop = time.time()

        return res, round(stop - start, 3)
    return inner

