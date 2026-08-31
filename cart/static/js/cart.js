document.addEventListener("DOMContentLoaded", () => {
    loadCart();
});

async function loadCart() {

    try {
        const response = await fetch("/api/cart/", {
            credentials: "include"
        });
        console.log(response)
        if (!response.ok) {
            throw new Error("Failed to load cart");
        }

        const cart = await response.json();
        console.log(cart)
        renderCart(cart);

    } catch (error) {
        console.error("Cart load error:", error);
    }
}

function renderCart(cart) {

    const container = document.getElementById("cart-items");
    container.innerHTML = "";

    let subtotal = 0;

    cart.items.forEach(item => {
        console.log(cart.items)
        const product = item.product_detail;
        const itemTotal = product.price * item.quantity;

        subtotal += itemTotal;

        container.innerHTML += `
            <div class="cart-card">

                <img class="product-image"
                     src="${escapeHtml(product.image || '')}">

                <div class="product-info">

                    <h3>${escapeHtml(product.name)}</h3>

                    <p>${escapeHtml(product.description)}</p>

                    <div class="quantity">

                        <button onclick="removeItem(${item.quantity - 1}, ${item.id})">-</button>

                        <span>${item.quantity}</span>

                        <button onclick="addItem(${item.product}, ${item.quantity})">+</button>

                    </div>

                </div>

                <div class="product-price">
                    ₱${itemTotal}
                </div>
                <button class="remove-btn" onclick="deleteItem(${item.id})">
                    Remove
                </button>

            </div>
        `;
    });

    updateSummary(subtotal);
}

function updateSummary(subtotal) {

    const shipping = 120;
    const total = subtotal + shipping;

    document.getElementById("subtotal").innerText =
        `₱${subtotal}`;

    document.getElementById("total").innerText =
        `₱${total}`;
}

async function addItem(productId) {

    await fetch("/api/cart/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken")
        },
        credentials: "include",
        body: JSON.stringify({
            product_id: productId,
            quantity: 1
        })
    });

    loadCart();
}


async function removeItem(quantity, itemId) {

    if (quantity < 1) {

        deleteItem(itemId);

    } else {

        await fetch(`/api/cart/${itemId}/`, {
            method: "PUT",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCookie("csrftoken")
            },
            credentials: "include",
            body: JSON.stringify({
                quantity: quantity
            })
        }); 

        loadCart();
    }
}

async function deleteItem(itemId) {

    await fetch(`/api/cart/${itemId}/`, {
        method: "DELETE",
        credentials: "include",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken")
        },
    });

    loadCart();
}

function getCookie(name) {
    let cookieValue = null;

    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');

        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();

            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }

    return cookieValue;
}

function escapeHtml(value) {
    const element = document.createElement("div");
    element.textContent = value ?? "";
    return element.innerHTML;
}
