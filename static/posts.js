const PostsGetter = () => {
    console.log("Запит даних оголошень...");

    fetch("./get-posts-data")
        .then((response) => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then((posts) => {
            console.log("Отримані дані оголошень:", posts);

            if (!Array.isArray(posts)) {
                throw new Error("Отримані дані не є масивом.");
            }

            // Ми отримаємо список постів з бази даних
            let post_PAGE = '';

        posts.forEach(post => {
            post_PAGE += `
                <div class="col-md-6 mb-4">
                    <div class="card bg-dark text-white border-warning">
                        <div class="card-body">
                            <h5 class="card-title text-warning">${post.title || 'Без заголовка'}</h5>
                            <p class="card-text">${post.text || 'Без тексту'}</p>
                            <hr>
                            <p class="card-text text-muted">
                                <small>ID: ${post.id} | Дата публікації: ${post.date || 'Дата не вказана'}</small>
                            </p>
                        </div>
                    </div>
                </div>`;
            });

            const postsContainer = document.getElementById('posts_code');
            if (postsContainer) {
                postsContainer.innerHTML = post_PAGE;
            } else {
                console.error("Елемент з ID 'posts_code' не знайдено.");
            }
        })
        .catch((error) => {
            console.error("Помилка при отриманні оголошень:", error);

            const errorContainer = document.getElementById('posts_code');
            if (errorContainer) {
                errorContainer.innerHTML = `<p style="color: red;">Виникла помилка при завантаженні оголошень. Перевірте ваше підключення до інтернету.</p>`;
            } else {
                document.body.innerHTML = `<p style="color: red;">Виникла критична помилка.</p>`;
            }
        });
};

window.onload = () => {
    PostsGetter();
};