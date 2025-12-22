// SRBMC College Management ERP - Main JavaScript

// Global variables
let currentUser = null;
let currentTheme = 'light';
let notifications = [];

// Initialize application
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    setupEventListeners();
    loadUserPreferences();
});

// Application initialization
function initializeApp() {
    console.log('Initializing SRBMC ERP Application...');

    // Initialize tooltips
    initializeTooltips();

    // Initialize modals
    initializeModals();

    // Setup form validation
    setupFormValidation();

    // Initialize data tables
    initializeDataTables();

    // Setup notification system
    initializeNotifications();

    // Apply fade-in animation to main content
    const mainContent = document.querySelector('main');
    if (mainContent) {
        mainContent.classList.add('fade-in');
    }

    console.log('Application initialized successfully');
}

// Event listeners setup
function setupEventListeners() {
    // Navbar dropdown enhancements
    setupNavbarDropdowns();

    // Search functionality
    setupSearchFunctionality();

    // Form auto-save
    setupAutoSave();

    // Keyboard shortcuts
    setupKeyboardShortcuts();

    // Window resize handler
    window.addEventListener('resize', handleWindowResize);

    // Before unload handler for unsaved changes
    window.addEventListener('beforeunload', handleBeforeUnload);
}

// Initialize Bootstrap tooltips
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Initialize Bootstrap modals
function initializeModals() {
    const modalElements = document.querySelectorAll('.modal');
    modalElements.forEach(modalEl => {
        modalEl.addEventListener('show.bs.modal', function(event) {
            // Reset form if modal contains a form
            const form = this.querySelector('form');
            if (form) {
                form.reset();
                clearFormErrors(form);
            }
        });
    });
}

// Form validation setup
function setupFormValidation() {
    const forms = document.querySelectorAll('form[novalidate]');

    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            event.preventDefault();
            event.stopPropagation();

            if (validateForm(form)) {
                // Show loading state
                showFormLoading(form);

                // Submit form (let default behavior handle actual submission)
                setTimeout(() => {
                    form.submit();
                }, 500);
            }

            form.classList.add('was-validated');
        });

        // Real-time validation
        const inputs = form.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            input.addEventListener('blur', function() {
                validateField(this);
            });

            input.addEventListener('input', function() {
                clearFieldError(this);
            });
        });
    });
}

// Form validation function
function validateForm(form) {
    let isValid = true;
    const requiredFields = form.querySelectorAll('[required]');

    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            showFieldError(field, 'This field is required');
            isValid = false;
        } else if (!validateField(field)) {
            isValid = false;
        }
    });

    return isValid;
}

// Individual field validation
function validateField(field) {
    const value = field.value.trim();
    let isValid = true;
    let errorMessage = '';

    // Email validation
    if (field.type === 'email' && value) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(value)) {
            errorMessage = 'Please enter a valid email address';
            isValid = false;
        }
    }

    // Phone validation
    if (field.type === 'tel' && value) {
        const phoneRegex = /^[\+]?[1-9][\d]{0,15}$/;
        if (!phoneRegex.test(value.replace(/\s/g, ''))) {
            errorMessage = 'Please enter a valid phone number';
            isValid = false;
        }
    }

    // Number validation
    if (field.type === 'number' && value) {
        const min = field.getAttribute('min');
        const max = field.getAttribute('max');
        const numValue = parseFloat(value);

        if (min && numValue < parseFloat(min)) {
            errorMessage = `Value must be at least ${min}`;
            isValid = false;
        } else if (max && numValue > parseFloat(max)) {
            errorMessage = `Value must not exceed ${max}`;
            isValid = false;
        }
    }

    if (!isValid) {
        showFieldError(field, errorMessage);
    } else {
        clearFieldError(field);
    }

    return isValid;
}

// Show field error
function showFieldError(field, message) {
    clearFieldError(field);

    field.classList.add('is-invalid');

    const errorDiv = document.createElement('div');
    errorDiv.className = 'invalid-feedback';
    errorDiv.textContent = message;

    field.parentNode.appendChild(errorDiv);
}

