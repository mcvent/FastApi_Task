from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession
from typing import AsyncIterable

from src.infrastructure.postgres.database import database
from src.infrastructure.postgres.repositories.posts import PostRepository
from src.infrastructure.postgres.repositories.comments import CommentRepository
from src.infrastructure.postgres.repositories.categories import CategoryRepository
from src.infrastructure.postgres.repositories.locations import LocationRepository
from src.infrastructure.postgres.repositories.users import UserRepository
from src.infrastructure.postgres.repositories.post_image import PostImageRepository
from src.infrastructure.postgres.repositories.comment_image import CommentImageRepository

from src.domain.posts.use_cases.create_post import CreatePostUseCase
from src.domain.posts.use_cases.update_post import UpdatePostUseCase
from src.domain.posts.use_cases.delete_post import DeletePostUseCase
from src.domain.posts.use_cases.get_post import GetPostUseCase
from src.domain.posts.use_cases.add_post_image import AddPostImageUseCase
from src.domain.posts.use_cases.get_post_image import GetPostImageUseCase
from src.domain.posts.use_cases.delete_post_image import DeletePostImageUseCase

from src.domain.comments.use_cases.create_comment import CreateCommentUseCase
from src.domain.comments.use_cases.update_comment import UpdateCommentUseCase
from src.domain.comments.use_cases.delete_comment import DeleteCommentUseCase
from src.domain.comments.use_cases.get_comment import GetCommentUseCase
from src.domain.comments.use_cases.add_comment_image import AddCommentImageUseCase
from src.domain.comments.use_cases.get_comment_images import GetCommentImagesUseCase
from src.domain.comments.use_cases.delete_comment_image import DeleteCommentImageUseCase

from src.domain.categories.use_cases.create_category import CreateCategoryUseCase
from src.domain.categories.use_cases.update_category import UpdateCategoryUseCase
from src.domain.categories.use_cases.delete_category import DeleteCategoryUseCase
from src.domain.categories.use_cases.get_category import GetCategoryUseCase

from src.domain.locations.use_cases.create_location import CreateLocationUseCase
from src.domain.locations.use_cases.update_location import UpdateLocationUseCase
from src.domain.locations.use_cases.delete_location import DeleteLocationUseCase
from src.domain.locations.use_cases.get_location import GetLocationUseCase

from src.domain.users.use_cases.create_user import CreateUserUseCase
from src.domain.users.use_cases.update_user import UpdateUserUseCase
from src.domain.users.use_cases.delete_user import DeleteUserUseCase
from src.domain.users.use_cases.get_user import GetUserUseCase


