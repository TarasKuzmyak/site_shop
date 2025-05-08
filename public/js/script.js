// Отримуємо елементи
const menuButton = document.getElementById('menu-button');
const popupMenu = document.getElementById('popup-menu');
const closeMenu = document.getElementById('close-menu');

// Відкриваємо меню
menuButton.addEventListener('click', () => {
    popupMenu.classList.remove('hidden');
});

// Закриваємо меню
closeMenu.addEventListener('click', () => {
    popupMenu.classList.add('hidden');
});

// + and -
function increaseQuantity(button) {
    let input = button.previousElementSibling; // Отримати поле вводу
    input.value = parseInt(input.value) + 1; // Збільшити значення
}

function decreaseQuantity(button) {
    let input = button.nextElementSibling; // Отримати поле вводу
    if (parseInt(input.value) > 1) {
        input.value = parseInt(input.value) - 1; // Зменшити значення, якщо більше 1
    }
}
