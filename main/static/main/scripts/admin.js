document.addEventListener('DOMContentLoaded', function () {
    var categoryField = document.getElementById('id_category');
    var form = document.querySelector('form');

    // Сопоставление категорий с обязательными полями
    var categoryFields = {
        'monitor': ['fps'],
        'keyboard': ['switch_type', 'backlight'],
        'mouse': ['dpi', 'sensor_type'],
        'motherboard': ['socket_type', 'form_factor'],
        'ram': ['ram_type', 'ram_size'],
        'power-supply': ['power_wattage', 'certification'],
        'storage': ['storage_type', 'storage_size'],
        'cooling': ['cooling_type'],
        'graphics card': ['video_memory', 'ram_type'],
        'headphones': ['connection_type'],
        'mouse pad': ['mouse_pad_size'],
        'case': ['form_factor']
    };

    // Функция для показа/скрытия полей в зависимости от категории
    function toggleFields() {
        var selectedCategory = categoryField.options[categoryField.selectedIndex].text.toLowerCase();

        // Сначала скрываем все поля
        for (var fields of Object.values(categoryFields)) {
            fields.forEach(function (field) {
                var fieldRow = document.querySelector('.form-row.field-' + field);
                var fieldInput = document.getElementById('id_' + field);
                if (fieldRow) {
                    fieldRow.style.display = 'none';
                    fieldInput.required = false;  // Поля не обязательные по умолчанию
                }
            });
        }

        // Показываем и делаем обязательными только поля, соответствующие выбранной категории
        if (categoryFields[selectedCategory]) {
            categoryFields[selectedCategory].forEach(function (field) {
                var fieldRow = document.querySelector('.form-row.field-' + field);
                var fieldInput = document.getElementById('id_' + field);
                if (fieldRow) {
                    fieldRow.style.display = 'block';
                    fieldInput.required = true;  // Делаем поле обязательным
                }
            });
        }
    }

    // Проверка обязательных полей перед отправкой формы
    form.addEventListener('submit', function (event) {
        var selectedCategory = categoryField.options[categoryField.selectedIndex].text.toLowerCase();

        if (categoryFields[selectedCategory]) {
            var isValid = true;
            categoryFields[selectedCategory].forEach(function (field) {
                var fieldInput = document.getElementById('id_' + field);
                if (fieldInput && fieldInput.required && !fieldInput.value) {
                    isValid = false;
                }
            });
            if (!isValid) {
                event.preventDefault();  // Останавливаем отправку формы
                alert('Пожалуйста, заполните все обязательные поля для категории "' + selectedCategory + '".');
            }
        }
    });

    // Изначально скрываем или показываем поля в зависимости от выбранной категории
    toggleFields();

    // Добавляем обработчик события на изменение категории
    categoryField.addEventListener('change', toggleFields);
});
