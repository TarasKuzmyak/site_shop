// Cart Manager - керування кошиком
class CartManager {
    static getCart() {
        return JSON.parse(localStorage.getItem("clicktype-cart")) || [];
    }

    static saveCart(cart) {
        localStorage.setItem("clicktype-cart", JSON.stringify(cart));
    }

    static addToCart(product) {
        const cart = this.getCart();
        const existingItem = cart.find(item => item.id == product.id);

        if (existingItem) {
            existingItem.quantity += product.quantity || 1;
        } else {
            cart.push({
                ...product,
                quantity: product.quantity || 1,
                addedAt: new Date().toISOString()
            });
        }

        this.saveCart(cart);
        return cart;
    }

    static removeFromCart(productId) {
        let cart = this.getCart();
        cart = cart.filter(item => item.id != productId);
        this.saveCart(cart);
        return cart;
    }

    static updateQuantity(productId, quantity) {
        let cart = this.getCart();
        const item = cart.find(item => item.id == productId);

        if (item) {
            item.quantity = quantity;
            this.saveCart(cart);
        }

        return cart;
    }

    static clearCart() {
        localStorage.removeItem("clicktype-cart");
        return [];
    }

    static getTotalItems() {
        return this.getCart().reduce((total, item) => total + item.quantity, 0);
    }

    static getTotalPrice() {
        return this.getCart().reduce((total, item) => total + (item.price * item.quantity), 0);
    }

    static getCartDataForTemplate() {
        return this.getCart().map(item => ({
            id: item.id,
            name: item.name,
            price: item.price,
            quantity: item.quantity,
            total: item.price * item.quantity,
            image: item.image
        }));
    }

    static async initCartForAuthenticatedUser(userId) {
        if (!userId) { // Додаткова перевірка, якщо userId з якихось причин не був переданий
            console.warn('initCartForAuthenticatedUser викликано без userId.');
            return [];
        }
        try {
            const response = await fetch(`/api/get-cart/?user_id=${userId}`);
            if (response.ok) {
                const cartData = await response.json();
                this.saveCart(cartData);
                return cartData;
            } else {
                const errorText = await response.text(); // Отримуємо текст для детальнішої помилки
                console.error('Error fetching cart:', response.status, errorText);
                UIManager.showToast(`Помилка завантаження кошика з сервера (${response.status}).`, 'danger');
                return [];
            }
        } catch (error) {
            console.error('Error fetching cart:', error);
            UIManager.showToast('Не вдалося підключитися до сервера для завантаження кошика.', 'danger');
            return [];
        }
    }
}

// UI Manager - оновлення інтерфейсу
class UIManager {
    static updateCartIcon() {
        const cartCount = CartManager.getTotalItems();
        document.querySelectorAll('.cart-count').forEach(el => {
            el.textContent = cartCount;
            el.style.display = cartCount > 0 ? 'inline-block' : 'none';
        });
    }

    static updateCartModal() {
        const cartItemsContainer = document.getElementById('cart-items');
        const totalPriceElement = document.getElementById('total-price');
        const emptyCartElement = document.getElementById('cart-empty');
        const cart = CartManager.getCart();

        if (cartItemsContainer) {
            cartItemsContainer.innerHTML = ''; // Очищаємо перед додаванням нових елементів

            if (cart.length === 0) {
                cartItemsContainer.style.display = 'none';
                if (emptyCartElement) emptyCartElement.style.display = 'block';
            } else {
                cartItemsContainer.style.display = 'block';
                if (emptyCartElement) emptyCartElement.style.display = 'none';

                cart.forEach(item => {
                    const cartItem = document.createElement('div');
                    cartItem.className = 'cart-item';
                    cartItem.innerHTML = `
                        <div class="cart-item-image">
                            <img src="${item.image}" alt="${item.name}" onerror="this.onerror=null;this.src='/static/img/no-image.png'">
                        </div>
                        <div class="cart-item-details">
                            <h5>${item.name}</h5>
                            <div class="cart-item-price">${item.price}₴ × ${item.quantity}</div>
                            <div class="cart-item-controls">
                                <button class="btn btn-sm btn-outline-secondary decrease-qty" data-id="${item.id}">-</button>
                                <span class="quantity">${item.quantity}</span>
                                <button class="btn btn-sm btn-outline-secondary increase-qty" data-id="${item.id}">+</button>
                                <button class="btn btn-sm btn-danger remove-item" data-id="${item.id}">
                                    <i class="fas fa-trash"></i>
                                </button>
                            </div>
                        </div>
                        <div class="cart-item-total">${(item.price * item.quantity).toFixed(2)}₴</div>
                    `;
                    cartItemsContainer.appendChild(cartItem);
                });
                // Після перемальовування модального вікна, делеговані події оброблятимуть кнопки
            }
        }

        if (totalPriceElement) {
            totalPriceElement.textContent = CartManager.getTotalPrice().toFixed(2);
        }
    }

