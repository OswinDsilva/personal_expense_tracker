from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..auth.jwt import get_current_user
from ..database import get_db
from ..models import Category, User
from ..schema import CategoryRequest, CategoryResponse

router = APIRouter(prefix="/categories", tags=["categories"])


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=CategoryResponse)
async def create_category(
    category: CategoryRequest, curr_user=Depends(get_current_user), db: Session = Depends(get_db)
) -> CategoryResponse:
    cat = Category(name=category.name)
    try:
        db.add(cat)
        db.commit()
        db.refresh(cat)
        return cat
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Category exists")


@router.get("/", response_model=List[CategoryResponse])
async def get_all_categories(
    curr_user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> List[CategoryResponse]:
    categories = db.execute(select(Category)).scalars().all()
    return categories


@router.get("/{id}", response_model=CategoryResponse)
async def get_category(
    id: int, curr_user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> CategoryResponse:
    category = db.execute(select(Category).filter(Category.id == id)).scalars().first()
    if category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    return category


@router.patch("/{id}", response_model=CategoryResponse)
async def update_category(
    id: int,
    cat: CategoryRequest,
    curr_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    category = db.execute(select(Category).filter(Category.id == id)).scalars().first()
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    try:
        category.name = cat.name
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Category exists")

    db.refresh(category)
    return category


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    id: int, curr_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    category_to_delete = db.execute(select(Category).filter(Category.id == id)).scalars().first()
    if category_to_delete is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    db.delete(category_to_delete)
    db.commit()
