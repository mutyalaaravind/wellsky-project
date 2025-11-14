

def chunk_array(array, chunk_size):
    return [array[i:i + chunk_size] for i in range(0, len(array), chunk_size)]

def split_tuple_object(t):
    t0 = list(t.keys())[0]
    t1 = list(t.values())[0]
    return t0, t1