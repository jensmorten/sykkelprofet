from cryptography.fernet import Fernet


#key = Fernet.generate_key()
#print(key.decode())
key = b"PASTE_KEY_HERE"
cipher = Fernet(key)

with open("test_target_secret.csv", "rb") as f:
    original = f.read()

encrypted = cipher.encrypt(original)

with open("test_target_secret_encrypted.bin", "wb") as f:
    f.write(encrypted)

print("✅ Kryptert og lagret som test_target_secret_encrypted.bin")
lIkg0T0mWUBHyKLQFzAiZj6XEyWsJtUxTjGIufIhUfc=