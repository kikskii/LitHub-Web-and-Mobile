

// Add this to your user.js
document.addEventListener('DOMContentLoaded', function() {
    const sidebar = document.getElementById('sidebar');
    const main = document.querySelector('.main');
    const header = document.querySelector('header');
    const toggleBtn = document.querySelector('.toggle-btn');

    toggleBtn.addEventListener('click', function() {
        sidebar.classList.toggle('collapsed');
        main.classList.toggle('expanded');
        header.classList.toggle('expanded');
        
        // Update visibility of elements when collapsed
        if (sidebar.classList.contains('collapsed')) {
            document.querySelectorAll('#sidebar .sidebar-logo, #sidebar .sidebar-link span')
                .forEach(el => el.style.display = 'none');
        } else {
            document.querySelectorAll('#sidebar .sidebar-logo, #sidebar .sidebar-link span')
                .forEach(el => el.style.display = 'block');
        }
    });

    // Your existing JavaScript code...
});
document.addEventListener('DOMContentLoaded', function() {
    // Update active state based on current URL
    function updateActiveState() {
        const currentPath = window.location.pathname;
        document.querySelectorAll('.sidebar-link').forEach(link => {
            if (link.getAttribute('href') === currentPath) {
                link.classList.add('active');
            } else {
                link.classList.remove('active');
            }
        });
    }
    

    // Call on page load
    updateActiveState();

    // Handle sidebar navigation
    document.querySelectorAll('.sidebar-link').forEach(link => {
        link.addEventListener('click', function(e) {
            if (!this.getAttribute('href').includes('logout')) {
                e.preventDefault();
                const url = this.getAttribute('href');
                
                // Update URL without page reload
                window.history.pushState({}, '', url);
                
                // Update active state
                updateActiveState();
                
                // Load content
                loadContent(url);
            }
        });
    });



    function loadContent(url) {
        const container = document.getElementById('content-container');
        if (!container) return;
        
        fetch(url, {
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.text())
        .then(html => {
            container.innerHTML = html;
            
            // Reinitialize any necessary JavaScript
            if (typeof initializeForms === 'function') {
                initializeForms();
            }
        })
        .catch(error => {
            console.error('Error loading content:', error);
            container.innerHTML = '<div class="alert alert-danger">Error loading content. Please try again.</div>';
        });
    }

    // Initialize forms and other interactive elements
    function initializeForms() {
        // Profile form
        const profileForm = document.querySelector('.profile-form');
        if (profileForm) {
            profileForm.addEventListener('submit', function(e) {
                e.preventDefault();
                const formData = new FormData(this);
                
                fetch('/update_profile', {
                    method: 'POST',
                    body: formData
                })
                .then(response => response.json())
                .then(data => {
                    if (data.message) {
                        showAlert(data.message, 'success');
                    } else if (data.error) {
                        showAlert(data.error, 'danger');
                    }
                });
            });
        }
    }

    // Helper function to show alerts
    function showAlert(message, type) {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        document.querySelector('.main .container').insertAdjacentElement('beforebegin', alertDiv);
        
        // Auto dismiss after 5 seconds
        setTimeout(() => {
            alertDiv.remove();
        }, 5000);
    }
});
