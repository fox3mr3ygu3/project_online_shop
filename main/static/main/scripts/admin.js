document.addEventListener('DOMContentLoaded', function() {
    var categoryField = document.getElementById('id_category');
    var fpsField = document.querySelector('.form-row.field-fps');
    var fpsInput = document.getElementById('id_fps');
    var form = document.querySelector('form');

    function toggleFPSField() {
        var selectedCategory = categoryField.options[categoryField.selectedIndex].text.toLowerCase();
        if (selectedCategory === 'monitor') {
            fpsField.style.display = 'block';  // Показываем поле FPS
            fpsInput.required = true;  // Делаем поле обязательным
        } else {
            fpsField.style.display = 'none';  // Скрываем поле FPS
            fpsInput.required = false;  // Снимаем обязательность
        }
    }

    // Проверяем перед отправкой формы
    form.addEventListener('submit', function(event) {
        var selectedCategory = categoryField.options[categoryField.selectedIndex].text.toLowerCase();
        if (selectedCategory === 'monitor' && !fpsInput.value) {
            event.preventDefault();  // Останавливаем отправку формы
            alert('Поле FPS обязательно для категории "monitor".');  // Показываем уведомление
        }
    });

    // Изначально скрываем или показываем поле в зависимости от выбранной категории
    toggleFPSField();

    // Добавляем обработчик события на изменение категории
    categoryField.addEventListener('change', toggleFPSField);
});