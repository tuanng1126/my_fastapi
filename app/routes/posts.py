from typing import List

from fastapi import HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from starlette import status
from starlette.responses import Response
from sqlalchemy import func
from app import models, schemas, oauth2
from app.database import get_db

router = APIRouter(prefix='/posts', tags=['Users'])


@router.get('/', response_model=List[schemas.PostResponse])
def get_posts(db: Session = Depends(get_db),
              current_user: models.User = Depends(oauth2.get_current_user),
              limit: int = 10,
              skip: int = 0,
              search: str = ""):
    posts = db.query(models.Post,
                     func.count(models.Vote.post_id).label("votes")).join(
        models.Vote, models.Vote.post_id == models.Post.id,
        isouter=True).group_by(models.Post.id).filter(
        models.Post.title.contains(search)).limit(limit).offset(skip).all()
    return posts


@router.post('/', status_code=status.HTTP_201_CREATED,
             response_model=schemas.PostResponse)
def create_posts(post: schemas.PostCreate, db: Session = Depends(get_db),
                 current_user: models.User = Depends(oauth2.get_current_user)):
    p = models.Post(owner_id=current_user.id, **post.dict())
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


@router.get('/{id}', response_model=schemas.PostResponse)
def get_post(id: int, db: Session = Depends(get_db),
             current_user: models.User = Depends(oauth2.get_current_user)):
    post = db.query(models.Post,
                    func.count(models.Vote.post_id).label("votes")).join(
        models.Vote, models.Vote.post_id == models.Post.id,
        isouter=True).group_by(models.Post.id).filter(
        models.Post.id == id).first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id {id} was not found")

    return post


@router.delete('/{id}')
def delete_post(id: int, db: Session = Depends(get_db),
                current_user: models.User = Depends(oauth2.get_current_user)):
    post = db.query(models.Post).filter_by(id=id).first()
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id {id} does not exist")
    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Not authorized to perform requested action")
    db.delete(post)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put('/{id}', response_model=schemas.PostResponse)
def update_post(id: int, post: schemas.PostCreate,
                db: Session = Depends(get_db),
                current_user: models.User = Depends(oauth2.get_current_user)):
    post_query = db.query(models.Post).filter_by(id=id)
    p = post_query.first()
    if p is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id {id} does not exist")
    if p.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Not authorized to perform requested action")
    post_query.update(post.dict(), synchronize_session=False)
    db.commit()
    return post_query.first()
