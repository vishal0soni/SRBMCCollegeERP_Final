// SRBMC College Management ERP - Charts JavaScript
// Chart.js initialization and management for analytics dashboards

// Global chart instances storage
window.analyticsCharts = {};

// Chart.js default configuration
Chart.defaults.font.family = "'Nunito', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif";
Chart.defaults.color = '#5a5c69';
Chart.defaults.borderColor = '#e3e6f0';

// Color palette for charts
const chartColors = {
    primary: '#4e73df',
    success: '#1cc88a',
    info: '#36b9cc',
    warning: '#f6c23e',
    danger: '#e74a3b',
    secondary: '#858796',
    light: '#f8f9fc',
    dark: '#5a5c69',
    college: {
        primary: '#2c5282',
        secondary: '#1a365d',
        accent: '#3182ce'
    }
};

// Chart color schemes
const colorSchemes = {
    default: [
        chartColors.primary,
        chartColors.success,
        chartColors.info,
        chartColors.warning,
        chartColors.danger,
        chartColors.secondary
    ],
    college: [
        chartColors.college.primary,
        chartColors.college.accent,
        chartColors.success,
        chartColors.warning,
        chartColors.info,
        chartColors.danger
    ],
    gradient: [
        '#667eea',
        '#764ba2',
        '#f093fb',
        '#f5576c',
        '#4facfe',
        '#00f2fe'
    ]
};

// Initialize all analytics charts
function initializeAnalyticsCharts() {
    console.log('Initializing analytics charts...');
    
    // Student enrollment trends
    initEnrollmentChart();
    
    // Course distribution
    initCourseDistributionChart();
    
    // Grade distribution
    initGradeDistributionChart();
    
    // Subject performance
    initSubjectPerformanceChart();
    
    // Fee collection trends
    initFeeCollectionChart();
    
    // Payment mode analysis
    initPaymentModeChart();
    
    // Scholarship distribution
    initScholarshipChart();
    
    // Gender demographics
    initGenderChart();
    
    // Category demographics
    initCategoryChart();
    
    // Attendance trends
    initAttendanceChart();
    
    console.log('All charts initialized successfully');
}

// Student Enrollment Trends Chart
function initEnrollmentChart() {
    const ctx = document.getElementById('enrollmentChart');
    if (!ctx) return;
    
    const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    
    window.analyticsCharts.enrollmentChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: monthNames,
            datasets: [{
                label: 'New Enrollments',
                data: [12, 19, 15, 25, 30, 45, 40, 35, 28, 22, 18, 15],
                borderColor: chartColors.college.primary,
                backgroundColor: chartColors.college.primary + '20',
                tension: 0.4,
                fill: true
            }, {
                label: 'Total Students',
                data: [145, 164, 179, 204, 234, 279, 319, 354, 382, 404, 422, 437],
                borderColor: chartColors.success,
                backgroundColor: chartColors.success + '20',
                tension: 0.4,
                fill: false
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                },
                title: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: chartColors.borderColor
                    }
                },
                x: {
                    grid: {
                        color: chartColors.borderColor
                    }
                }
            },
            interaction: {
                intersect: false,
                mode: 'index'
            }
        }
    });
}

// Course Distribution Chart
function initCourseDistributionChart() {
    const ctx = document.getElementById('courseDistribution');
    if (!ctx) return;
    
    window.analyticsCharts.courseDistribution = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Bachelor of Arts', 'Bachelor of Science', 'Master of Arts', 'Other'],
            datasets: [{
                data: [145, 100, 35, 20],
                backgroundColor: colorSchemes.college,
                borderWidth: 2,
                borderColor: '#fff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 20,
                        usePointStyle: true
                    }
                }
            },
            cutout: '60%'
        }
    });
}

// Grade Distribution Analysis Chart
function initGradeDistributionChart() {
    const ctx = document.getElementById('gradeDistribution');
    if (!ctx) return;
    
    window.analyticsCharts.gradeDistribution = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['A+', 'A', 'B+', 'B', 'C+', 'C', 'F'],
            datasets: [{
                label: 'Number of Students',
                data: [25, 45, 38, 28, 15, 8, 4],
                backgroundColor: [
                    chartColors.success,
                    chartColors.success + 'CC',
                    chartColors.info,
                    chartColors.info + 'CC',
                    chartColors.warning,
                    chartColors.warning + 'CC',
                    chartColors.danger
                ],
                borderWidth: 0,
                borderRadius: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: chartColors.borderColor
                    }
                },
                x: {
                    grid: {
                        display: false
                    }
                }
            }
        }
    });
}

