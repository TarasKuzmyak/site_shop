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

