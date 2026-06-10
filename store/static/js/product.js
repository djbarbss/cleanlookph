document.addEventListener("DOMContentLoaded", () => {
    loadProduct();
});

async function loadProduct() {

    // Get product ID from Django template
    const productId = window.PRODUCT_ID;
    console.log(window)
    if (!productId) {
        console.error("Product ID not found");
        return;
    }

    try {
        const response = await fetch(`/api/products/${productId}/`);

        if (!response.ok) {
            throw new Error("Failed to fetch product");
        }

        const product = await response.json();
        console.log(product);
        renderProduct(product);

    } catch (error) {
        console.error("Error loading product:", error);
    }
}

function renderProduct(product) {

    // NAME
    const nameEl = document.getElementById("product-name");
    if (nameEl) {
        nameEl.innerText = product.name;
    }

    // DESCRIPTION
    const descEl = document.getElementById("product-description");
    if (descEl) {
        descEl.innerText = product.description;
    }

    // PRICE
    const priceEl = document.getElementById("product-price");
    if (priceEl) {
        priceEl.innerText = `₱${product.price}`;
    }

    // IMAGE
    const imageEl = document.getElementById("product-image");
    if (imageEl && product.image) {
        imageEl.src = product.image;
        imageEl.alt = product.name;
    }

}