    static showToast(message, type = 'success') {
        const toastContainer = document.getElementById('toast-container');
        if (!toastContainer) {
            console.warn('Toast container not found. Toast message will not be displayed.');
            return;
        }

        const toast = document.createElement('div');
        toast.className = `toast show align-items-center text-white bg-${type}`;
        toast.setAttribute('role', 'alert');
        toast.setAttribute('aria-live', 'assertive');
        toast.setAttribute('aria-atomic', 'true');
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">${message}</div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        `;

        toastContainer.appendChild(toast);

        // Видалення тоста через деякий час
        setTimeout(() => {
            if (toast) { // Перевірка, щоб уникнути помилок, якщо toast вже був видалений вручну
                toast.classList.remove('show');
                setTimeout(() => toast.remove(), 300); // Час для анімації fade-out
            }
        }, 3000);
    }

    static updateCartPage() {
        const cartContainer = document.getElementById('cart-container');
        if (!cartContainer) return;

        const cart = CartManager.getCartDataForTemplate();

        if (cart.length === 0) {
            cartContainer.innerHTML = `
                <div class="alert alert-info">
                    <i class="fas fa-info-circle me-2"></i>Ваш кошик порожній.
                </div>
                <a href="/products/" class="btn btn-outline-dark">
                    <i class="fas fa-arrow-left me-2"></i>Продовжити покупки
                </a>
            `;
            return;
        }

        const totalPrice = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);

