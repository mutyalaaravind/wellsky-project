import hashlib

def get_sha256_hash(binary_data):    
    sha256_hash = hashlib.sha256(binary_data)
    return sha256_hash.hexdigest()