from paperglass.domain.values import ChangeTracker


def change_tracker_updates(name):
    def decorator(func):
        def wrapper(*args, **kwargs):
            if args:   
                for value in args:
                    if isinstance(value, ChangeTracker):
                        value.name = name
            result = func(*args, **kwargs)
            return result
        return wrapper
    return decorator