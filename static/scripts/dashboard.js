/**
 * Priority Care - Dashboard Page JavaScript
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize dashboard
    loadDashboardData();
    
    // Refresh stats every 30 seconds (simulated)
    setInterval(refreshStats, 30000);
});

/**
 * Load dashboard data
 */
function loadDashboardData() {
    // Calculate stats from the recent patients table
    calculateStats();
    
    // Animate stat cards on load
    animateStats();
    
    console.log('Dashboard data loaded');
}

/**
 * Calculate statistics from the recent patients table
 */
function calculateStats() {
    const rows = document.querySelectorAll('#recentPatientsTable tr');
    
    let totalPatients = rows.length;
    let redCount = 0;
    let yellowCount = 0;
    let greenCount = 0;
    
    rows.forEach(row => {
        const badge = row.querySelector('.badge');
        if (badge) {
            const triageLevel = badge.textContent.trim();
            if (triageLevel === 'RED') redCount++;
            else if (triageLevel === 'YELLOW') yellowCount++;
            else if (triageLevel === 'GREEN') greenCount++;
        }
    });
    
    // Update the stat cards with calculated values
    const totalElement = document.getElementById('totalPatients');
    const redElement = document.getElementById('redPatients');
    
    if (totalElement) totalElement.textContent = totalPatients;
    if (redElement) redElement.textContent = redCount;
    
    console.log('Stats calculated:', { totalPatients, redCount, yellowCount, greenCount });
}

/**
 * Animate stat values on page load
 */
function animateStats() {
    const statValues = document.querySelectorAll('.stat-value');
    
    statValues.forEach(stat => {
        const finalValue = parseInt(stat.textContent);
        let currentValue = 0;
        const increment = Math.ceil(finalValue / 20);
        
        const timer = setInterval(() => {
            currentValue += increment;
            if (currentValue >= finalValue) {
                stat.textContent = finalValue;
                clearInterval(timer);
            } else {
                stat.textContent = currentValue;
            }
        }, 50);
    });
}

/**
 * Refresh dashboard stats
 */
function refreshStats() {
    console.log('Refreshing stats...');
    // In a real application, this would fetch updated data from an API
}

/**
 * Filter table by triage level (if needed)
 */
function filterByTriage(level) {
    const rows = document.querySelectorAll('#recentPatientsTable tr');
    
    rows.forEach(row => {
        if (level === 'all') {
            row.style.display = '';
        } else {
            const badge = row.querySelector('.badge');
            if (badge && badge.textContent === level) {
                row.style.display = '';
            } else {
                row.style.display = 'none';
            }
        }
    });
}
