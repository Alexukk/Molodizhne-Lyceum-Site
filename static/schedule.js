document.addEventListener('DOMContentLoaded', function() {
  const linkMap = {
    'Elementary': 'Elementary_code',
    'Secondary': 'Seconadary_code',
    'High': 'High_code'
  };

  fetch('/get-schedule')
    .then(response => {
      if (!response.ok) {
        throw new Error(`Network response was not ok, status: ${response.status}`);
      }
      return response.json();
    })
    .then(data => {
      console.log("Данные расписания получены:", data);

      if (Object.keys(data).length === 0) {
        console.log("Получены пустые данные расписания.");
        const links = document.querySelectorAll('.card-button');
        links.forEach(link => {
          link.href = '#';
          link.innerHTML = 'Розклад відсутній';
          link.style.pointerEvents = 'none';
          link.style.opacity = '0.5';
        });
        return;
      }

      for (const scheduleType in linkMap) {
        const elementId = linkMap[scheduleType];
        const link = data[scheduleType];

        const element = document.getElementById(elementId);
        if (element && link) {
          element.href = link;
          element.innerHTML = 'Перейти до розкладу';
          element.style.pointerEvents = 'auto';
          element.style.opacity = '1';
        } else if (element) {
          element.href = '#';
          element.innerHTML = 'Розклад відсутній';
          element.style.pointerEvents = 'none';
          element.style.opacity = '0.5';
        }
      }
    })
    .catch(error => {
      console.error('There has been a problem with your fetch operation:', error);
      const links = document.querySelectorAll('.card-button');
      links.forEach(link => {
        link.href = '#';
        link.innerHTML = 'Помилка завантаження';
        link.style.pointerEvents = 'none';
        link.style.opacity = '0.5';
      });
    });
});