// Subject Performance Chart
function initSubjectPerformanceChart() {
    const ctx = document.getElementById('subjectPerformance');
    if (!ctx) return;
    
    window.analyticsCharts.subjectPerformance = new Chart(ctx, {
        type: 'radar',
        data: {
            labels: ['English', 'Hindi', 'Mathematics', 'History', 'Political Science', 'Economics'],
            datasets: [{
                label: 'Average Score (%)',
                data: [78, 82, 65, 75, 73, 70],
                borderColor: chartColors.college.primary,
                backgroundColor: chartColors.college.primary + '30',
                pointBackgroundColor: chartColors.college.primary,
                pointBorderColor: '#fff',
                pointHoverBackgroundColor: '#fff',
                pointHoverBorderColor: chartColors.college.primary
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                r: {
                    beginAtZero: true,
                    max: 100,
                    grid: {
                        color: chartColors.borderColor
                    },
                    pointLabels: {
                        font: {
                            size: 12
                        }
                    }
                }
            }
        }
    });
}

// Fee Collection Trends Chart
function initFeeCollectionChart() {
    const ctx = document.getElementById('feeCollectionChart');
    if (!ctx) return;
    
    const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    
    window.analyticsCharts.feeCollectionChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: monthNames,
            datasets: [{
                label: 'Fees Collected (₹)',
                data: [45000, 52000, 48000, 61000, 55000, 67000, 72000, 58000, 64000, 70000, 0, 0],
                borderColor: chartColors.success,
                backgroundColor: chartColors.success + '20',
                tension: 0.4,
                fill: true
            }, {
                label: 'Target (₹)',
                data: [50000, 50000, 50000, 50000, 50000, 50000, 50000, 50000, 50000, 50000, 50000, 50000],
                borderColor: chartColors.warning,
                backgroundColor: 'transparent',
                borderDash: [5, 5],
                tension: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return '₹' + value.toLocaleString();
                        }
                    },
                    grid: {
                        color: chartColors.borderColor
                    }
                },
                x: {
                    grid: {
                        color: chartColors.borderColor
                    }
                }
            },
            interaction: {
                intersect: false,
                mode: 'index'
            }
        }
    });
}

// Payment Mode Chart
function initPaymentModeChart() {
    const ctx = document.getElementById('paymentModeChart');
    if (!ctx) return;
    
    window.analyticsCharts.paymentModeChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Cash', 'Online', 'Cheque', 'DD'],
            datasets: [{
                data: [65, 25, 8, 2],
                backgroundColor: [
                    chartColors.primary,
                    chartColors.success,
                    chartColors.info,
                    chartColors.warning
                ],
                borderWidth: 2,
                borderColor: '#fff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 15,
                        usePointStyle: true
                    }
                }
            },
            cutout: '50%'
        }
    });
}

// Scholarship Distribution Chart
function initScholarshipChart() {
    const ctx = document.getElementById('scholarshipChart');
    if (!ctx) return;
    
    window.analyticsCharts.scholarshipChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Government Scholarship', 'Meera Rebate', 'Merit Scholarship', 'Need-based Aid'],
            datasets: [{
                label: 'Applied',
                data: [85, 65, 25, 15],
                backgroundColor: chartColors.info + '80',
                borderColor: chartColors.info,
                borderWidth: 1
            }, {
                label: 'Approved',
                data: [72, 58, 20, 12],
                backgroundColor: chartColors.success + '80',
                borderColor: chartColors.success,
                borderWidth: 1
            }, {
                label: 'Rejected',
                data: [13, 7, 5, 3],
                backgroundColor: chartColors.danger + '80',
                borderColor: chartColors.danger,
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    stacked: false,
                    grid: {
                        color: chartColors.borderColor
                    }
                },
                x: {
                    grid: {
                        display: false
                    }
                }
            }
        }
    });
}

// Gender Distribution Chart
function initGenderChart() {
    const ctx = document.getElementById('genderChart');
    if (!ctx) return;
    
    window.analyticsCharts.genderChart = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: ['Male', 'Female', 'Other'],
            datasets: [{
                data: [145, 98, 2],
                backgroundColor: [
                    chartColors.primary,
                    '#e91e63',
                    chartColors.secondary
                ],
                borderWidth: 2,
                borderColor: '#fff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 10,
                        usePointStyle: true,
                        font: {
                            size: 10
                        }
                    }
                }
            }
        }
    });
}

// Category Distribution Chart
function initCategoryChart() {
    const ctx = document.getElementById('categoryChart');
    if (!ctx) return;
    
    window.analyticsCharts.categoryChart = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: ['General', 'OBC', 'SC', 'ST'],
            datasets: [{
                data: [125, 85, 25, 10],
                backgroundColor: [
                    chartColors.success,
                    chartColors.warning,
                    chartColors.info,
                    chartColors.danger
                ],
                borderWidth: 2,
                borderColor: '#fff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 10,
                        usePointStyle: true,
                        font: {
                            size: 10
                        }
                    }
                }
            }
        }
    });
}

