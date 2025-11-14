import functools

def read_from_file(file_path):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with open(file_path, 'r') as file:
                content = file.read()
            return func(content, *args, **kwargs)
        return wrapper
    return decorator