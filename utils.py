import inspect
import traceback
from datetime import datetime

def inspect_caller():
    stack = inspect.stack()
    if not len(stack):
        return None
    frame = None
    i = 2
    while i < len(stack):
        frame = stack[i]
        if frame.function != 'decorator':
            break
    return f"{frame.filename}:{frame.lineno}: {frame.function} (code: '{frame.code_context})')"


def print_graphql_exception(error):

    from tornado.options import options as opts
    with open(opts.graphql_error_log_file, 'a') as file:
        file.write(f"Date: {datetime.now().isoformat()}\n")
        traceback.print_exception(None, error, error.__traceback__, file=file)
