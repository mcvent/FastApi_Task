from locust import HttpUser, task, between
import random


class FastAPIUser(HttpUser):
    wait_time = between(0.5, 2)
    host = "http://127.0.0.1:8000"

    def on_start(self):
        self.username = f"loadtest_{random.randint(1, 100000)}"
        self.password = "LoadTest123!"
        self.my_posts = []
        self.user_id = None

        # Регистрация
        reg_response = self.client.post("/users/create", json={
            "username": self.username,
            "password": self.password,
            "email": f"{self.username}@test.com"
        })

        if reg_response.status_code == 201:
            self.user_id = reg_response.json().get("id")

        # Логин
        login_response = self.client.post("/auth/login",
                                          data={
                                              "username": self.username,
                                              "password": self.password
                                          },
                                          headers={"Content-Type": "application/x-www-form-urlencoded"}
                                          )

        if login_response.status_code == 200:
            self.token = login_response.json().get("access_token")
            self.headers = {"Authorization": f"Bearer {self.token}"}
            print(f"✅ {self.username} (id={self.user_id}) авторизован")
        else:
            self.token = None
            self.headers = {}
    # ========== GET эндпоинты (не требуют авторизации) ==========

    @task(3)  # вес 3 — чаще других
    def get_posts(self):
        """GET /posts/ — список постов"""
        self.client.get("/posts/", headers=self.headers)

    @task(2)
    def get_post_detail(self):
        """GET /posts/{id} — детальный пост (ID от 1 до 50)"""
        post_id = random.randint(31, 36)
        self.client.get(f"/posts/{post_id}", headers=self.headers)

    @task(2)
    def get_users(self):
        """GET /users/ — список пользователей"""
        self.client.get("/users/", headers=self.headers)

    @task(2)
    def get_user_detail(self):
        """GET /users/id/{id} — детально о пользователе"""
        user_id = random.randint(6, 20)
        self.client.get(f"/users/id/{user_id}", headers=self.headers)

    @task(1)
    def get_posts_by_category(self):
        """GET /categories/slug/{slug} — посты категории"""
        slugs = ["technology", "science", "art", "sports", "music"]
        slug = random.choice(slugs)
        self.client.get(f"/categories/slug/{slug}", headers=self.headers)

    @task(1)
    def get_posts_by_author(self):
        """GET /posts/author/{id} — посты пользователя"""
        author_id = random.randint(5, 25)
        self.client.get(f"/posts/author/{author_id}?skip=0&limit=10", headers=self.headers)

    # ========== POST эндпоинты (требуют токен) ==========

    @task(1)
    def create_post(self):
        if not self.token:
            return

        data = {
            "title": f"Load test post {random.randint(1, 10000)}",
            "text": "This is a test post. " * 10,
            "pub_date": "2025-05-19T12:00:00",
            "is_published": True,
            "author_id": self.user_id,
            "category_id": random.choice([1, 2, 3, None]),
            "location_id": random.choice([1, 2, 3, None])
        }
        response = self.client.post("/posts/", json=data, headers=self.headers)

        if response.status_code == 201:
            post_id = response.json().get("id")
            if post_id:
                self.my_posts.append(post_id)

    @task(1)
    def create_comment(self):
        """POST /comments/ — создание комментария"""
        if not self.token:
            return

        post_id = random.randint(31, 36)
        data = {
            "text": f"Test comment {random.randint(1, 10000)}",
            "post_id": post_id,
            "author_id": self.user_id
        }
        response = self.client.post("/comments/",
                                    json=data,
                                    headers=self.headers)

        if response.status_code != 201:
            print(f"❌ Ошибка создания комментария: {response.status_code} - {response.text}")

    @task(1)
    def register_user(self):
        """POST /users/create — регистрация нового пользователя"""
        random_suffix = random.randint(1, 100000)
        data = {
            "username": f"newuser_{random_suffix}",
            "password": "NewUser123!",
            "email": f"user_{random_suffix}@test.com"
        }
        self.client.post("/users/create", json=data)

    # @task(1)
    # def delete_my_post(self):
    #     """DELETE /posts/{id} — удаление своего поста"""
    #     if not self.token or not self.my_posts:
    #         return
    #
    #     post_id = self.my_posts.pop()
    #     self.client.delete(f"/posts/{post_id}", headers=self.headers)


class FastAPIAdminUser(HttpUser):
    wait_time = between(0.5, 2)
    host = "http://127.0.0.1:8000"

    def on_start(self):
        self.username = "admin"
        self.password = "TestPass123!"
        self.user_id = 2
        self.my_posts = []

        login_response = self.client.post("/auth/login",
                                          data={
                                              "username": self.username,
                                              "password": self.password
                                          },
                                          headers={"Content-Type": "application/x-www-form-urlencoded"}
                                          )

        if login_response.status_code == 200:
            self.token = login_response.json().get("access_token")
            self.headers = {"Authorization": f"Bearer {self.token}"}
            print(f"✅ Админ {self.username} (id={self.user_id}) авторизован")
        else:
            self.token = None
            self.headers = {}
            print(f"❌ Ошибка авторизации админа: {login_response.status_code}")

    @task(3)
    def get_posts(self):
        self.client.get("/posts/", headers=self.headers)

    @task(2)
    def get_users(self):
        self.client.get("/users/", headers=self.headers)

    @task(1)
    def get_categories(self):
        self.client.get("/categories/", headers=self.headers)

    @task(1)
    def get_locations(self):
        self.client.get("/locations/", headers=self.headers)