        cartContainer.innerHTML = `
            <div class="row">
                <div class="col-lg-8">
                    <div class="card mb-4">
                        <div class="card-body">
                            <div class="table-responsive">
                                <table class="table">
                                    <thead>
                                        <tr>
                                            <th>Товар</th>
                                            <th>Ціна</th>
                                            <th>Кількість</th>
                                            <th>Сума</th>
                                            <th></th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        ${cart.map(item => `
                                            <tr>
                                                <td>
                                                    <div class="d-flex align-items-center">
                                                        <img src="${item.image}" alt="${item.name}" class="me-3" style="width: 80px;" onerror="this.onerror=null; this.src='/static/img/no-image.png'">
                                                        <div>
                                                            <h5 class="mb-0">${item.name}</h5>
                                                        </div>
                                                    </div>
                                                </td>
                                                <td>${item.price}₴</td>
                                                <td>
                                                    <div class="input-group input-group-sm" style="width: 100px;">
                                                        <button class="btn btn-outline-secondary decrease-qty" type="button" data-id="${item.id}">-</button>
                                                        <input type="text" class="form-control text-center quantity-input" value="${item.quantity}" readonly>
                                                        <button class="btn btn-outline-secondary increase-qty" type="button" data-id="${item.id}">+</button>
                                                    </div>
                                                </td>
                                                <td>${(item.price * item.quantity).toFixed(2)}₴</td>
                                                <td>
                                                    <button class="btn btn-sm btn-outline-danger remove-item" data-id="${item.id}">
                                                        <i class="fas fa-trash"></i>
                                                    </button>
                                                </td>
                                            </tr>
                                        `).join('')}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                    
                    <div class="d-flex justify-content-between mb-4">
                        <a href="/products/" class="btn btn-outline-dark">
                            <i class="fas fa-arrow-left me-2"></i>Продовжити покупки
                        </a>
                        <a href="/checkout/" class="btn btn-warning">
                            Оформити замовлення <i class="fas fa-arrow-right ms-2"></i>
                        </a>
                    </div>
                </div>
                
                <div class="col-lg-4">
                    <div class="card">
                        <div class="card-header bg-dark text-white">
                            <h5 class="mb-0">Підсумок кошика</h5>
                        </div>
                        <div class="card-body">
                            <div class="d-flex justify-content-between mb-2">
                                <span>Товари (${cart.length})</span>
                                <span>${totalPrice.toFixed(2)}₴</span>
                            </div>
                            <div class="d-flex justify-content-between mb-2">
                                <span>Доставка</span>
                                <span>Безкоштовно</span>
                            </div>
                            <hr>
                            <div class="d-flex justify-content-between fw-bold">
                                <span>До оплати</span>
                                <span>${totalPrice.toFixed(2)}₴</span>
                            </div>
                            <a href="/checkout/" class="btn btn-warning w-100 mt-3">
                                Оформити замовлення
                            </a>
                        </div>
                    </div>
                </div>
            </div>
        `;
        // Важливо: після перемальовування сторінки, делеговані обробники подій все ще працюють.
        // Тому не потрібно додавати нові addEventListener тут.
    }
}

// Product Manager - обробка продуктів
class ProductManager {
    static initProductPage() {
        this.initAddToCartButtons();
        this.initBuyNowButtons();
    }

    static initCategoryPage() {
        this.initAddToCartButtons();
        this.initBuyNowButtons();
    }

    static initAddToCartButtons() {
        document.querySelectorAll('.add-to-cart').forEach(button => {
            button.addEventListener('click', function () {
                const product = {
                    id: this.dataset.id,
                    name: this.dataset.name,
                    price: parseFloat(this.dataset.price),
                    image: this.dataset.image || this.closest('.product-card')?.querySelector('img')?.src
                };

                CartManager.addToCart(product);
                UIManager.updateCartIcon();
                UIManager.updateCartModal(); // Оновити модальне вікно, щоб відобразити доданий товар
                UIManager.showToast('Товар додано до кошика!');
            });
        });
    }

    static initBuyNowButtons() {
        document.querySelectorAll('.buy-now').forEach(button => {
            button.addEventListener('click', function () {
                const product = {
                    id: this.dataset.id,
                    name: this.dataset.name,
                    price: parseFloat(this.dataset.price),
                    image: this.dataset.image || this.closest('.product-card')?.querySelector('img')?.src
                };

                CartManager.clearCart();
                CartManager.addToCart(product);
                UIManager.updateCartIcon();
                UIManager.updateCartModal(); // Оновити модальне вікно
                UIManager.showToast('Товар додано до кошика!', 'info');

                // Відкрити модальне вікно кошика
                const cartModalEl = document.getElementById('cartModal');
                if (cartModalEl) {
                    const cartModal = new bootstrap.Modal(cartModalEl);
                    cartModal.show();
                }
            });
        });
    }
}

