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
    const tables = document.querySelectorAll('.table');
    
    tables.forEach(table => {
        setupTableInteractions(table);
        setupTableSearch(table);
    });
}

// Enhanced table interactions
function setupTableInteractions(table) {
    // Add hover effects to sortable headers
    const sortableHeaders = table.querySelectorAll('.sortable-header');
    
    sortableHeaders.forEach(header => {
        header.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-1px)';
        });
        
        header.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
        
        // Add click feedback
        header.addEventListener('click', function() {
            showSortingFeedback(this);
        });
    });
    
    // Add row hover effects
    const rows = table.querySelectorAll('tbody tr');
    rows.forEach(row => {
        row.addEventListener('mouseenter', function() {
            this.classList.add('table-row-hover');
        });
        
        row.addEventListener('mouseleave', function() {
            this.classList.remove('table-row-hover');
        });
    });
}

// Show sorting feedback
function showSortingFeedback(header) {
    // Add loading class temporarily
    const table = header.closest('table');
    table.classList.add('sort-transition');
    
    // Remove after transition
    setTimeout(() => {
        table.classList.remove('sort-transition');
    }, 300);
    
    // Show notification for sort action
    const columnName = header.querySelector('span')?.textContent || 'Column';
    const icon = header.querySelector('i');
    let direction = 'ascending';
    
    if (icon && icon.classList.contains('fa-sort-down')) {
        direction = 'descending';
    }
    
    // Small visual feedback
    header.style.background = 'rgba(78, 115, 223, 0.1)';
    setTimeout(() => {
        header.style.background = '';
    }, 200);
}

// Enhanced client-side sorting for tables without server-side sorting
function setupClientSideSorting(table) {
    const headers = table.querySelectorAll('.sortable-header');
    
    headers.forEach((header, index) => {
        // Skip if already has server-side sorting link
        if (header.querySelector('a[href*="sort="]')) return;
        
        header.style.cursor = 'pointer';
        header.addEventListener('click', function() {
            sortTableClientSide(table, index);
        });
    });
}

// Client-side table sorting
function sortTableClientSide(table, columnIndex) {
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    const header = table.querySelectorAll('.sortable-header')[columnIndex];
    const currentOrder = header.dataset.order || 'asc';
    const newOrder = currentOrder === 'asc' ? 'desc' : 'asc';
    
    // Clear all sort indicators
    table.querySelectorAll('.sortable-header i').forEach(icon => {
        icon.className = 'fas fa-sort text-muted';
    });
    
    // Set new sort indicator
    const icon = header.querySelector('i');
    if (icon) {
        icon.className = `fas fa-sort-${newOrder === 'asc' ? 'up' : 'down'} text-primary`;
    }
    header.dataset.order = newOrder;
    
    // Sort rows
    rows.sort((a, b) => {
        const aCell = a.cells[columnIndex];
        const bCell = b.cells[columnIndex];
        
        if (!aCell || !bCell) return 0;
        
        const aValue = aCell.textContent.trim();
        const bValue = bCell.textContent.trim();
        
        // Try to parse as numbers
        const aNum = parseFloat(aValue.replace(/[^0-9.-]/g, ''));
        const bNum = parseFloat(bValue.replace(/[^0-9.-]/g, ''));
        
        if (!isNaN(aNum) && !isNaN(bNum)) {
            return newOrder === 'asc' ? aNum - bNum : bNum - aNum;
        } else {
            return newOrder === 'asc' 
                ? aValue.localeCompare(bValue)
                : bValue.localeCompare(aValue);
        }
    });
    
    // Add loading state
    tbody.style.opacity = '0.7';
    tbody.style.transition = 'opacity 0.3s ease';
    
    // Reorder table rows with animation
    setTimeout(() => {
        rows.forEach(row => tbody.appendChild(row));
        tbody.style.opacity = '1';
        
        // Add stagger animation to rows
        rows.forEach((row, index) => {
            row.style.animationDelay = `${index * 20}ms`;
            row.classList.add('fade-in');
        });
    }, 150);
}

// Improved table search with highlighting
function setupTableSearch(table) {
    const searchInput = document.querySelector(`input[data-table-search="${table.id}"]`);
    if (!searchInput) return;
    
    searchInput.addEventListener('input', function() {
        const searchTerm = this.value.toLowerCase();
        const rows = table.querySelectorAll('tbody tr');
        let visibleCount = 0;
        
        rows.forEach(row => {
            const text = row.textContent.toLowerCase();
            const isVisible = searchTerm === '' || text.includes(searchTerm);
            
            if (isVisible) {
                row.style.display = '';
                row.classList.add('fade-in');
                visibleCount++;
                
                // Highlight search terms
                if (searchTerm) {
                    highlightSearchTerm(row, searchTerm);
                } else {
                    removeHighlight(row);
                }
            } else {
                row.style.display = 'none';
                row.classList.remove('fade-in');
            }
        });
        
        // Update visible count if there's a counter
        const counter = table.querySelector('.search-results-count');
        if (counter) {
            counter.textContent = `${visibleCount} results found`;
        }
    });
}

// Highlight search terms
function highlightSearchTerm(row, term) {
    const cells = row.querySelectorAll('td');
    cells.forEach(cell => {
        if (cell.querySelector('.btn-group')) return; // Skip action columns
        
        const originalText = cell.textContent;
        const regex = new RegExp(`(${term})`, 'gi');
        const highlightedText = originalText.replace(regex, '<mark class="bg-warning">$1</mark>');
        
        if (highlightedText !== originalText) {
            cell.innerHTML = highlightedText;
        }
    });
}

// Remove highlighting
function removeHighlight(row) {
    const marks = row.querySelectorAll('mark');
    marks.forEach(mark => {
        mark.outerHTML = mark.textContent;
    });
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
function showNotification(message, type = 'info', duration = 5000) {
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
