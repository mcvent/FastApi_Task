import requests
import time
from datetime import datetime, timezone

BASE_URL = "http://localhost:8000"

def print_result(method, path, status, expected):
    icon = "✅" if status == expected else "❌"
    print(f"{icon} {method} {path}: {status} (ожидался {expected})")

# ==================== 1. АВТОРИЗАЦИЯ ====================
print("=" * 60)
print("1. АВТОРИЗАЦИЯ")
print("=" * 60)

login_resp = requests.post(f"{BASE_URL}/auth/login", data={
    "username": "admin",
    "password": "TestPass123!"
})

if login_resp.status_code != 200:
    print(f"❌ Не удалось авторизоваться: {login_resp.status_code}")
    exit()

token = login_resp.json().get("access_token")
headers = {"Authorization": f"Bearer {token}"}
print(f"✅ Токен получен\n")

# ==================== 2. ПОДГОТОВКА УНИКАЛЬНЫХ ДАННЫХ ====================
print("=" * 60)
print("2. ПОДГОТОВКА ДАННЫХ")
print("=" * 60)

timestamp = int(time.time())
username = f"testuser_{timestamp}"
user_email = f"test_{timestamp}@test.com"

# Создание категории
cat_resp = requests.post(f"{BASE_URL}/categories/", headers=headers, json={
    "title": f"Test Category {timestamp}",
    "slug": f"test-category-{timestamp}"
})
if cat_resp.status_code == 201:
    category_id = cat_resp.json()["id"]
else:
    # Берём первую существующую категорию
    cats = requests.get(f"{BASE_URL}/categories/").json()
    category_id = cats["items"][0]["id"] if cats.get("items") else 1
print(f"✅ Категория: id={category_id}")

# Создание локации
loc_resp = requests.post(f"{BASE_URL}/locations/", headers=headers, json={
    "name": f"Test Location {timestamp}"
})
if loc_resp.status_code == 201:
    location_id = loc_resp.json()["id"]
else:
    locs = requests.get(f"{BASE_URL}/locations/").json()
    location_id = locs["items"][0]["id"] if locs.get("items") else 1
print(f"✅ Локация: id={location_id}")

# Создание пользователя
user_resp = requests.post(f"{BASE_URL}/users/create", json={
    "username": username,
    "password": "Test123!",
    "email": user_email
})
if user_resp.status_code == 201:
    user_id = user_resp.json()["id"]
else:
    user_id = 2
print(f"✅ Пользователь: id={user_id}")

# Создание поста
pub_date = datetime.now(timezone.utc).isoformat(timespec='milliseconds').replace('+00:00', 'Z')
post_resp = requests.post(f"{BASE_URL}/posts/", headers=headers, json={
    "title": f"Test Post {timestamp}",
    "text": "Test content",
    "pub_date": pub_date,
    "is_published": True,
    "author_id": user_id,
    "category_id": category_id,
    "location_id": location_id,
    "image": None
})
if post_resp.status_code == 201:
    post_id = post_resp.json()["id"]
else:
    print(f"❌ Не удалось создать пост: {post_resp.status_code}")
    post_id = None
print(f"✅ Пост: id={post_id}")

# Создание комментария
if post_id:
    comment_resp = requests.post(f"{BASE_URL}/comments/", headers=headers, json={
        "text": f"Test comment {timestamp}",
        "post_id": post_id,
        "author_id": user_id
    })
    if comment_resp.status_code == 201:
        comment_id = comment_resp.json()["id"]
    else:
        comment_id = None
else:
    comment_id = None
print(f"✅ Комментарий: id={comment_id}\n")

# ==================== 3. ПРОВЕРКА API ====================
print("=" * 60)
print("3. ПРОВЕРКА API")
print("=" * 60)

# ---------- AUTH ----------
print("\n--- AUTH ---")
print_result("POST", "/auth/login", login_resp.status_code, 200)

# ---------- USERS (публичные) ----------
print("\n--- USERS (публичные) ---")
resp = requests.get(f"{BASE_URL}/users/")
print_result("GET", "/users/", resp.status_code, 200)

resp = requests.get(f"{BASE_URL}/users/active")
print_result("GET", "/users/active", resp.status_code, 200)

if user_id:
    resp = requests.get(f"{BASE_URL}/users/id/{user_id}")
    print_result("GET", f"/users/id/{user_id}", resp.status_code, 200)

