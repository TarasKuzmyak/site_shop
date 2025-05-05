document.addEventListener("DOMContentLoaded", function () {
    const menuButton = document.getElementById("menu-button");
    const menuPopup = document.getElementById("popup-menu");
    const closeMenu = document.getElementById("close-menu");

    // Приховати меню на старті
    menuPopup.style.display = "none";

    menuButton.addEventListener("click", function () {
        if (menuPopup.style.display === "none") {
            menuPopup.style.display = "block"; // Відкрити меню
            console.log("Меню відкрито.");
        } else {
            menuPopup.style.display = "none"; // Закрити меню
            console.log("Меню приховано.");
        }
    });

    closeMenu.addEventListener("click", function () {
        menuPopup.style.display = "none"; // Закриття меню
        console.log("Меню закрито.");
    });
});