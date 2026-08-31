document.addEventListener("DOMContentLoaded", () => {
    loadCart();
    loadCheckoutCart();
    initPaymentToggle();
});

/* =========================
   LOAD CART INTO SUMMARY
========================= */

async function loadCheckoutCart() {
    try {
        const response = await fetch("/api/cart/", {
            credentials: "include"
        });

        if (!response.ok) throw new Error("Failed to load cart");

        const cart = await response.json();
        renderCheckoutItems(cart);

    } catch (error) {
        console.error("Checkout cart load error:", error);
    }
}

function renderCheckoutItems(cart) {
    const container = document.getElementById("checkout-items");
    container.innerHTML = "";

    let subtotal = 0;

    cart.items.forEach(item => {
        const product = item.product_detail;
        const itemTotal = product.price * item.quantity;
        subtotal += itemTotal;

        container.innerHTML += `
            <div class="checkout-item">
                <img src="${escapeHtml(product.image || '')}" alt="${escapeHtml(product.name)}">
                <div class="checkout-item-info">
                    <p>${escapeHtml(product.name)}</p>
                    <span>x${item.quantity}</span>
                </div>
                <div class="checkout-item-price">₱${itemTotal.toLocaleString()}</div>
            </div>
        `;
    });

    updateCheckoutSummary(subtotal);
}

function updateCheckoutSummary(subtotal) {
    const shipping = 120;
    const total = subtotal + shipping;

    document.getElementById("subtotal").innerText = `₱${subtotal.toLocaleString()}`;
    document.getElementById("total").innerText = `₱${total.toLocaleString()}`;
}

/* =========================
   PAYMENT METHOD TOGGLE
========================= */

function initPaymentToggle() {
    const options = document.querySelectorAll(".payment-option");

    options.forEach(option => {
        option.addEventListener("click", () => {
            // update active style
            options.forEach(o => o.classList.remove("active"));
            option.classList.add("active");

            // check the radio
            option.querySelector("input[type='radio']").checked = true;

            const paymentHelp = document.getElementById("payment-help");
            const value = option.querySelector("input").value;
            paymentHelp.style.display = value === "cod" ? "none" : "block";
        });
    });
}

/* =========================
   PLACE ORDER
========================= */

async function placeOrder() {
    const fullName  = document.getElementById("full-name").value.trim();
    const email     = document.getElementById("email").value.trim();
    const phone     = document.getElementById("phone").value.trim();
    const address   = document.getElementById("address").value.trim();
    const city      = document.getElementById("city").value.trim();
    const province  = document.getElementById("province").value.trim();
    const zip       = document.getElementById("zip").value.trim();
    const region    = document.getElementById("region").value.trim();
    const payment   = document.querySelector('input[name="payment"]:checked').value;

    // basic validation
    if (!fullName || !email || !phone || !address || !city || !province || !zip) {
        alert("Please fill in all required fields.");
        return;
    }

    const payload = {
        full_name: fullName,
        email,
        phone,
        address,
        city,
        province,
        zip,
        region,
        payment_method: payment,
    };

    try {
        const response = await fetch("/api/checkout/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCookie("csrftoken")
            },
            credentials: "include",
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            const err = await response.json();
            alert(err.error || "Something went wrong. Please try again.");
            return;
        }

        const result = await response.json();

        if (result.checkout_url) {
            window.location.href = result.checkout_url;
            return;
        }

        // show success modal
        document.getElementById("order-modal").style.display = "flex";

    } catch (error) {
        console.error("Order error:", error);
        alert("Something went wrong. Please try again.");
    }
}

/* =========================
   CSRF HELPER
========================= */

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

    } catch (error) {
        console.error("Cart load error:", error);
    }

}

function escapeHtml(value) {
    const element = document.createElement("div");
    element.textContent = value ?? "";
    return element.innerHTML;
}