// Clear field error
function clearFieldError(field) {
    field.classList.remove('is-invalid');

    const errorDiv = field.parentNode.querySelector('.invalid-feedback');
    if (errorDiv) {
        errorDiv.remove();
    }
}

// Clear all form errors
function clearFormErrors(form) {
    const errorFields = form.querySelectorAll('.is-invalid');
    errorFields.forEach(field => {
        clearFieldError(field);
    });

    form.classList.remove('was-validated');
}

// Show form loading state
function showFormLoading(form) {
    const submitBtn = form.querySelector('button[type="submit"]');
    if (submitBtn) {
        submitBtn.disabled = true;
        const originalText = submitBtn.textContent;
        submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Processing...';

        // Store original text to restore later
        submitBtn.dataset.originalText = originalText;
    }
}

// Initialize data tables
function initializeDataTables() {
    const tables = document.querySelectorAll('.table-sortable');

    tables.forEach(table => {
        setupTableSorting(table);
        setupTableSearch(table);
    });
}

// Table sorting functionality
function setupTableSorting(table) {
    const headers = table.querySelectorAll('th[data-sortable]');

    headers.forEach(header => {
        header.style.cursor = 'pointer';
        header.innerHTML += ' <i class="fas fa-sort text-muted"></i>';

        header.addEventListener('click', function() {
            sortTable(table, this);
        });
    });
}

// Sort table function
function sortTable(table, header) {
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    const columnIndex = Array.from(header.parentNode.children).indexOf(header);
    const currentOrder = header.dataset.order || 'asc';
    const newOrder = currentOrder === 'asc' ? 'desc' : 'asc';

    // Clear all sort indicators
    table.querySelectorAll('th i').forEach(icon => {
        icon.className = 'fas fa-sort text-muted';
    });

    // Set new sort indicator
    const icon = header.querySelector('i');
    icon.className = `fas fa-sort-${newOrder === 'asc' ? 'up' : 'down'} text-primary`;
    header.dataset.order = newOrder;

    // Sort rows
    rows.sort((a, b) => {
        const aValue = a.cells[columnIndex].textContent.trim();
        const bValue = b.cells[columnIndex].textContent.trim();

        // Try to parse as numbers
        const aNum = parseFloat(aValue);
        const bNum = parseFloat(bValue);

        if (!isNaN(aNum) && !isNaN(bNum)) {
            return newOrder === 'asc' ? aNum - bNum : bNum - aNum;
        } else {
            return newOrder === 'asc' 
                ? aValue.localeCompare(bValue)
                : bValue.localeCompare(aValue);
        }
    });

    // Reorder table rows
    rows.forEach(row => tbody.appendChild(row));

    // Add animation
    tbody.style.opacity = '0.7';
    setTimeout(() => {
        tbody.style.opacity = '1';
    }, 300);
}

// Table search functionality
function setupTableSearch(table) {
    const searchInput = document.querySelector(`input[data-table-search="${table.id}"]`);
    if (!searchInput) return;

    searchInput.addEventListener('input', function() {
        const searchTerm = this.value.toLowerCase();
        const rows = table.querySelectorAll('tbody tr');

        rows.forEach(row => {
            const text = row.textContent.toLowerCase();
            if (text.includes(searchTerm)) {
                row.style.display = '';
                row.classList.add('fade-in');
            } else {
                row.style.display = 'none';
                row.classList.remove('fade-in');
            }
        });
    });
}

// Navbar dropdown enhancements
function setupNavbarDropdowns() {
    const dropdowns = document.querySelectorAll('.navbar-nav .dropdown');

    dropdowns.forEach(dropdown => {
        const toggle = dropdown.querySelector('.dropdown-toggle');
        const menu = dropdown.querySelector('.dropdown-menu');

        if (toggle && menu) {
            toggle.addEventListener('mouseenter', function() {
                if (window.innerWidth > 768) {
                    bootstrap.Dropdown.getOrCreateInstance(this).show();
                }
            });

            dropdown.addEventListener('mouseleave', function() {
                if (window.innerWidth > 768) {
                    bootstrap.Dropdown.getOrCreateInstance(toggle).hide();
                }
            });
        }
    });
}

