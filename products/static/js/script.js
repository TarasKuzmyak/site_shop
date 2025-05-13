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

document.addEventListener("DOMContentLoaded", function () {
    const tabs = document.querySelectorAll(".nav-link");
    const content = document.querySelectorAll(".tab-pane");

    tabs.forEach(tab => {
        tab.addEventListener("click", function (event) {
            event.preventDefault();
            tabs.forEach(t => t.classList.remove("active"));
            this.classList.add("active");

            const target = this.id.replace("-tab", "");
            content.forEach(c => c.classList.remove("show", "active"));
            document.getElementById(target).classList.add("show", "active");
        });
    });
});

<script>
    document.addEventListener("DOMContentLoaded", function () {
        document.getElementById("openRegisterModal").addEventListener("click", function () {
            var loginModal = new bootstrap.Modal(document.getElementById("loginModal"));
            var registerModal = new bootstrap.Modal(document.getElementById("registerModal"));

            loginModal.hide(); // Закриваємо модальне вікно входу
            registerModal.show(); // Відкриваємо модальне вікно реєстрації
        });
});
</script>