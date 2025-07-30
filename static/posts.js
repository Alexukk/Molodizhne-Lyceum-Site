const PostsGetter = () => {
    // Используем console.log для отслеживания начала запроса
    console.log("Запрос данных постов...");

    fetch("./get-posts-data")
        .then((response) => {
            // Проверяем, успешен ли HTTP-ответ (статус 200-299)
            if (!response.ok) {
                // Если нет, выбрасываем ошибку, которая будет поймана в .catch()
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json(); // Парсим ответ как JSON
        })
        .then((data) => {
            console.log("Данные постов получены:", data);


            if (!Array.isArray(data)) {
                throw new Error("Полученные данные не являются массивом.");
            }

            const reversedPosts = [...data].reverse();
            let post_PAGE = '';

            reversedPosts.forEach(post => {
                post_PAGE += `<article class="col-md-6 mb-4">
                    <div class="card">
                      <div class="card-body">
                        <h5 class="card-title">${post.title || 'Без заголовка'}</h5>
                        <p class="card-text">${post.text || 'Без текста'}</p>
                        <hr>
                        <p class="card-text text-muted">${post.Date || 'Дата не указана'}</p>
                      </div>
                    </div>
                  </article>`;
            });


            const postsContainer = document.getElementById('posts_code');
            if (postsContainer) {
                postsContainer.innerHTML = post_PAGE;
            } else {
                console.error("Элемент с ID 'posts_code' не найден.");

                document.body.innerHTML = `<p style="color: red;">Ошибка: Контейнер для постов не найден на странице!</p>`;
            }
        })
        .catch((error) => {
            console.error("Ошибка при получении постов:", error);


            const errorContainer = document.getElementById('posts_code');
            if (errorContainer) {
                errorContainer.innerHTML = `<p style="color: red;">Не удалось загрузить посты с сервера. Пожалуйста, проверьте ваше соединение или свяжитесь с нами.</p>`;
            } else {

                document.body.innerHTML = `<p style="color: red;">Критическая ошибка: ${error.message}. Не удалось загрузить посты.</p>`;
            }
        });
};

// Запускаем PostsGetter после полной загрузки DOM
window.onload = () => {
    PostsGetter();
};

// Алтернативный вариант запуска, который может быть лучше в современных проектах
// document.addEventListener('DOMContentLoaded', PostsGetter);