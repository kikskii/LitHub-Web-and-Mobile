// Function to update cart count in the navbar
function updateCartCount() {
    fetch('/get_cart_count')
        .then(response => response.json())
        .then(data => {
            document.getElementById('cart-count').textContent = data.count;
        })
        .catch(error => {
            console.error('Error fetching cart count:', error);
        });
}

// Function to add item to cart
function addToCart(productId) {
    const form = document.getElementById(`add-to-cart-form-${productId}`);
    const quantityInput = form.querySelector('input[name="quantity"]');
    const quantity = parseInt(quantityInput.value);

    if (isNaN(quantity) || quantity < 1) {
        alert('Please enter a valid quantity');
        return;
    }

    const formData = new FormData();
    formData.append('quantity', quantity);

    fetch(`/add_to_cart/${productId}`, {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            // Show success message
            alert(data.message);
            // Update cart count
            updateCartCount();
        } else {
            // Show error message
            alert(data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred while adding to cart. Please try again.');
    });
}

// Function to handle quantity buttons for all products
function initQuantityControls() {
    // Plus button click handler
    document.querySelectorAll('.button-plus').forEach(button => {
        button.addEventListener('click', function() {
            const input = this.parentElement.querySelector('.quantity-field');
            input.value = parseInt(input.value) + 1;
        });
    });

    // Minus button click handler
    document.querySelectorAll('.button-minus').forEach(button => {
        button.addEventListener('click', function() {
            const input = this.parentElement.querySelector('.quantity-field');
            const value = parseInt(input.value);
            if (value > 1) {
                input.value = value - 1;
            }
        });
    });
}

// Initialize cart functionality when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize quantity controls
    initQuantityControls();
    
    // Update initial cart count
    updateCartCount();
});