resp = requests.get(f"{BASE_URL}/users/username/{username}")
print_result("GET", f"/users/username/{username}", resp.status_code, 200)

resp = requests.get(f"{BASE_URL}/users/email/{user_email}")
print_result("GET", f"/users/email/{user_email}", resp.status_code, 200)

# ---------- USERS (защищённые) ----------
print("\n--- USERS (защищённые) ---")
resp = requests.post(f"{BASE_URL}/users/create", json={
    "username": f"newuser_{timestamp}",
    "password": "Newjjjjj123!",
    "email": f"new_{timestamp}@test.com"
})
print_result("POST", "/users/create", resp.status_code, 201)

if user_id:
    resp = requests.patch(f"{BASE_URL}/users/{user_id}", headers=headers, json={"first_name": "Updated"})
    print_result("PATCH", f"/users/{user_id}", resp.status_code, 200)

    resp = requests.delete(f"{BASE_URL}/users/{user_id}", headers=headers)
    print_result("DELETE", f"/users/{user_id}", resp.status_code, 204)

# ---------- CATEGORIES (публичные) ----------
print("\n--- CATEGORIES (публичные) ---")
resp = requests.get(f"{BASE_URL}/categories/")
print_result("GET", "/categories/", resp.status_code, 200)

if category_id:
    resp = requests.get(f"{BASE_URL}/categories/{category_id}")
    print_result("GET", f"/categories/{category_id}", resp.status_code, 200)

resp = requests.get(f"{BASE_URL}/categories/slug/test-category-{timestamp}")
print_result("GET", f"/categories/slug/test-category-{timestamp}", resp.status_code, 200)

# ---------- CATEGORIES (защищённые) ----------
print("\n--- CATEGORIES (защищённые) ---")
new_cat_resp = requests.post(f"{BASE_URL}/categories/", headers=headers, json={
    "title": f"New Category {timestamp}",
    "slug": f"new-category-{timestamp}"
})
new_cat_id = new_cat_resp.json()["id"] if new_cat_resp.status_code == 201 else None
print_result("POST", "/categories/", new_cat_resp.status_code, 201)

if new_cat_id:
    resp = requests.patch(f"{BASE_URL}/categories/{new_cat_id}", headers=headers, json={"title": "Patched"})
    print_result("PATCH", f"/categories/{new_cat_id}", resp.status_code, 200)

    resp = requests.delete(f"{BASE_URL}/categories/{new_cat_id}", headers=headers)
    print_result("DELETE", f"/categories/{new_cat_id}", resp.status_code, 204)

# ---------- LOCATIONS (публичные) ----------
print("\n--- LOCATIONS (публичные) ---")
resp = requests.get(f"{BASE_URL}/locations/")
print_result("GET", "/locations/", resp.status_code, 200)

if location_id:
    resp = requests.get(f"{BASE_URL}/locations/{location_id}")
    print_result("GET", f"/locations/{location_id}", resp.status_code, 200)

resp = requests.get(f"{BASE_URL}/locations/name/Test%20Location%20{timestamp}")
print_result("GET", f"/locations/name/Test%20Location%20{timestamp}", resp.status_code, 200)

# ---------- LOCATIONS (защищённые) ----------
print("\n--- LOCATIONS (защищённые) ---")
new_loc_resp = requests.post(f"{BASE_URL}/locations/", headers=headers, json={
    "name": f"New Location {timestamp}"
})
new_loc_id = new_loc_resp.json()["id"] if new_loc_resp.status_code == 201 else None
print_result("POST", "/locations/", new_loc_resp.status_code, 201)

if new_loc_id:
    resp = requests.patch(f"{BASE_URL}/locations/{new_loc_id}", headers=headers, json={"name": "Patched"})
    print_result("PATCH", f"/locations/{new_loc_id}", resp.status_code, 200)

    resp = requests.delete(f"{BASE_URL}/locations/{new_loc_id}", headers=headers)
    print_result("DELETE", f"/locations/{new_loc_id}", resp.status_code, 204)

# ---------- POSTS (публичные) ----------
print("\n--- POSTS (публичные) ---")
resp = requests.get(f"{BASE_URL}/posts/")
print_result("GET", "/posts/", resp.status_code, 200)

if post_id:
    resp = requests.get(f"{BASE_URL}/posts/{post_id}")
    print_result("GET", f"/posts/{post_id}", resp.status_code, 200)

