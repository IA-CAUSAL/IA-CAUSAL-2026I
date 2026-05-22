import hashlib

# 1. Choose an algorithm and create a hash object
data = "Amazon"
sha256_hash = hashlib.sha256(data.encode())

# 2. Get the hash digest as a hexadecimal string
hex_output = sha256_hash.hexdigest()

print(f"SHA-256: {hex_output}")

