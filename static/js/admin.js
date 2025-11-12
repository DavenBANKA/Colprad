// Admin-specific JavaScript

// Real-time dashboard updates
function updateDashboardStats() {
    fetch('/api/dashboard/stats')
        .then(response => response.json())
        .then(data => {
            // Update stats if elements exist
            const totalOrders = document.getElementById('total-orders');
            const totalRevenue = document.getElementById('total-revenue');
            
            if (totalOrders) totalOrders.textContent = data.total_orders;
            if (totalRevenue) totalRevenue.textContent = data.total_revenue.toLocaleString() + ' FCFA';
        })
        .catch(error => console.error('Error updating stats:', error));
}

// Auto-refresh dashboard every 30 seconds
if (window.location.pathname.includes('/admin/dashboard')) {
    setInterval(updateDashboardStats, 30000);
}

// Confirm delete actions
document.querySelectorAll('[data-confirm-delete]').forEach(element => {
    element.addEventListener('click', function(e) {
        if (!confirm('Êtes-vous sûr de vouloir supprimer cet élément ?')) {
            e.preventDefault();
        }
    });
});

// Export functionality with loading state
document.querySelectorAll('[data-export]').forEach(button => {
    button.addEventListener('click', function() {
        const originalText = button.innerHTML;
        button.disabled = true;
        button.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Export en cours...';
        
        setTimeout(() => {
            button.disabled = false;
            button.innerHTML = originalText;
        }, 2000);
    });
});

// Search functionality for tables
function initTableSearch(inputId, tableId) {
    const searchInput = document.getElementById(inputId);
    const table = document.getElementById(tableId);
    
    if (!searchInput || !table) return;
    
    searchInput.addEventListener('keyup', function() {
        const filter = this.value.toLowerCase();
        const rows = table.querySelectorAll('tbody tr');
        
        rows.forEach(row => {
            const text = row.textContent.toLowerCase();
            row.style.display = text.includes(filter) ? '' : 'none';
        });
    });
}

// Initialize search for participants table
initTableSearch('search-participants', 'participants-table');

// Chart initialization (if Chart.js is loaded)
function initSalesChart(canvasId, data) {
    const canvas = document.getElementById(canvasId);
    if (!canvas || typeof Chart === 'undefined') return;
    
    new Chart(canvas, {
        type: 'line',
        data: {
            labels: data.labels,
            datasets: [{
                label: 'Ventes',
                data: data.values,
                borderColor: '#0E5E96',
                backgroundColor: 'rgba(14, 94, 150, 0.1)',
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

// Bulk actions for tables
function initBulkActions() {
    const selectAll = document.getElementById('select-all');
    const checkboxes = document.querySelectorAll('.row-checkbox');
    const bulkActions = document.getElementById('bulk-actions');
    
    if (!selectAll || !checkboxes.length) return;
    
    selectAll.addEventListener('change', function() {
        checkboxes.forEach(cb => cb.checked = this.checked);
        updateBulkActionsVisibility();
    });
    
    checkboxes.forEach(cb => {
        cb.addEventListener('change', updateBulkActionsVisibility);
    });
    
    function updateBulkActionsVisibility() {
        const checkedCount = document.querySelectorAll('.row-checkbox:checked').length;
        if (bulkActions) {
            bulkActions.style.display = checkedCount > 0 ? 'block' : 'none';
        }
    }
}

initBulkActions();

// Auto-save form data to localStorage
function initAutoSave(formId) {
    const form = document.getElementById(formId);
    if (!form) return;
    
    // Load saved data
    const savedData = localStorage.getItem(formId);
    if (savedData) {
        const data = JSON.parse(savedData);
        Object.keys(data).forEach(key => {
            const input = form.querySelector(`[name="${key}"]`);
            if (input) input.value = data[key];
        });
    }
    
    // Save on input
    form.addEventListener('input', function() {
        const formData = new FormData(form);
        const data = {};
        formData.forEach((value, key) => data[key] = value);
        localStorage.setItem(formId, JSON.stringify(data));
    });
    
    // Clear on submit
    form.addEventListener('submit', function() {
        localStorage.removeItem(formId);
    });
}

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + K for search
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        const searchInput = document.querySelector('input[type="search"], input[placeholder*="Rechercher"]');
        if (searchInput) searchInput.focus();
    }
    
    // Ctrl/Cmd + S to save (prevent default and trigger form submit)
    if ((e.ctrlKey || e.metaKey) && e.key === 's') {
        e.preventDefault();
        const form = document.querySelector('form');
        if (form) form.requestSubmit();
    }
});

// Status badge colors
function updateStatusBadges() {
    document.querySelectorAll('.status-badge').forEach(badge => {
        const status = badge.textContent.toLowerCase().trim();
        badge.classList.remove('bg-success', 'bg-warning', 'bg-danger', 'bg-secondary');
        
        if (status.includes('complet') || status.includes('success') || status.includes('résolu')) {
            badge.classList.add('bg-success');
        } else if (status.includes('pending') || status.includes('en cours')) {
            badge.classList.add('bg-warning');
        } else if (status.includes('failed') || status.includes('error') || status.includes('ouvert')) {
            badge.classList.add('bg-danger');
        } else {
            badge.classList.add('bg-secondary');
        }
    });
}

updateStatusBadges();
