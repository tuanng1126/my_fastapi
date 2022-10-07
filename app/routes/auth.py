from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app import utils, oauth2
from app.database import get_db
from app.models import User
from app.schemas import Token

router = APIRouter(prefix='/auth', tags=['Authentication'])


@router.post('/login', response_model=Token)
def login(user_credentials: OAuth2PasswordRequestForm = Depends(),
          db: Session = Depends(get_db)):
    user = db.query(User).filter_by(email=user_credentials.username).first()
    if not user or not utils.verify(user_credentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Invalid credentials")
    access_token = oauth2.create_access_token(data={"user_id": user.id})
    return {
        'access_token': access_token,
        'token_type': 'Bearer'
    }