// Search functionality
function setupSearchFunctionality() {
    const globalSearch = document.querySelector('#globalSearch');
    if (globalSearch) {
        globalSearch.addEventListener('input', debounce(handleGlobalSearch, 300));
    }
}

// Global search handler
function handleGlobalSearch(event) {
    const searchTerm = event.target.value.trim();

    if (searchTerm.length < 2) {
        hideSearchResults();
        return;
    }

    // Show loading indicator
    showSearchLoading();

    // Simulate search API call
    setTimeout(() => {
        const mockResults = generateMockSearchResults(searchTerm);
        displaySearchResults(mockResults);
    }, 500);
}

// Auto-save functionality
function setupAutoSave() {
    const forms = document.querySelectorAll('form[data-auto-save]');

    forms.forEach(form => {
        const inputs = form.querySelectorAll('input, select, textarea');

        inputs.forEach(input => {
            input.addEventListener('change', debounce(() => {
                autoSaveForm(form);
            }, 2000));
        });
    });
}

// Auto-save form data
function autoSaveForm(form) {
    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());

    // Save to localStorage
    const saveKey = `autosave_${form.id || 'form'}_${Date.now()}`;
    localStorage.setItem(saveKey, JSON.stringify(data));

    showNotification('Draft saved automatically', 'info', 2000);
}

// Keyboard shortcuts
function setupKeyboardShortcuts() {
    document.addEventListener('keydown', function(event) {
        // Ctrl/Cmd + S for save
        if ((event.ctrlKey || event.metaKey) && event.key === 's') {
            event.preventDefault();
            const activeForm = document.querySelector('form:focus-within');
            if (activeForm) {
                const submitBtn = activeForm.querySelector('button[type="submit"]');
                if (submitBtn) {
                    submitBtn.click();
                }
            }
        }

        // Escape key to close modals
        if (event.key === 'Escape') {
            const openModal = document.querySelector('.modal.show');
            if (openModal) {
                bootstrap.Modal.getInstance(openModal).hide();
            }
        }

        // Ctrl/Cmd + F for search
        if ((event.ctrlKey || event.metaKey) && event.key === 'f') {
            const searchInput = document.querySelector('#globalSearch');
            if (searchInput) {
                event.preventDefault();
                searchInput.focus();
            }
        }
    });
}

// Notification system
function initializeNotifications() {
    createNotificationContainer();

    // Check for flash messages and convert to notifications
    const flashMessages = document.querySelectorAll('.alert');
    flashMessages.forEach(alert => {
        const type = alert.classList.contains('alert-success') ? 'success' :
                    alert.classList.contains('alert-danger') ? 'error' :
                    alert.classList.contains('alert-warning') ? 'warning' : 'info';

        const message = alert.textContent.trim();
        if (message) {
            setTimeout(() => {
                showNotification(message, type);
                alert.remove();
            }, 500);
        }
    });
}

// Create notification container
function createNotificationContainer() {
    if (document.querySelector('.notification-container')) return;

    const container = document.createElement('div');
    container.className = 'notification-container position-fixed';
    container.style.cssText = 'top: 20px; right: 20px; z-index: 9999; max-width: 350px;';
    document.body.appendChild(container);
}

