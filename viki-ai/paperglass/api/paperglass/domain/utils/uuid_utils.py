from uuid import uuid1, uuid4

def get_uuid():
    return uuid1().hex


def get_uuid4():
    return uuid4().hex