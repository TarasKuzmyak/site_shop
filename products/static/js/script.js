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
        const existingItem = cart.find(item => item.id === product.id);

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
        cart = cart.filter(item => item.id !== productId);
        this.saveCart(cart);
        return cart;
    }

    static updateQuantity(productId, quantity) {
        let cart = this.getCart();
        const item = cart.find(item => item.id === productId);

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
            cartItemsContainer.innerHTML = '';

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
                <img src="${item.image || '/static/img/no-image.png'}" alt="${item.name}">
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
            }
        }

        if (totalPriceElement) {
            totalPriceElement.textContent = CartManager.getTotalPrice().toFixed(2) + '₴';
        }
    }

    static showToast(message, type = 'success') {
        const toast = document.createElement('div');
        toast.className = `toast show align-items-center text-white bg-${type}`;
        toast.innerHTML = `
        <div class="d-flex">
          <div class="toast-body">${message}</div>
          <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
      `;

        const toastContainer = document.getElementById('toast-container') || document.body;
        toastContainer.appendChild(toast);

        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }
}

// Product Manager - обробка продуктів
class ProductManager {
    static initProductPage() {
        // Кнопка "Додати в кошик" на сторінці товару
        document.querySelectorAll('.add-to-cart').forEach(button => {
            button.addEventListener('click', () => {
                const product = {
                    id: button.dataset.id,
                    name: button.dataset.name,
                    price: parseFloat(button.dataset.price),
                    image: button.dataset.image
                };

                CartManager.addToCart(product);
                UIManager.updateCartIcon();
                UIManager.updateCartModal();
                UIManager.showToast('Товар додано до кошика!');
            });
        });

        // Кнопка "Купити зараз" на сторінці товару
        document.querySelectorAll('.buy-now').forEach(button => {
            button.addEventListener('click', () => {
                const product = {
                    id: button.dataset.id,
                    name: button.dataset.name,
                    price: parseFloat(button.dataset.price),
                    image: button.dataset.image
                };

                CartManager.clearCart();
                CartManager.addToCart(product);
                UIManager.updateCartIcon();
                UIManager.showToast('Товар додано до кошика!', 'info');

                // Відкриваємо кошик для оформлення
                const cartModal = new bootstrap.Modal(document.getElementById('cartModal'));
                cartModal.show();
            });
        });
    }
}

// Main App Initialization
document.addEventListener('DOMContentLoaded', () => {
    // Ініціалізація кошика
    UIManager.updateCartIcon();

    // Обробка подій кошика
    document.addEventListener('click', (e) => {
        // Додавання до кошика зі списку товарів
        if (e.target.closest('.add-to-cart')) {
            const button = e.target.closest('.add-to-cart');
            const product = {
                id: button.dataset.id,
                name: button.dataset.name,
                price: parseFloat(button.dataset.price),
                image: button.dataset.image || button.closest('.product-card')?.querySelector('img')?.src
            };

            CartManager.addToCart(product);
            UIManager.updateCartIcon();
            UIManager.updateCartModal();
            UIManager.showToast('Товар додано до кошика!');
        }

        // Видалення з кошика
        if (e.target.closest('.remove-item')) {
            const productId = e.target.closest('.remove-item').dataset.id;
            CartManager.removeFromCart(productId);
            UIManager.updateCartIcon();
            UIManager.updateCartModal();
            UIManager.showToast('Товар видалено з кошика', 'warning');
        }

        // Зміна кількості
        if (e.target.closest('.increase-qty')) {
            const productId = e.target.closest('.increase-qty').dataset.id;
            const cart = CartManager.getCart();
            const item = cart.find(item => item.id === productId);

            if (item) {
                CartManager.updateQuantity(productId, item.quantity + 1);
                UIManager.updateCartIcon();
                UIManager.updateCartModal();
            }
        }

        if (e.target.closest('.decrease-qty')) {
            const productId = e.target.closest('.decrease-qty').dataset.id;
            const cart = CartManager.getCart();
            const item = cart.find(item => item.id === productId);

            if (item && item.quantity > 1) {
                CartManager.updateQuantity(productId, item.quantity - 1);
                UIManager.updateCartIcon();
                UIManager.updateCartModal();
            }
        }
    });

    // Ініціалізація сторінки товару
    if (document.querySelector('.product-detail-page')) {
        ProductManager.initProductPage();
    }

    // Ініціалізація модального вікна кошика
    const cartModal = document.getElementById('cartModal');
    if (cartModal) {
        cartModal.addEventListener('show.bs.modal', () => {
            UIManager.updateCartModal();
        });

        // Оформлення замовлення
        const checkoutBtn = document.getElementById('checkout-btn');
        if (checkoutBtn) {
            checkoutBtn.addEventListener('click', () => {
                if (CartManager.getTotalItems() > 0) {
                    window.location.href = '/checkout/';
                } else {
                    UIManager.showToast('Кошик порожній!', 'danger');
                }
            });
        }
    }

    // Меню
    const menuButton = document.getElementById('menu-button');
    const closeMenuButton = document.getElementById('close-menu');
    const popupMenu = document.getElementById('popup-menu');

    if (menuButton && closeMenuButton && popupMenu) {
        menuButton.addEventListener('click', () => {
            popupMenu.classList.add('show');
            document.body.style.overflow = 'hidden';
        });

        closeMenuButton.addEventListener('click', () => {
            popupMenu.classList.remove('show');
            document.body.style.overflow = '';
        });
    }

    // Форми входу/реєстрації
    const handleFormSubmit = async (event, url) => {
        event.preventDefault();
        const form = event.target;
        const formData = new FormData(form);
        const submitButton = form.querySelector('button[type="submit"]');
        const originalText = submitButton.innerHTML;

        try {
            submitButton.disabled = true;
            submitButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Обробка...';

            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: formData
            });

            const data = await response.json();

            if (data.success) {
                UIManager.showToast(data.message || 'Успішно!');
                setTimeout(() => {
                    window.location.href = data.redirect_url || '/';
                }, 1500);
            } else {
                let errorMessage = data.message || 'Сталася помилка';
                if (data.errors) {
                    errorMessage += ': ' + Object.values(data.errors).join(', ');
                }
                UIManager.showToast(errorMessage, 'danger');
            }
        } catch (error) {
            UIManager.showToast('Помилка мережі. Спробуйте ще раз.', 'danger');
            console.error('Помилка:', error);
        } finally {
            submitButton.disabled = false;
            submitButton.innerHTML = originalText;
        }
    };

    const loginForm = document.getElementById('login-form');
    const registerForm = document.getElementById('register-form');

    if (loginForm) {
        loginForm.addEventListener('submit', (e) => handleFormSubmit(e, '/login/'));
    }

    if (registerForm) {
        registerForm.addEventListener('submit', (e) => handleFormSubmit(e, '/registration/'));
    }

    // Кнопка "Наверх"
    const backToTopButton = document.getElementById('back-to-top');
    if (backToTopButton) {
        window.addEventListener('scroll', () => {
            if (window.pageYOffset > 300) {
                backToTopButton.style.display = 'block';
            } else {
                backToTopButton.style.display = 'none';
            }
        });

        backToTopButton.addEventListener('click', () => {
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
    }
});

// Анімації при скролі
window.addEventListener('scroll', () => {
    document.querySelectorAll('.animate-on-scroll').forEach(element => {
        const elementPosition = element.getBoundingClientRect().top;
        const screenPosition = window.innerHeight / 1.3;

        if (elementPosition < screenPosition) {
            element.classList.add('animated');
        }
    });
});