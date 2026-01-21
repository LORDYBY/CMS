# import hashlib

# def sha256_file(file_path: str) -> str:
#     sha256 = hashlib.sha256()
#     with open(file_path, "rb") as f:
#         for chunk in iter(lambda: f.read(8192), b""):
#             sha256.update(chunk)
#     return sha256.hexdigest()


import hashlib

def compute_checksum(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()
