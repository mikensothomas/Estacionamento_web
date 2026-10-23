from datetime import datetime, timedelta, timezone
import jwt
from pwdlib import PasswordHash
from fastapi import HTTPException, status
from .config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

password_hash = PasswordHash.recommended()

def hash_senha(senha: str) -> str:
    return password_hash.hash(senha)

def verificar_senha(senha: str, senha_hash: str) -> bool:
    try:
        return password_hash.verify(senha, senha_hash)
    except Exception:
        return False

def criar_token(email: str) -> tuple[str, int]:
    expires_minutes = ACCESS_TOKEN_EXPIRE_MINUTES
    agora = datetime.now(timezone.utc)
    payload = {
        "sub": email,
        "iat": agora,
        "exp": agora + timedelta(minutes=expires_minutes),
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token, expires_minutes * 60

def decodificar_token(token: str) -> str:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        subject = payload.get("sub")
        if not subject:
            raise ValueError("Token sem usuário.")
        return subject
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sessão inválida ou expirada. Faça login novamente.",
            headers={"WWW-Authenticate": "Bearer"},
        )
