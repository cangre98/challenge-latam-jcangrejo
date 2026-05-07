from uuid import UUID
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.repositories.user_repository import user_repository
from app.core.logging import logger


class UserService:

    def get_user(self, db: Session, user_id: UUID) -> User:
        user = user_repository.get_by_id(db, user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Usuario con id '{user_id}' no encontrado")
        return user

    def get_all_users(self, db: Session, skip: int = 0, limit: int = 100) -> list[User]:
        return user_repository.get_all(db, skip=skip, limit=limit)

    def create_user(self, db: Session, user_data: UserCreate) -> User:
        if user_repository.get_by_username(db, user_data.username):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"El username '{user_data.username}' ya está en uso")
        if user_repository.get_by_email(db, user_data.email):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"El email '{user_data.email}' ya está en uso")
        user = user_repository.create(db, user_data)
        logger.info(f"Usuario creado: {user.username} (id={user.id})")
        return user

    def update_user(self, db: Session, user_id: UUID, user_data: UserUpdate) -> User:
        user = self.get_user(db, user_id)
        if user_data.username and user_data.username != user.username:
            if user_repository.get_by_username(db, user_data.username):
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"El username '{user_data.username}' ya está en uso")
        if user_data.email and user_data.email != user.email:
            if user_repository.get_by_email(db, user_data.email):
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"El email '{user_data.email}' ya está en uso")
        user = user_repository.update(db, user, user_data)
        logger.info(f"Usuario actualizado: {user.username} (id={user.id})")
        return user

    def delete_user(self, db: Session, user_id: UUID) -> None:
        user = self.get_user(db, user_id)
        user_repository.delete(db, user)
        logger.info(f"Usuario eliminado: {user.username} (id={user_id})")


user_service = UserService()