// Main App Initialization
document.addEventListener('DOMContentLoaded', async function () {
    // Ініціалізація кошика для авторизованих користувачів
    // Тепер ці дані мають бути передані через HTML атрибути,
    // а не через Django шаблонізатор безпосередньо в JS файлі.
    const isAuthenticated = document.body.dataset.isAuthenticated === 'true';
    const userId = document.body.dataset.userId ? parseInt(document.body.dataset.userId) : null;

    if (isAuthenticated && userId) {
        await CartManager.initCartForAuthenticatedUser(userId);
    }

    UIManager.updateCartIcon();
    UIManager.updateCartPage(); // Первинне оновлення сторінки кошика

    // Ініціалізація сторінки товару
    if (document.querySelector('.product-detail-page')) {
        ProductManager.initProductPage();
    }

    // Ініціалізація сторінок категорій (keyboard, mouse, headsets)
    if (document.querySelector('.products-section')) {
        ProductManager.initCategoryPage();
    }

    // Обробка подій кошика через делегування (для динамічних елементів)
    document.addEventListener('click', function (e) {
        // Видалення товару
        const removeItemButton = e.target.closest('.remove-item');
        if (removeItemButton) {
            const productId = removeItemButton.dataset.id;
            CartManager.removeFromCart(productId);
            UIManager.updateCartIcon();
            UIManager.updateCartModal(); // Оновлення модального вікна
            UIManager.updateCartPage(); // Оновлення сторінки кошика
            UIManager.showToast('Товар видалено з кошика', 'warning');
            return; // Вийти, щоб уникнути обробки іншими if-блоками, якщо це той самий клік
        }

        // Збільшення кількості
        const increaseQtyButton = e.target.closest('.increase-qty');
        if (increaseQtyButton) {
            const productId = increaseQtyButton.dataset.id;
            const cart = CartManager.getCart();
            const item = cart.find(item => item.id == productId);

            if (item) {
                CartManager.updateQuantity(productId, item.quantity + 1);
                UIManager.updateCartIcon();
                UIManager.updateCartModal();
                UIManager.updateCartPage();
            }
            return;
        }

        // Зменшення кількості
        const decreaseQtyButton = e.target.closest('.decrease-qty');
        if (decreaseQtyButton) {
            const productId = decreaseQtyButton.dataset.id;
            const cart = CartManager.getCart();
            const item = cart.find(item => item.id == productId);

            if (item && item.quantity > 1) {
                CartManager.updateQuantity(productId, item.quantity - 1);
                UIManager.updateCartIcon();
                UIManager.updateCartModal();
                UIManager.updateCartPage();
            } else if (item && item.quantity === 1) {
                // Можна також видалити товар, якщо кількість стає 0
                CartManager.removeFromCart(productId);
                UIManager.updateCartIcon();
                UIManager.updateCartModal();
                UIManager.updateCartPage();
                UIManager.showToast('Товар видалено з кошика', 'warning');
            }
            return;
        }
    });

    // Ініціалізація модального вікна кошика (оновлення при відкритті)
    const cartModal = document.getElementById('cartModal');
    if (cartModal) {
        cartModal.addEventListener('show.bs.modal', function () {
            UIManager.updateCartModal();
        });

        const checkoutBtn = document.getElementById('checkout-btn');
        if (checkoutBtn) {
            checkoutBtn.addEventListener('click', function () {
                if (CartManager.getTotalItems() > 0) {
                    window.location.href = '/checkout/';
                } else {
                    UIManager.showToast('Кошик порожній!', 'danger');
                }
            });
        }
    }

    // Меню (ініціалізація та обробники)
    const menuButton = document.getElementById('menu-button');
    const closeMenuButton = document.getElementById('close-menu');
    const popupMenu = document.getElementById('popup-menu');

    if (menuButton && closeMenuButton && popupMenu) {
        menuButton.addEventListener('click', function () {
            popupMenu.classList.add('show');
            document.body.style.overflow = 'hidden'; // Заборонити скрол сторінки
        });

        closeMenuButton.addEventListener('click', function () {
            popupMenu.classList.remove('show');
            document.body.style.overflow = ''; // Відновити скрол
        });
    }

    // Обробник для форм авторизації/реєстрації
    const handleFormSubmit = async function (event, url) {
        event.preventDefault();
        const form = event.target;
        const formData = new FormData(form);
        const submitButton = form.querySelector('button[type="submit"]');
        const originalText = submitButton ? submitButton.innerHTML : 'Submit'; // Захист від null

        if (submitButton) {
            submitButton.disabled = true;
            submitButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Обробка...';
        }

        try {
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
            if (!csrfToken) {
                throw new Error('CSRF токен не знайдено.');
            }

            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken,
                    'Accept': 'application/json',
                },
                body: formData
            });

            const contentType = response.headers.get('content-type');
            if (!contentType || !contentType.includes('application/json')) {
                const text = await response.text();
                // Якщо не JSON, можливо, це редирект або HTML помилка, яку Django повертає за замовчуванням
                if (response.redirected) {
                    window.location.href = response.url; // Перенаправити, якщо був редирект
                    return;
                }
                throw new Error(`Очікувався JSON, але отримано: ${contentType}. Відповідь: ${text.substring(0, 100)}...`);
            }

            const data = await response.json();

            if (data.success) {
                UIManager.showToast(data.message || 'Успішно!');
                setTimeout(function () {
                    if (data.redirect_url) {
                        window.location.href = data.redirect_url;
                    } else {
                        window.location.reload();
                    }
                }, 1500);
            } else {
                let errorMessage = data.error || 'Сталася помилка';
                if (data.errors) { // Якщо є детальні помилки форми (наприклад, Django Form errors)
                    const errorsArray = Object.values(data.errors).map(err => Array.isArray(err) ? err.join(' ') : err);
                    errorMessage += ': ' + errorsArray.join('; ');
                }
                UIManager.showToast(errorMessage, 'danger');
            }
        } catch (error) {
            console.error('Помилка при відправці форми:', error);
            UIManager.showToast('Помилка сервера. Спробуйте ще раз або зверніться до підтримки.', 'danger');
        } finally {
            if (submitButton) {
                submitButton.disabled = false;
                submitButton.innerHTML = originalText;
            }
        }
    };

    // Обробник форми входу
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', function (e) {
            handleFormSubmit(e, '/login/'); // Переконайтеся, що це коректний URL
        });
    }

    // Обробник форми реєстрації
    const registerForm = document.getElementById('register-form');
    if (registerForm) {
        registerForm.addEventListener('submit', function (e) { // Змінено на handleFormSubmit
            handleFormSubmit(e, '/accounts/register/'); // Переконайтеся, що це коректний URL
        });
    }

    // Кнопка "Наверх"
    const backToTopButton = document.getElementById('back-to-top');
    if (backToTopButton) {
        window.addEventListener('scroll', function () {
            if (window.pageYOffset > 300) {
                backToTopButton.style.display = 'block';
            } else {
                backToTopButton.style.display = 'none';
            }
        });

        backToTopButton.addEventListener('click', function () {
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
    }

    // Анімації при скролі
    // Цей обробник буде спрацьовувати щоразу при скролі, можна оптимізувати,
    // наприклад, використовувати Intersection Observer API для кращої продуктивності
    // або додавати клас тільки один раз.
    window.addEventListener('scroll', function () {
        document.querySelectorAll('.animate-on-scroll:not(.animated)').forEach(element => {
            const elementPosition = element.getBoundingClientRect().top;
            const screenPosition = window.innerHeight / 1.3; // Елемент анімується, коли 1/3 екрану пройшла його

            if (elementPosition < screenPosition) {
                element.classList.add('animated');
            }
        });
    });
});

document.addEventListener('DOMContentLoaded', function () {
    // Check if we have success parameter in URL
    const urlParams = new URLSearchParams(window.location.search);
    const orderSuccess = urlParams.get('order_success');

    if (orderSuccess) {
        Swal.fire({
            title: 'Замовлення оформлено!',
            text: 'Ваше замовлення успішно оформлене.',
            icon: 'success',
            confirmButtonText: 'OK'
        }).then(() => {
            // Remove the parameter from URL
            const newUrl = window.location.href.split('?')[0];
            window.history.replaceState({}, document.title, newUrl);
        });
    }
});