class AppProvider(Provider):
    """Dishka провайдер для всех зависимостей приложения"""

    # Сессия БД
    @provide(scope=Scope.REQUEST)
    async def get_db_session(self) -> AsyncIterable[AsyncSession]:
        async with database.session() as session:
            yield session

    # ========== Репозитории (НЕ зависят от session) ==========
    @provide(scope=Scope.REQUEST)
    def get_post_repo(self) -> PostRepository:
        return PostRepository()

    @provide(scope=Scope.REQUEST)
    def get_comment_repo(self) -> CommentRepository:
        return CommentRepository()

    @provide(scope=Scope.REQUEST)
    def get_category_repo(self) -> CategoryRepository:
        return CategoryRepository()

    @provide(scope=Scope.REQUEST)
    def get_location_repo(self) -> LocationRepository:
        return LocationRepository()

    @provide(scope=Scope.REQUEST)
    def get_user_repo(self) -> UserRepository:
        return UserRepository()

    @provide(scope=Scope.REQUEST)
    def get_post_image_repo(self) -> PostImageRepository:
        return PostImageRepository()

    @provide(scope=Scope.REQUEST)
    def get_comment_image_repo(self) -> CommentImageRepository:
        return CommentImageRepository()

    # ========== Use Cases (Posts) ==========
    # CREATE/UPDATE/DELETE — нужна session
    @provide(scope=Scope.REQUEST)
    def get_create_post_uc(
        self, session: AsyncSession, repo: PostRepository,
        user_repo: UserRepository, category_repo: CategoryRepository,
        location_repo: LocationRepository
    ) -> CreatePostUseCase:
        return CreatePostUseCase(session, repo, user_repo, category_repo, location_repo)

    @provide(scope=Scope.REQUEST)
    def get_update_post_uc(
        self, session: AsyncSession, repo: PostRepository,
        category_repo: CategoryRepository, location_repo: LocationRepository
    ) -> UpdatePostUseCase:
        return UpdatePostUseCase(session, repo, category_repo, location_repo)

    @provide(scope=Scope.REQUEST)
    def get_delete_post_uc(
        self, session: AsyncSession, repo: PostRepository, comment_repo: CommentRepository
    ) -> DeletePostUseCase:
        return DeletePostUseCase(session, repo, comment_repo)

    # GET — НЕ нужна session
    @provide(scope=Scope.REQUEST)
    def get_get_post_uc(self, repo: PostRepository) -> GetPostUseCase:
        return GetPostUseCase(repo)

    # CREATE/UPDATE/DELETE для изображений — нужна session
    @provide(scope=Scope.REQUEST)
    def get_add_post_image_uc(
        self, session: AsyncSession, post_repo: PostRepository, image_repo: PostImageRepository
    ) -> AddPostImageUseCase:
        return AddPostImageUseCase(session, post_repo, image_repo)

    @provide(scope=Scope.REQUEST)
    def get_delete_post_image_uc(
        self, session: AsyncSession, post_repo: PostRepository, image_repo: PostImageRepository
    ) -> DeletePostImageUseCase:
        return DeletePostImageUseCase(session, post_repo, image_repo)

    # GET для изображений — НЕ нужна session
    @provide(scope=Scope.REQUEST)
    def get_get_post_image_uc(
        self, post_repo: PostRepository, image_repo: PostImageRepository
    ) -> GetPostImageUseCase:
        return GetPostImageUseCase(post_repo, image_repo)

    # ========== Use Cases (Comments) ==========
    @provide(scope=Scope.REQUEST)
    def get_create_comment_uc(
        self, session: AsyncSession, repo: CommentRepository,
        user_repo: UserRepository, post_repo: PostRepository
    ) -> CreateCommentUseCase:
        return CreateCommentUseCase(session, repo, user_repo, post_repo)

    @provide(scope=Scope.REQUEST)
    def get_update_comment_uc(
        self, session: AsyncSession, repo: CommentRepository
    ) -> UpdateCommentUseCase:
        return UpdateCommentUseCase(session, repo)

    @provide(scope=Scope.REQUEST)
    def get_delete_comment_uc(
        self, session: AsyncSession, repo: CommentRepository
    ) -> DeleteCommentUseCase:
        return DeleteCommentUseCase(session, repo)

    @provide(scope=Scope.REQUEST)
    def get_get_comment_uc(self, repo: CommentRepository) -> GetCommentUseCase:
        return GetCommentUseCase(repo)

    @provide(scope=Scope.REQUEST)
    def get_add_comment_image_uc(
        self, session: AsyncSession, comment_repo: CommentRepository, image_repo: CommentImageRepository
    ) -> AddCommentImageUseCase:
        return AddCommentImageUseCase(session, comment_repo, image_repo)

    @provide(scope=Scope.REQUEST)
    def get_delete_comment_image_uc(
        self, session: AsyncSession, comment_repo: CommentRepository, image_repo: CommentImageRepository
    ) -> DeleteCommentImageUseCase:
        return DeleteCommentImageUseCase(session, comment_repo, image_repo)

    # GET для изображений комментариев — НЕ нужна session
    @provide(scope=Scope.REQUEST)
    def get_get_comment_images_uc(
        self, comment_repo: CommentRepository, image_repo: CommentImageRepository
    ) -> GetCommentImagesUseCase:
        return GetCommentImagesUseCase(comment_repo, image_repo)

    # ========== Use Cases (Categories) ==========
    @provide(scope=Scope.REQUEST)
    def get_create_category_uc(
        self, session: AsyncSession, repo: CategoryRepository
    ) -> CreateCategoryUseCase:
        return CreateCategoryUseCase(session, repo)

    @provide(scope=Scope.REQUEST)
    def get_update_category_uc(
        self, session: AsyncSession, repo: CategoryRepository
    ) -> UpdateCategoryUseCase:
        return UpdateCategoryUseCase(session, repo)

    @provide(scope=Scope.REQUEST)
    def get_delete_category_uc(
        self, session: AsyncSession, repo: CategoryRepository
    ) -> DeleteCategoryUseCase:
        return DeleteCategoryUseCase(session, repo)

    @provide(scope=Scope.REQUEST)
    def get_get_category_uc(self, repo: CategoryRepository) -> GetCategoryUseCase:
        return GetCategoryUseCase(repo)

    # ========== Use Cases (Locations) ==========
    @provide(scope=Scope.REQUEST)
    def get_create_location_uc(
        self, session: AsyncSession, repo: LocationRepository
    ) -> CreateLocationUseCase:
        return CreateLocationUseCase(session, repo)

    @provide(scope=Scope.REQUEST)
    def get_update_location_uc(
        self, session: AsyncSession, repo: LocationRepository
    ) -> UpdateLocationUseCase:
        return UpdateLocationUseCase(session, repo)

    @provide(scope=Scope.REQUEST)
    def get_delete_location_uc(
        self, session: AsyncSession, repo: LocationRepository
    ) -> DeleteLocationUseCase:
        return DeleteLocationUseCase(session, repo)

    @provide(scope=Scope.REQUEST)
    def get_get_location_uc(self, repo: LocationRepository) -> GetLocationUseCase:
        return GetLocationUseCase(repo)

    # ========== Use Cases (Users) ==========
    @provide(scope=Scope.REQUEST)
    def get_create_user_uc(
        self, session: AsyncSession, repo: UserRepository
    ) -> CreateUserUseCase:
        return CreateUserUseCase(session, repo)

    @provide(scope=Scope.REQUEST)
    def get_update_user_uc(
        self, session: AsyncSession, repo: UserRepository
    ) -> UpdateUserUseCase:
        return UpdateUserUseCase(session, repo)

    @provide(scope=Scope.REQUEST)
    def get_delete_user_uc(
        self, session: AsyncSession, repo: UserRepository
    ) -> DeleteUserUseCase:
        return DeleteUserUseCase(session, repo)

    @provide(scope=Scope.REQUEST)
    def get_get_user_uc(self, repo: UserRepository) -> GetUserUseCase:
        return GetUserUseCase(repo)