document.addEventListener("DOMContentLoaded", function () {
    const menuButton = document.getElementById("menu-button");
    const closeButton = document.getElementById("close-menu");
    const popupMenu = document.getElementById("popup-menu");

    menuButton.addEventListener("click", function () {
        popupMenu.classList.toggle("hidden");
    });

    closeButton.addEventListener("click", function () {
        popupMenu.classList.add("hidden");
    });
});