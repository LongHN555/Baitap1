import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

app = FastAPI(title="AES Crypto Backend")

# Dữ liệu truyền lên từ Frontend
class CryptoRequest(BaseModel):
    key: str
    text: str

class DecryptRequest(BaseModel):
    key: str
    ciphertext_hex: str
    iv_hex: str

def get_32byte_key(raw_key: str) -> bytes:
    """Đảm bảo khóa bí mật luôn đúng 32 bytes (AES-256) bằng cách pad hoặc cắt"""
    key_bytes = raw_key.encode('utf-8')
    if len(key_bytes) < 32:
        return key_bytes.ljust(32, b'\0')
    return key_bytes[:32]

@app.post("/api/encrypt")
def encrypt_data(req: CryptoRequest):
    try:
        key_bytes = get_32byte_key(req.key)
        iv = os.urandom(16)  # IV ngẫu nhiên 16 bytes
        cipher = AES.new(key_bytes, AES.MODE_CBC, iv)
        
        data_padded = pad(req.text.encode('utf-8'), AES.block_size)
        ciphertext = cipher.encrypt(data_padded)
        
        return {
            "ok": True,
            "ciphertext": ciphertext.hex(),
            "iv": iv.hex()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/decrypt")
def decrypt_data(req: DecryptRequest):
    try:
        key_bytes = get_32byte_key(req.key)
        iv = bytes.fromhex(req.iv_hex)
        ciphertext = bytes.fromhex(req.ciphertext_hex)
        
        cipher = AES.new(key_bytes, AES.MODE_CBC, iv)
        decrypted_padded = cipher.decrypt(ciphertext)
        decrypted_text = unpad(decrypted_padded, AES.block_size).decode('utf-8')
        
        return {
            "ok": True,
            "plaintext": decrypted_text
        }
    except Exception as e:
        return {
            "ok": False,
            "msg": "Lỗi giải mã: Khóa không đúng hoặc bản mã bị hỏng!"
        }