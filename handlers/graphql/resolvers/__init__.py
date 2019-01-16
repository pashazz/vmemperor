from functools import wraps


def with_connection(method):
    @wraps(method)
    def decorator(self, info, *args, **kwargs):
        with info.context.conn:
            return method(self, info, *args, **kwargs)

    return decorator

