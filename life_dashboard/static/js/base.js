// Mobile menu handler
function setupMobileMenu() {
    const toggler = document.querySelector('.navbar-toggler');
    const collapse = document.querySelector('.navbar-collapse');

    if (!toggler || !collapse) return;

    // Toggle mobile menu icon
    toggler.addEventListener('click', function() {
        const isExpanded = this.getAttribute('aria-expanded') === 'true' || false;
        const icon = this.querySelector('i');

        // Toggle icon between bars and times
        if (icon) {
            icon.classList.toggle('fa-bars', isExpanded);
            icon.classList.toggle('fa-times', !isExpanded);
        }
    });

    // Handle dropdown toggles on mobile
    document.addEventListener('click', function(e) {
        // Only handle mobile view
        if (window.innerWidth >= 992) return;

        const dropdownToggle = e.target.closest('.dropdown-toggle');
        const dropdownMenu = e.target.closest('.dropdown-menu');

        // If clicking a dropdown toggle
        if (dropdownToggle) {
            e.preventDefault();
            const menu = dropdownToggle.nextElementSibling;
            if (!menu || !menu.classList.contains('dropdown-menu')) return;

            const isExpanded = dropdownToggle.getAttribute('aria-expanded') === 'true' || false;

            // Close other dropdowns
            document.querySelectorAll('.dropdown-menu.show').forEach(openMenu => {
                if (openMenu !== menu) {
                    openMenu.classList.remove('show');
                    const openToggle = openMenu.previousElementSibling;
                    if (openToggle) {
                        openToggle.setAttribute('aria-expanded', 'false');
                    }
                }
            });

            // Toggle current dropdown
            menu.classList.toggle('show', !isExpanded);
            dropdownToggle.setAttribute('aria-expanded', !isExpanded);
        }
        // If clicking outside dropdown
        else if (!dropdownMenu) {
            document.querySelectorAll('.dropdown-menu.show').forEach(menu => {
                menu.classList.remove('show');
                const toggle = menu.previousElementSibling;
                if (toggle) {
                    toggle.setAttribute('aria-expanded', 'false');
                }
            });
        }
    });

    // Close mobile menu when clicking on a nav link
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', function() {
            if (window.innerWidth < 992 && collapse.classList.contains('show')) {
                const bsCollapse = bootstrap.Collapse.getInstance(collapse);
                if (bsCollapse) {
                    bsCollapse.hide();
                }
            }
        });
    });
}

// Utility functions
function formatDate(date) {
    if (!date) return '';
    const d = new Date(date);
    return d.toLocaleDateString();
}

function formatDateTime(date) {
    if (!date) return '';
    const d = new Date(date);
    return d.toLocaleString();
}

// Initialize tooltips
document.addEventListener('DOMContentLoaded', function() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});

// Initialize date pickers
document.addEventListener('DOMContentLoaded', function() {
    const dateInputs = document.querySelectorAll('input[type="date"]');
    dateInputs.forEach(input => {
        if (!input.value) {
            const today = new Date().toISOString().split('T')[0];
            input.value = today;
        }
    });
});

// Confirm delete
function confirmDelete(message) {
    return confirm(message || 'Are you sure you want to delete this item?');
}

// Show alert
function showAlert(message, type = 'success') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.role = 'alert';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;

    // Try to find a container element
    const container = document.querySelector('.container');
    if (container) {
        container.insertBefore(alertDiv, container.firstChild);
    } else {
        // Fallback: append to body if no container found
        console.warn('No .container element found, appending alert to body');
        document.body.insertBefore(alertDiv, document.body.firstChild);
    }

    // Auto-remove after 5 seconds
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

// Update progress bar
function updateProgressBar(elementId, value, max) {
    const element = document.getElementById(elementId);
    if (element) {
        const percentage = (value / max) * 100;
        element.style.width = `${percentage}%`;
        element.setAttribute('aria-valuenow', value);
        element.setAttribute('aria-valuemax', max);
    }
}

// Toggle visibility
function toggleVisibility(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.classList.toggle('d-none');
    }
}

// Copy to clipboard
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showAlert('Copied to clipboard!');
    }).catch(err => {
        console.error('Failed to copy text: ', err);
    });
}

// Debounce function
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Throttle function
function throttle(func, limit) {
    let inThrottle;
    return function executedFunction(...args) {
        if (!inThrottle) {
            func(...args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}
