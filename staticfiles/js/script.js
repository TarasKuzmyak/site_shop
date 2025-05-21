document.addEventListener("DOMContentLoaded", function () {
    const menuButton = document.getElementById("menu-button");
    const closeMenuButton = document.getElementById("close-menu");
    const popupMenu = document.getElementById("popup-menu");

    menuButton.addEventListener("click", function () {
        popupMenu.classList.remove("hidden"); // 🔹 Відображаємо меню
    });

    closeMenuButton.addEventListener("click", function () {
        popupMenu.classList.add("hidden"); // 🔹 Закриваємо меню
    });
});

// Відкриття модального вікна реєстрації при натисканні "Зареєструватися"
document.getElementById("openRegisterModal").addEventListener("click", function () {
    var loginModalEl = document.getElementById("loginModal");
    var registerModalEl = document.getElementById("registerModal");

    var loginModal = bootstrap.Modal.getInstance(loginModalEl);
    if (loginModal) {
        loginModal.hide();
    }

    var registerModal = new bootstrap.Modal(registerModalEl);
    registerModal.show();
});

// Обробка форми входу
document.getElementById("login-form").addEventListener("submit", function (event) {
    event.preventDefault();

    const formData = new FormData(this);
    const csrfToken = document.querySelector("[name=csrfmiddlewaretoken]").value;
    formData.append("csrfmiddlewaretoken", csrfToken);

    fetch("/login/", {
        method: "POST",
        headers: { "X-CSRFToken": csrfToken },
        body: formData,
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                window.location.href = data.redirect_url;
            } else {
                console.error("❌ Помилка входу:", data.errors);
            }
        })
        .catch(error => console.error("❌ Помилка запиту:", error));
});

// Обробка форми реєстрації
document.getElementById("register-form").addEventListener("submit", function (event) {
    event.preventDefault();

    const formData = new FormData(this);
    const csrfToken = document.querySelector("[name=csrfmiddlewaretoken]").value;
    formData.append("csrfmiddlewaretoken", csrfToken);

    fetch("/registration/", {
        method: "POST",
        headers: { "X-CSRFToken": csrfToken },
        body: formData,
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                window.location.href = data.redirect_url;
            } else {
                console.error("❌ Помилка реєстрації:", data.errors);
            }
        })
        .catch(error => console.error("❌ Помилка запиту:", error));
});
