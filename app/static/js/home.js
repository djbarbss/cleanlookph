document.addEventListener("DOMContentLoaded", () => {
    loadLatestProducts();
});

async function loadLatestProducts() {

    try {

        const response = await fetch("/api/products/latest");

        if (!response.ok) {
            throw new Error("Failed to load products");
        }

        const products = await response.json();

        const container = document.getElementById("latest-products");

        if (!container) return;

        container.innerHTML = "";
        console.log(products)
        // Only show latest 6 products
        products.slice(0, 6).forEach(product => {

            container.innerHTML += `
                <div class="product-card" data-product-id=${product.id}>
                    <a href="/product/${product.id}/" class="product-link">
                        <div>
                            <img class="img" src="${product.image}" alt="${product.name}">
                        </div>

                        <h3>${product.name}</h3>

                        <p>${product.description}</p>

                        <span>₱${product.price}</span>
                    </a>
                    <button class="add-to-cart-btn">Add to Cart</button>
                </div>
            `;

        });

    } catch (error) {
        console.error("Error loading latest products:", error);
    }
}


document.addEventListener("click", async (event) => {

    if (event.target.classList.contains("add-to-cart-btn")) {

        const card = event.target.closest(".product-card");

        const productId = card.getAttribute("data-product-id");

        await addToCart(productId);
    }

});

function attachCartButtons() {

    const buttons = document.querySelectorAll(".product-card button");

    buttons.forEach(button => {

        button.addEventListener("click", async (event) => {
            event.preventDefault();
            event.stopPropagation();

            const card = button.closest(".product-card");
            const productId = card.getAttribute("data-product-id");

            await addToCart(productId);
        });

    });
}

async function addToCart(productId) {
    console.log(productId)
    try {
        const response = await fetch("/api/cart/", {
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
        console.log(response)
        if (!response.ok) {
            throw new Error("Failed to add to cart");
        }

        const data = await response.json();

        showToast("Added to cart!");

    } catch (error) {
        console.error("Add to cart error:", error);
        showToast("Error adding to cart");
    }
}

function showToast(message) {

    let toast = document.createElement("div");

    toast.innerText = message;

    toast.style.position = "fixed";
    toast.style.bottom = "20px";
    toast.style.right = "20px";
    toast.style.background = "#111";
    toast.style.color = "#fff";
    toast.style.padding = "10px 15px";
    toast.style.borderRadius = "8px";
    toast.style.zIndex = "9999";

    document.body.appendChild(toast);

    setTimeout(() => {
        toast.remove();
    }, 2000);
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