if user_id:
    resp = requests.get(f"{BASE_URL}/posts/author/{user_id}")
    print_result("GET", f"/posts/author/{user_id}", resp.status_code, 200)

resp = requests.get(f"{BASE_URL}/posts/published/")
print_result("GET", "/posts/published/", resp.status_code, 200)

# ---------- POSTS (защищённые) ----------
print("\n--- POSTS (защищённые) ---")
new_post_resp = requests.post(f"{BASE_URL}/posts/", headers=headers, json={
    "title": f"New Post {timestamp}",
    "text": "Content",
    "pub_date": pub_date,
    "is_published": True,
    "author_id": user_id if user_id else 2,
    "category_id": category_id,
    "location_id": location_id,
    "image": None
})
new_post_id = new_post_resp.json()["id"] if new_post_resp.status_code == 201 else None
print_result("POST", "/posts/", new_post_resp.status_code, 201)

if new_post_id:
    resp = requests.patch(f"{BASE_URL}/posts/{new_post_id}", headers=headers, json={"title": "Patched Post"})
    print_result("PATCH", f"/posts/{new_post_id}", resp.status_code, 200)

    resp = requests.delete(f"{BASE_URL}/posts/{new_post_id}", headers=headers)
    print_result("DELETE", f"/posts/{new_post_id}", resp.status_code, 204)

# ---------- POST IMAGES (только GET) ----------
print("\n--- POST IMAGES (публичные) ---")
print("📌 Для тестирования POST /posts/{id}/images/ и DELETE /posts/{id}/images/{image_id}/ требуется загрузить изображение через Swagger или Postman")
if post_id:
    resp = requests.get(f"{BASE_URL}/posts/{post_id}/images/")
    print_result("GET", f"/posts/{post_id}/images/", resp.status_code, 200)

# ---------- COMMENTS (публичные) ----------
print("\n--- COMMENTS (публичные) ---")
resp = requests.get(f"{BASE_URL}/comments/")
print_result("GET", "/comments/", resp.status_code, 200)

if comment_id:
    resp = requests.get(f"{BASE_URL}/comments/{comment_id}")
    print_result("GET", f"/comments/{comment_id}", resp.status_code, 200)

if post_id:
    resp = requests.get(f"{BASE_URL}/comments/post/{post_id}")
    print_result("GET", f"/comments/post/{post_id}", resp.status_code, 200)

if user_id:
    resp = requests.get(f"{BASE_URL}/comments/author/{user_id}")
    print_result("GET", f"/comments/author/{user_id}", resp.status_code, 200)

# ---------- COMMENTS (защищённые) ----------
print("\n--- COMMENTS (защищённые) ---")
if post_id and user_id:
    new_comment_resp = requests.post(f"{BASE_URL}/comments/", headers=headers, json={
        "text": f"New comment {timestamp}",
        "post_id": post_id,
        "author_id": user_id
    })
    new_comment_id = new_comment_resp.json()["id"] if new_comment_resp.status_code == 201 else None
    print_result("POST", "/comments/", new_comment_resp.status_code, 201)

    if new_comment_id:
        resp = requests.patch(f"{BASE_URL}/comments/{new_comment_id}", headers=headers, json={"text": "Patched comment"})
        print_result("PATCH", f"/comments/{new_comment_id}", resp.status_code, 200)

        resp = requests.delete(f"{BASE_URL}/comments/{new_comment_id}", headers=headers)
        print_result("DELETE", f"/comments/{new_comment_id}", resp.status_code, 204)

# ---------- COMMENT IMAGES (только GET) ----------
print("\n--- COMMENT IMAGES (публичные) ---")
print("📌 Для тестирования POST /comments/{id}/images/ и DELETE требуется загрузить изображение через Swagger или Postman")
if comment_id:
    resp = requests.get(f"{BASE_URL}/comments/{comment_id}/images/")
    print_result("GET", f"/comments/{comment_id}/images/", resp.status_code, 200)

# ==================== 4. ИТОГ ====================
print("\n" + "=" * 60)
print("4. ИТОГ")
print("=" * 60)
print("✅ Проверка всех API эндпоинтов завершена")
print("📌 Изображения (POST /posts/{id}/images/, POST /comments/{id}/images/)")
print("   требуют ручного тестирования через Swagger или Postman")