from fastapi import APIRouter, status, HTTPException
from src.schemas.posts import Post
from src.schemas.users import User

posts_db = []
post_counter = 1
users_db = []
user_counter = 1


router = APIRouter()


@router.get("/hello_world", status_code=status.HTTP_200_OK)
async def get_hello_world() -> dict:
    response = {"text": "Hello, World!"}

    return response


@router.post("/posts", status_code=status.HTTP_201_CREATED)
async def create_post(post: Post) -> dict:
    global post_counter

    if len(post.title) < 10:
        raise HTTPException(
            detail="Название поста должно быть не меньше 10 символов",
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        )

    # Привязываем к id и в бд
    post_dict = post.dict()
    post_dict["id"] = post_counter
    post_counter += 1
    posts_db.append(post_dict)

    response = {
        "title": post.title,
        "text": post.text,
        "author_id": post.author_id,
        "pub_date": post.pub_date,
        "location_id": post.location_id,
        "category_id": post.category_id,
        "id": post_dict["id"]
    }

    return response


@router.get("/posts/{post_id}", status_code=status.HTTP_200_OK)
async def get_post(post_id: int) -> dict:
    for post in posts_db:
        if post["id"] == post_id:
            return post

    # Если поста нет
    raise HTTPException(
        detail=f"Пост с id {post_id} не найден",
        status_code=status.HTTP_404_NOT_FOUND,
    )


@router.delete("/posts/{post_id}", status_code=status.HTTP_200_OK)
async def delete_post(post_id: int) -> dict:
    for i, post in enumerate(posts_db):
        if post["id"] == post_id:
            # Удаляем ненужный пост
            deleted_post = posts_db.pop(i)

            return {
                "message": "Пост удален",
                "deleted_post": deleted_post
            }

    raise HTTPException(
        detail=f"Пост с id {post_id} не найден",
        status_code=status.HTTP_404_NOT_FOUND,
    )


@router.put("/posts/{post_id}", status_code=status.HTTP_200_OK)
async def update_post(post_id: int, updated_post: Post) -> dict:
    # Ищем пост
    for i, post in enumerate(posts_db):
        if post["id"] == post_id:
            if len(updated_post.title) < 10:
                raise HTTPException(
                    detail="Название поста должно быть не меньше 10 символов",
                    status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                )

            # Обновляем все поля
            updated_data = updated_post.dict()
            updated_data["id"] = post_id  # сохраняем тот же id
            posts_db[i] = updated_data

            return updated_data

    raise HTTPException(
        detail=f"Пост с id {post_id} не найден",
        status_code=status.HTTP_404_NOT_FOUND,
    )


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_user(user: User) -> dict:
    global user_counter

    # Проверяем email
    for existing_user in users_db:
        if existing_user["email"] == user.email:
            raise HTTPException(
                detail="Пользователь с таким email уже существует",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

    user_password = user.password.get_secret_value()
    # Привязываем к id и сохраняем в бд
    user_dict = user.dict()
    user_dict["user_id"] = user_counter

    # Сохраняем пароль отдельно
    user_dict["password"] = user_password

    users_db.append(user_dict)
    user_counter += 1

    response = {
        "username": user.username,
        "user_id": user_dict["user_id"],
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "password": user.password
    }

    return response


@router.get("/users/{user_id}", response_model=User)
async def get_user(user_id: int):
    # Ищем пользователя в списке
    for user in users_db:
        if user["user_id"] == user_id:
            return user

    # Если не нашли
    raise HTTPException(
        detail=f"Пользователь с id {user_id} не найден",
        status_code=status.HTTP_404_NOT_FOUND,
    )
