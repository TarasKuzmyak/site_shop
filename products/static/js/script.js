function getCart() {
    return JSON.parse(localStorage.getItem("cart")) || [];
}

function updateCartUI() {
    console.log("🔹 Оновлюємо кошик...");

    const cartItemsContainer = document.getElementById("cart-items");
    const cartCountElement = document.querySelector(".cart-count");
    const cart = getCart();

    if (cartCountElement) {
        // Показуємо загальну кількість товарів у кошику
        cartCountElement.innerText = cart.length;
    }

    if (cartItemsContainer) {
        cartItemsContainer.innerHTML = "";

        if (cart.length === 0) {
            cartItemsContainer.innerHTML = "<p>🚨 Кошик порожній!</p>";
        } else {
            cart.forEach(product => {
                const item = document.createElement("li");
                item.classList.add("list-group-item", "d-flex", "justify-content-between", "align-items-center");

                item.innerHTML = `
                    <div>
                        <strong>${product.name}</strong> - ${product.price} грн
                    </div>
                    <button class="btn btn-danger btn-sm remove-from-cart" data-id="${product.id}">Видалити</button>
                `;

                cartItemsContainer.appendChild(item);
            });

            // Підписуємося на кнопки "Видалити"
            document.querySelectorAll(".remove-from-cart").forEach(button => {
                button.addEventListener("click", function () {
                    const productId = this.dataset.id;
                    let cart = getCart();
                    // Видаляємо товар за id
                    cart = cart.filter(item => item.id !== productId);
                    localStorage.setItem("cart", JSON.stringify(cart));
                    updateCartUI();
                });
            });
        }
    }
}

document.addEventListener("DOMContentLoaded", function () {
    updateCartUI();

    // Додаємо товари у кошик
    document.querySelectorAll(".add-to-cart").forEach(button => {
        button.addEventListener("click", function () {
            const product = {
                id: this.dataset.id,
                name: this.dataset.name,
                price: parseFloat(this.dataset.price)
            };

            let cart = getCart();
            const existingProduct = cart.find(item => item.id === product.id);
            if (!existingProduct) {
                cart.push(product);
                localStorage.setItem("cart", JSON.stringify(cart));
                updateCartUI();
            }
        });
    });

    // Відкриття модального вікна кошика
    const openCartBtn = document.getElementById("open-cart");
    if (openCartBtn) {
        openCartBtn.addEventListener("click", function () {
            const cartModal = document.getElementById("cartModal");
            if (cartModal) {
                cartModal.style.display = "block";
                cartModal.classList.add("show");
                cartModal.removeAttribute("aria-hidden");
            }
            updateCartUI();
        });
    }

    // Вхід
    const loginButton = document.getElementById("login-button");
    if (loginButton) {
        loginButton.addEventListener("click", function () {
            const loginModalEl = document.getElementById("loginModal");
            if (loginModalEl) {
                const loginModal = new bootstrap.Modal(loginModalEl);
                loginModal.show();
                console.log("🔹 Відкрито вікно входу!");
            } else {
                console.error("🚨 Модальне вікно входу не знайдено!");
            }
        });
    } else {
        console.error("🚨 Кнопка 'Log in' не знайдена!");
    }

    // Реєстрація
    const openRegisterModal = document.getElementById("openRegisterModal");
    if (openRegisterModal) {
        openRegisterModal.addEventListener("click", function () {
            const loginModalEl = document.getElementById("loginModal");
            const registerModalEl = document.getElementById("registerModal");

            if (loginModalEl && registerModalEl) {
                const loginModal = bootstrap.Modal.getInstance(loginModalEl);
                if (loginModal) loginModal.hide();

                const registerModal = new bootstrap.Modal(registerModalEl);
                registerModal.show();
            }
        });
    }

    // Обробка форм входу та реєстрації
    function handleFormSubmit(event, url) {
        event.preventDefault();
        const formData = new FormData(event.target);
        const csrfToken = document.querySelector("[name=csrfmiddlewaretoken]").value;
        formData.append("csrfmiddlewaretoken", csrfToken);

        fetch(url, {
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
            .catch(error => console.error("🚨 Помилка запиту:", error));
    }

    const loginForm = document.getElementById("login-form");
    const registerForm = document.getElementById("register-form");

    if (loginForm) {
        loginForm.addEventListener("submit", event => handleFormSubmit(event, "/login/"));
    } else {
        console.error("🚨 Форма входу не знайдена!");
    }

    if (registerForm) {
        registerForm.addEventListener("submit", event => handleFormSubmit(event, "/registration/"));
    }

    // Меню
    const menuButton = document.getElementById("menu-button");
    const closeMenuButton = document.getElementById("close-menu");
    const popupMenu = document.getElementById("popup-menu");

    if (menuButton && closeMenuButton && popupMenu) {
        menuButton.addEventListener("click", function () {
            popupMenu.classList.remove("hidden");
        });
        closeMenuButton.addEventListener("click", function () {
            popupMenu.classList.add("hidden");
        });
    } else {
        console.error("🚨 Меню не знайдено!");
    }
});

console.log("🔍 Функція updateCartUI() визначена!");
