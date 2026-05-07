from uuid import UUID
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.services.user_service import user_service

router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "/",
    response_model=list[UserResponse],
    summary="Listar todos los usuarios",
    description="Retorna una lista paginada de todos los usuarios registrados.",
)
def list_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return user_service.get_all_users(db, skip=skip, limit=limit)


@router.post(
    "/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un usuario",
    description="Crea un nuevo usuario. El username y el email deben ser únicos.",
)
def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    return user_service.create_user(db, user_data)


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Obtener un usuario por ID",
    description="Retorna los datos de un usuario específico dado su UUID.",
)
def get_user(user_id: UUID, db: Session = Depends(get_db)):
    return user_service.get_user(db, user_id)


@router.put(
    "/{user_id}",
    response_model=UserResponse,
    summary="Actualizar un usuario",
    description="Actualiza parcialmente los campos de un usuario. Solo se actualizan los campos enviados.",
)
def update_user(user_id: UUID, user_data: UserUpdate, db: Session = Depends(get_db)):
    return user_service.update_user(db, user_id, user_data)


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar un usuario",
    description="Elimina permanentemente un usuario por su UUID.",
)
def delete_user(user_id: UUID, db: Session = Depends(get_db)):
    user_service.delete_user(db, user_id)