// Attendance Trends Chart
function initAttendanceChart() {
    const ctx = document.getElementById('attendanceChart');
    if (!ctx) return;
    
    const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    
    window.analyticsCharts.attendanceChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: monthNames,
            datasets: [{
                label: 'BA Students',
                data: [95, 94, 96, 93, 94, 95, 92, 94, 95, 96, 0, 0],
                borderColor: chartColors.college.primary,
                backgroundColor: chartColors.college.primary + '20',
                tension: 0.4
            }, {
                label: 'BSC Students',
                data: [93, 95, 94, 96, 95, 93, 94, 95, 93, 94, 0, 0],
                borderColor: chartColors.success,
                backgroundColor: chartColors.success + '20',
                tension: 0.4
            }, {
                label: 'Overall Average',
                data: [94, 94.5, 95, 94.5, 94.5, 94, 93, 94.5, 94, 95, 0, 0],
                borderColor: chartColors.warning,
                backgroundColor: 'transparent',
                borderWidth: 3,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top'
                }
            },
            scales: {
                y: {
                    beginAtZero: false,
                    min: 85,
                    max: 100,
                    ticks: {
                        callback: function(value) {
                            return value + '%';
                        }
                    },
                    grid: {
                        color: chartColors.borderColor
                    }
                },
                x: {
                    grid: {
                        color: chartColors.borderColor
                    }
                }
            },
            interaction: {
                intersect: false,
                mode: 'index'
            }
        }
    });
}