// Show notification
function showNotification(message, type = 'info', duration = 8000) {
    const container = document.querySelector('.notification-container');
    if (!container) return;

    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show mb-2 notification-item`;
    notification.style.cssText = 'box-shadow: 0 0.5rem 1rem rgba(0,0,0,0.15); border: none;';

    const icon = getNotificationIcon(type);
    notification.innerHTML = `
        <div class="d-flex align-items-center">
            <i class="${icon} me-2"></i>
            <span>${message}</span>
            <button type="button" class="btn-close ms-auto" data-bs-dismiss="alert"></button>
        </div>
    `;

    container.appendChild(notification);

    // Auto remove after duration
    if (duration > 0) {
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, duration);
    }

    // Add to notifications array
    notifications.push({
        message,
        type,
        timestamp: new Date(),
        id: Date.now()
    });
}

// Show message popup
function showMessagePopup(message, type = 'info', title = null, callback = null) {
    const modal = document.getElementById('messagePopupModal');
    const modalTitle = document.getElementById('messageModalTitle');
    const modalIcon = document.getElementById('messageModalIcon');
    const modalText = document.getElementById('messageModalText');
    const modalHeader = document.getElementById('messageModalHeader');
    const modalOkBtn = document.getElementById('messageModalOkBtn');

    // Set message text
    modalText.textContent = message;

    // Set title and styling based on type
    const config = getPopupConfig(type);
    modalTitle.textContent = title || config.title;
    modalIcon.className = `${config.icon} me-2`;
    modalHeader.className = `modal-header ${config.headerClass}`;
    modalOkBtn.className = `btn ${config.buttonClass}`;

    // Set callback for OK button
    modalOkBtn.onclick = function() {
        if (callback) callback();
        bootstrap.Modal.getInstance(modal).hide();
    };

    // Show modal
    const modalInstance = new bootstrap.Modal(modal);
    modalInstance.show();
}

// Show confirmation popup
function showConfirmationPopup(message, onConfirm, onCancel = null, title = 'Confirm Action') {
    const modal = document.getElementById('confirmationPopupModal');
    const modalTitle = document.getElementById('confirmationPopupModalLabel');
    const modalText = document.getElementById('confirmationModalText');
    const confirmBtn = document.getElementById('confirmationModalConfirmBtn');

    // Set content
    modalTitle.innerHTML = `<i class="fas fa-question-circle text-warning me-2"></i>${title}`;
    modalText.textContent = message;

    // Set up event handlers
    confirmBtn.onclick = function() {
        if (onConfirm) onConfirm();
        bootstrap.Modal.getInstance(modal).hide();
    };

    // Handle cancel
    modal.addEventListener('hidden.bs.modal', function() {
        if (onCancel) onCancel();
    }, { once: true });

    // Show modal
    const modalInstance = new bootstrap.Modal(modal);
    modalInstance.show();
}

// Get popup configuration based on type
function getPopupConfig(type) {
    const configs = {
        success: {
            title: 'Success',
            icon: 'fas fa-check-circle text-success',
            headerClass: 'border-success',
            buttonClass: 'btn-success'
        },
        error: {
            title: 'Error',
            icon: 'fas fa-exclamation-circle text-danger',
            headerClass: 'border-danger',
            buttonClass: 'btn-danger'
        },
        warning: {
            title: 'Warning',
            icon: 'fas fa-exclamation-triangle text-warning',
            headerClass: 'border-warning',
            buttonClass: 'btn-warning'
        },
        info: {
            title: 'Information',
            icon: 'fas fa-info-circle text-info',
            headerClass: 'border-info',
            buttonClass: 'btn-info'
        }
    };
    return configs[type] || configs.info;
}

// Get notification icon
function getNotificationIcon(type) {
    const icons = {
        success: 'fas fa-check-circle',
        error: 'fas fa-exclamation-circle',
        warning: 'fas fa-exclamation-triangle',
        info: 'fas fa-info-circle'
    };
    return icons[type] || icons.info;
}

// Notification Bell Functions
let notificationsData = [];

function addNotification(title, message, type = 'info', link = null) {
    const notification = {
        id: Date.now(),
        title: title,
        message: message,
        type: type, // info, success, warning, danger
        link: link,
        time: new Date(),
        read: false
    };
    
    notificationsData.unshift(notification);
    
    // Keep only last 10 notifications
    if (notificationsData.length > 10) {
        notificationsData = notificationsData.slice(0, 10);
    }
    
    updateNotificationBell();
    
    // Ring the bell
    const bellIcon = document.querySelector('#notificationsDropdown .fa-bell');
    if (bellIcon) {
        bellIcon.classList.add('ringing');
        setTimeout(() => bellIcon.classList.remove('ringing'), 500);
    }
}

function updateNotificationBell() {
    const notificationCount = document.getElementById('notificationCount');
    const notificationsList = document.getElementById('notificationsList');
    
    if (!notificationCount || !notificationsList) return;
    
    const unreadCount = notificationsData.filter(n => !n.read).length;
    
    // Update counter badge
    if (unreadCount > 0) {
        notificationCount.textContent = unreadCount > 9 ? '9+' : unreadCount;
        notificationCount.style.display = 'inline';
    } else {
        notificationCount.style.display = 'none';
    }
    
    // Update notifications list
    if (notificationsData.length === 0) {
        notificationsList.innerHTML = `
            <div class="dropdown-item text-center text-muted py-3">
                <i class="fas fa-inbox me-2"></i>No new notifications
            </div>
        `;
    } else {
        notificationsList.innerHTML = notificationsData.map(n => {
            const timeAgo = getTimeAgo(n.time);
            const iconClass = getNotificationIconClass(n.type);
            const unreadClass = n.read ? '' : 'unread';
            
            return `
                <div class="notification-item ${unreadClass} d-flex align-items-start gap-2" 
                     onclick="markAsRead(${n.id}); ${n.link ? `window.location.href='${n.link}';` : ''}" 
                     data-notification-id="${n.id}">
                    <div class="notification-icon ${n.type}">
                        <i class="${iconClass}"></i>
                    </div>
                    <div class="notification-content">
                        <div class="notification-title">${n.title}</div>
                        <div class="notification-text">${n.message}</div>
                        <div class="notification-time">
                            <i class="far fa-clock me-1"></i>${timeAgo}
                        </div>
                    </div>
                </div>
            `;
        }).join('');
    }
}

function getNotificationIconClass(type) {
    const icons = {
        info: 'fas fa-info-circle',
        success: 'fas fa-check-circle',
        warning: 'fas fa-exclamation-triangle',
        danger: 'fas fa-exclamation-circle'
    };
    return icons[type] || icons.info;
}

function getTimeAgo(date) {
    const seconds = Math.floor((new Date() - date) / 1000);
    
    if (seconds < 60) return 'Just now';
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
    if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
    if (seconds < 604800) return `${Math.floor(seconds / 86400)}d ago`;
    return date.toLocaleDateString();
}

function markAsRead(notificationId) {
    const notification = notificationsData.find(n => n.id === notificationId);
    if (notification) {
        notification.read = true;
        updateNotificationBell();
    }
}

function clearAllNotifications() {
    notificationsData = [];
    updateNotificationBell();
}

// Load Meera rebate notifications for Admin
function loadMeeraRebateNotifications() {
    fetch('/api/meera-rebate-notifications')
        .then(response => response.json())
        .then(data => {
            if (data.success && data.notifications) {
                // Clear existing notifications
                notificationsData = [];
                
                // Add Meera rebate notifications
                data.notifications.forEach(n => {
                    notificationsData.push({
                        id: n.id,
                        title: n.title,
                        message: n.message,
                        type: n.type,
                        link: n.link,
                        time: new Date(n.time),
                        read: false
                    });
                });
                
                updateNotificationBell();
            }
        })
        .catch(error => {
            console.error('Error loading Meera rebate notifications:', error);
        });
}

// Initialize notification system on page load
document.addEventListener('DOMContentLoaded', function() {
    // Load Meera rebate notifications for Admin
    loadMeeraRebateNotifications();
    
    // Refresh notifications every 5 minutes
    setInterval(loadMeeraRebateNotifications, 5 * 60 * 1000);
});

// Utility functions
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

function formatCurrency(amount) {
    return new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: 'INR',
        minimumFractionDigits: 2
    }).format(amount);
}

function formatDate(date) {
    return new Intl.DateTimeFormat('en-IN', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    }).format(new Date(date));
}

function formatPercentage(value, decimals = 1) {
    return `${parseFloat(value).toFixed(decimals)}%`;
}

// Theme management
function toggleTheme() {
    currentTheme = currentTheme === 'light' ? 'dark' : 'light';
    applyTheme(currentTheme);
    saveUserPreferences();
}

function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);

    // Update theme toggle button
    const themeToggle = document.querySelector('#themeToggle');
    if (themeToggle) {
        const icon = themeToggle.querySelector('i');
        if (icon) {
            icon.className = theme === 'light' ? 'fas fa-moon' : 'fas fa-sun';
        }
    }
}

// User preferences
function loadUserPreferences() {
    const preferences = localStorage.getItem('srbmc_preferences');
    if (preferences) {
        try {
            const prefs = JSON.parse(preferences);
            currentTheme = prefs.theme || 'light';
            applyTheme(currentTheme);
        } catch (e) {
            console.warn('Failed to load user preferences:', e);
        }
    }
}

function saveUserPreferences() {
    const preferences = {
        theme: currentTheme,
        lastLogin: new Date().toISOString()
    };

    localStorage.setItem('srbmc_preferences', JSON.stringify(preferences));
}

// Window resize handler
function handleWindowResize() {
    // Recalculate chart sizes if needed
    if (window.Chart && window.Chart.instances) {
        Object.values(window.Chart.instances).forEach(chart => {
            chart.resize();
        });
    }

    // Adjust table responsiveness
    const tables = document.querySelectorAll('.table-responsive');
    tables.forEach(table => {
        if (window.innerWidth < 768) {
            table.style.fontSize = '0.875rem';
        } else {
            table.style.fontSize = '';
        }
    });
}

// Before unload handler
function handleBeforeUnload(event) {
    const unsavedForms = document.querySelectorAll('form.was-validated');
    if (unsavedForms.length > 0) {
        event.preventDefault();
        event.returnValue = 'You have unsaved changes. Are you sure you want to leave?';
        return event.returnValue;
    }
}

// Export functions for global use
window.SRBMCApp = {
    showNotification,
    showMessagePopup,
    showConfirmationPopup,
    formatCurrency,
    formatDate,
    formatPercentage,
    toggleTheme,
    validateForm,
    debounce,
    clearFormErrors,
    showFormLoading
};

// Print functionality
function printPage() {
    window.print();
}

function printElement(elementId) {
    const element = document.getElementById(elementId);
    if (!element) {
        showNotification('Element not found for printing', 'error');
        return;
    }

    const printWindow = window.open('', '_blank');
    printWindow.document.write(`
        <!DOCTYPE html>
        <html>
        <head>
            <title>Print - SRBMC ERP</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
            <link href="${window.location.origin}/static/css/style.css" rel="stylesheet">
            <style>
                @media print {
                    body { margin: 0; }
                    .no-print { display: none !important; }
                }
            </style>
        </head>
        <body>
            ${element.outerHTML}
        </body>
        </html>
    `);

    printWindow.document.close();
    printWindow.onload = function() {
        printWindow.print();
        printWindow.close();
    };
}

// CSV Export functionality
function exportTableToCSV(tableId, filename = 'data.csv') {
    const table = document.getElementById(tableId);
    if (!table) {
        showNotification('Table not found for export', 'error');
        return;
    }

    const rows = table.querySelectorAll('tr');
    const csvContent = [];

    rows.forEach(row => {
        const cols = row.querySelectorAll('td, th');
        const csvRow = Array.from(cols).map(col => {
            let text = col.textContent.trim();
            // Escape quotes and wrap in quotes if contains comma
            if (text.includes(',') || text.includes('"')) {
                text = '"' + text.replace(/"/g, '""') + '"';
            }
            return text;
        });
        csvContent.push(csvRow.join(','));
    });

    const blob = new Blob([csvContent.join('\n')], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    link.click();
    window.URL.revokeObjectURL(url);

    showNotification('Data exported successfully', 'success');
}

// Initialize on page load
console.log('SRBMC ERP Main JavaScript Loaded');