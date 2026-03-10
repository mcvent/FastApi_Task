from fastapi import HTTPException, status
from src.infrastructure.sqlite.database import database
from src.infrastructure.sqlite.repositories.posts import PostRepository
from src.infrastructure.sqlite.repositories.users import UserRepository
from src.infrastructure.sqlite.repositories.categories import CategoryRepository
from src.infrastructure.sqlite.repositories.locations import LocationRepository
from src.schemas.posts import PostResponse, PostCreate
from datetime import datetime


class CreatePostUseCase:
    def __init__(self):
        self._database = database
        self._repo = PostRepository()
        self._user_repo = UserRepository()
        self._category_repo = CategoryRepository()
        self._location_repo = LocationRepository()

    async def execute(self, post_data: PostCreate) -> PostResponse:
        """Создать новый пост"""
        try:
            with self._database.session() as session:
                # Проверяем существование автора
                author = self._user_repo.get_by_id(session, post_data.author_id)
                if not author:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Автор с ID {post_data.author_id} не найден"
                    )

                #Проверяем существование категории (если указана)
                if post_data.category_id:
                    category = self._category_repo.get_by_id(session, post_data.category_id)
                    if not category:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Категория с ID {post_data.category_id} не найдена"
                        )

                # Проверяем существование локации (если указана)
                if post_data.location_id:
                    location = self._location_repo.get_by_id(session, post_data.location_id)
                    if not location:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Локация с ID {post_data.location_id} не найдена"
                        )

                # Создаем пост
                # Конвертация в dict + добавление created_at
                post_dict = post_data.model_dump()
                post_dict["created_at"] = datetime.now()

                # Создаём пост (передаём dict, не Pydantic!)
                new_post = self._repo.create(session, post_dict)
                session.commit()  # Фиксируем транзакцию

                return PostResponse.model_validate(new_post)

        except HTTPException:
            raise
        except Exception as e:
            print(f"Ошибка при создании поста: {e}")
            raise