document.addEventListener('DOMContentLoaded', function() {
    // Hamburger menu toggle
    const hamBurger = document.querySelector(".toggle-btn");
    hamBurger.addEventListener("click", function () {
        document.querySelector("#sidebar").classList.toggle("expand");
    });
});