// Dashboard-specific chart initializations
function initDashboardCharts() {
    // Course Chart for Dashboard
    const courseCtx = document.getElementById('courseChart');
    if (courseCtx) {
        window.analyticsCharts.dashboardCourseChart = new Chart(courseCtx, {
            type: 'doughnut',
            data: {
                labels: ['BA', 'BSC', 'MA', 'Others'],
                datasets: [{
                    data: [145, 100, 35, 20],
                    backgroundColor: colorSchemes.college
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }

    // Fee Chart for Dashboard
    const feeCtx = document.getElementById('feeChart');
    if (feeCtx) {
        const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                           'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
        
        window.analyticsCharts.dashboardFeeChart = new Chart(feeCtx, {
            type: 'line',
            data: {
                labels: monthNames,
                datasets: [{
                    label: 'Fee Collections (₹)',
                    data: [45000, 52000, 48000, 61000, 55000, 67000, 
                           72000, 58000, 64000, 70000, 0, 0],
                    borderColor: chartColors.success,
                    backgroundColor: chartColors.success + '20',
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return '₹' + value.toLocaleString();
                            }
                        }
                    }
                }
            }
        });
    }
}

// Student Summary Charts
function initStudentSummaryCharts() {
    // Course Distribution Chart
    const courseDistributionCtx = document.getElementById('courseDistributionChart');
    if (courseDistributionCtx) {
        window.analyticsCharts.studentCourseDistribution = new Chart(courseDistributionCtx, {
            type: 'doughnut',
            data: {
                labels: ['Bachelor of Arts', 'Bachelor of Science', 'Master of Arts'],
                datasets: [{
                    data: [145, 100, 35],
                    backgroundColor: colorSchemes.college
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }

    // Gender Distribution Chart
    const genderDistributionCtx = document.getElementById('genderDistributionChart');
    if (genderDistributionCtx) {
        window.analyticsCharts.studentGenderDistribution = new Chart(genderDistributionCtx, {
            type: 'pie',
            data: {
                labels: ['Male', 'Female', 'Other'],
                datasets: [{
                    data: [145, 98, 2],
                    backgroundColor: [chartColors.primary, '#e91e63', chartColors.secondary]
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }

    // Category Distribution Chart
    const categoryDistributionCtx = document.getElementById('categoryDistributionChart');
    if (categoryDistributionCtx) {
        window.analyticsCharts.studentCategoryDistribution = new Chart(categoryDistributionCtx, {
            type: 'bar',
            data: {
                labels: ['General', 'OBC', 'SC', 'ST'],
                datasets: [{
                    label: 'Students',
                    data: [125, 85, 25, 10],
                    backgroundColor: chartColors.college.primary
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }

    // Monthly Admissions Chart
    const monthlyAdmissionsCtx = document.getElementById('monthlyAdmissionsChart');
    if (monthlyAdmissionsCtx) {
        const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                           'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
        
        window.analyticsCharts.monthlyAdmissions = new Chart(monthlyAdmissionsCtx, {
            type: 'line',
            data: {
                labels: monthNames,
                datasets: [{
                    label: 'Admissions',
                    data: [12, 19, 15, 25, 30, 45, 40, 35, 28, 22, 18, 15],
                    borderColor: chartColors.success,
                    backgroundColor: chartColors.success + '20',
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }
}

// Fee Management Charts
function initFeeManagementCharts() {
    // Monthly Collection Chart
    const monthlyCollectionCtx = document.getElementById('monthlyCollectionChart');
    if (monthlyCollectionCtx) {
        window.analyticsCharts.feeMonthlyCollection = new Chart(monthlyCollectionCtx, {
            type: 'line',
            data: {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
                datasets: [{
                    label: 'Collection (₹)',
                    data: [45000, 52000, 48000, 61000, 55000, 67000, 72000, 58000, 64000, 70000, 0, 0],
                    borderColor: chartColors.success,
                    backgroundColor: chartColors.success + '20',
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return '₹' + value.toLocaleString();
                            }
                        }
                    }
                }
            }
        });
    }

    // Payment Mode Chart
    const paymentModeCtx = document.getElementById('paymentModeChart');
    if (paymentModeCtx) {
        window.analyticsCharts.feePaymentMode = new Chart(paymentModeCtx, {
            type: 'doughnut',
            data: {
                labels: ['Cash', 'Online', 'Cheque', 'DD'],
                datasets: [{
                    data: [65, 25, 8, 2],
                    backgroundColor: [chartColors.primary, chartColors.success, chartColors.info, chartColors.warning]
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }
}

// Exam Charts
function initExamCharts() {
    // Grade Distribution Chart
    const gradeDistributionCtx = document.getElementById('gradeDistributionChart');
    if (gradeDistributionCtx) {
        window.analyticsCharts.examGradeDistribution = new Chart(gradeDistributionCtx, {
            type: 'doughnut',
            data: {
                labels: ['A+', 'A', 'B+', 'B', 'C+', 'C', 'F'],
                datasets: [{
                    data: [15, 22, 18, 12, 8, 5, 3],
                    backgroundColor: [
                        chartColors.success, chartColors.success + 'CC', chartColors.info, 
                        chartColors.info + 'CC', chartColors.warning, chartColors.warning + 'CC', 
                        chartColors.danger
                    ]
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }

    // Subject Performance Chart
    const subjectPerformanceCtx = document.getElementById('subjectPerformanceChart');
    if (subjectPerformanceCtx) {
        window.analyticsCharts.examSubjectPerformance = new Chart(subjectPerformanceCtx, {
            type: 'bar',
            data: {
                labels: ['English', 'Hindi', 'Mathematics', 'History', 'Political Science'],
                datasets: [{
                    label: 'Average Score (%)',
                    data: [78, 82, 65, 75, 73],
                    backgroundColor: chartColors.college.primary
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100
                    }
                }
            }
        });
    }
}

// Chart utility functions
function updateChartData(chartId, newData) {
    const chart = window.analyticsCharts[chartId];
    if (chart) {
        chart.data = newData;
        chart.update();
    }
}

function destroyChart(chartId) {
    const chart = window.analyticsCharts[chartId];
    if (chart) {
        chart.destroy();
        delete window.analyticsCharts[chartId];
    }
}

function resizeAllCharts() {
    Object.values(window.analyticsCharts).forEach(chart => {
        if (chart && typeof chart.resize === 'function') {
            chart.resize();
        }
    });
}

// Export chart as image
function exportChartAsImage(chartId, filename = 'chart.png') {
    const chart = window.analyticsCharts[chartId];
    if (chart) {
        const url = chart.toBase64Image();
        const link = document.createElement('a');
        link.download = filename;
        link.href = url;
        link.click();
    }
}

// Initialize charts based on current page
function initPageSpecificCharts() {
    const currentPage = window.location.pathname;
    
    if (currentPage.includes('/dashboard')) {
        initDashboardCharts();
    } else if (currentPage.includes('/students/summary')) {
        initStudentSummaryCharts();
    } else if (currentPage.includes('/fees')) {
        initFeeManagementCharts();
    } else if (currentPage.includes('/exams')) {
        initExamCharts();
    } else if (currentPage.includes('/analytics')) {
        initializeAnalyticsCharts();
    }
}

// Handle window resize for chart responsiveness
window.addEventListener('resize', function() {
    setTimeout(resizeAllCharts, 300);
});

// Initialize charts when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initPageSpecificCharts();
});

// Export functions for global use
window.chartUtils = {
    initializeAnalyticsCharts,
    initDashboardCharts,
    initStudentSummaryCharts,
    initFeeManagementCharts,
    initExamCharts,
    updateChartData,
    destroyChart,
    resizeAllCharts,
    exportChartAsImage,
    chartColors,
    colorSchemes
};

console.log('SRBMC ERP Charts JavaScript Loaded');
