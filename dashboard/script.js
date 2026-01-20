/* ========================================
   UIDAI Analytics Dashboard - Enhanced Script
   Interactive Charts & Functionality
   ======================================== */

// Chart instances storage
let charts = {};

document.addEventListener('DOMContentLoaded', function () {
    // Initialize all components
    initNavigation();
    initCharts();
    initTables();
    initTabNavigation();
    initModals();
    animateMetrics();
});

/* ========================================
   Navigation System
   ======================================== */
function initNavigation() {
    const navItems = document.querySelectorAll('.nav-item');
    const sections = document.querySelectorAll('.dashboard-section');

    navItems.forEach(item => {
        item.addEventListener('click', function () {
            const targetSection = this.dataset.section;

            // Update active nav item
            navItems.forEach(nav => nav.classList.remove('active'));
            this.classList.add('active');

            // Update active section
            sections.forEach(section => {
                section.classList.remove('active');
                if (section.id === targetSection) {
                    section.classList.add('active');
                    window.scrollTo({ top: 0, behavior: 'smooth' });
                }
            });

            // Update page title
            updatePageTitle(targetSection);
        });
    });
}

function updatePageTitle(sectionId) {
    const titles = {
        'overview': 'System Overview',
        'temporal': 'Temporal Analysis',
        'spatial': 'Spatial Patterns',
        'demographic': 'Demographic Equity',
        'clusters': 'District Clustering',
        'advanced': 'Advanced Analytics',
        'data': 'Data Tables'
    };

    const pageTitle = document.querySelector('.page-title');
    if (pageTitle && titles[sectionId]) {
        pageTitle.textContent = titles[sectionId];
    }
}

/* ========================================
   Chart Initialization
   ======================================== */
function initCharts() {
    // Set Chart.js defaults
    Chart.defaults.font.family = "'Inter', sans-serif";
    Chart.defaults.color = '#5f6368';

    createCompositionChart();
    createStateVolumeChart();
    createMonthlyTrendChart();
    createStateComparisonChart();
    createChildGapChart();
    createClusterPieChart();
    createCorrelationChart();
}

// Composition Donut Chart
function createCompositionChart() {
    const ctx = document.getElementById('compositionChart');
    if (!ctx) return;

    const data = window.dashboardData.kpi;

    charts.composition = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Demographic Updates', 'Biometric Updates', 'Enrolments'],
            datasets: [{
                data: [data.totalDemoUpdates, data.totalBioUpdates, data.totalEnrolments],
                backgroundColor: ['#fb8c00', '#673ab7', '#1a73e8'],
                borderWidth: 0,
                hoverOffset: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            cutout: '65%',
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: { padding: 20, usePointStyle: true }
                },
                tooltip: {
                    callbacks: {
                        label: function (context) {
                            const value = context.parsed;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const pct = ((value / total) * 100).toFixed(1);
                            return `${context.label}: ${formatNumber(value)} (${pct}%)`;
                        }
                    }
                }
            }
        }
    });
}

// State Volume Bar Chart
function createStateVolumeChart() {
    const ctx = document.getElementById('stateVolumeChart');
    if (!ctx) return;

    const states = window.dashboardData.states.slice(0, 10);

    charts.stateVolume = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: states.map(s => s.state),
            datasets: [
                {
                    label: 'Demographic',
                    data: states.map(s => s.demo),
                    backgroundColor: '#fb8c00',
                    borderRadius: 4
                },
                {
                    label: 'Biometric',
                    data: states.map(s => s.bio),
                    backgroundColor: '#673ab7',
                    borderRadius: 4
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            indexAxis: 'y',
            scales: {
                x: {
                    stacked: true,
                    grid: { display: false },
                    ticks: {
                        callback: function (value) {
                            return formatNumber(value);
                        }
                    }
                },
                y: {
                    stacked: true,
                    grid: { display: false }
                }
            },
            plugins: {
                legend: { position: 'top' },
                tooltip: {
                    callbacks: {
                        label: function (context) {
                            return `${context.dataset.label}: ${formatNumber(context.parsed.x)}`;
                        }
                    }
                }
            }
        }
    });
}

// Monthly Trend Line Chart
function createMonthlyTrendChart() {
    const ctx = document.getElementById('monthlyTrendChart');
    if (!ctx) return;

    const monthly = window.dashboardData.monthly;

    charts.monthlyTrend = new Chart(ctx, {
        type: 'line',
        data: {
            labels: monthly.labels,
            datasets: [
                {
                    label: 'Demographic Updates (Millions)',
                    data: monthly.demographic,
                    borderColor: '#fb8c00',
                    backgroundColor: 'rgba(251, 140, 0, 0.1)',
                    fill: true,
                    tension: 0.4,
                    pointRadius: 6,
                    pointHoverRadius: 8
                },
                {
                    label: 'Biometric Updates (Millions)',
                    data: monthly.biometric,
                    borderColor: '#673ab7',
                    backgroundColor: 'rgba(103, 58, 183, 0.1)',
                    fill: true,
                    tension: 0.4,
                    pointRadius: 6,
                    pointHoverRadius: 8
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                intersect: false,
                mode: 'index'
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: { display: true, text: 'Updates (Millions)' }
                }
            },
            plugins: {
                legend: { position: 'top' },
                tooltip: {
                    callbacks: {
                        label: function (context) {
                            return `${context.dataset.label}: ${context.parsed.y}M`;
                        }
                    }
                }
            }
        }
    });
}

// State Comparison Chart
function createStateComparisonChart() {
    const ctx = document.getElementById('stateComparisonChart');
    if (!ctx) return;

    const states = window.dashboardData.states;

    charts.stateComparison = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: states.map(s => s.state),
            datasets: [{
                label: 'Total Updates',
                data: states.map(s => s.total),
                backgroundColor: '#1a73e8',
                borderRadius: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function (value) {
                            return formatNumber(value);
                        }
                    }
                },
                x: {
                    ticks: { maxRotation: 45, minRotation: 45 }
                }
            },
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: function (context) {
                            return `Updates: ${formatNumber(context.parsed.y)}`;
                        }
                    }
                }
            }
        }
    });
}

// Child Gap Chart
function createChildGapChart() {
    const ctx = document.getElementById('childGapChart');
    if (!ctx) return;

    const states = window.dashboardData.states.sort((a, b) => a.childGap - b.childGap);

    charts.childGap = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: states.map(s => s.state),
            datasets: [{
                label: 'Child Attention Gap',
                data: states.map(s => s.childGap * 100),
                backgroundColor: states.map(s =>
                    s.childGap < -0.3 ? '#ea4335' :
                        s.childGap < -0.2 ? '#fb8c00' :
                            s.childGap < -0.1 ? '#f9ab00' : '#34a853'
                ),
                borderRadius: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            indexAxis: 'y',
            scales: {
                x: {
                    title: { display: true, text: 'Gap (%)' },
                    ticks: {
                        callback: function (value) {
                            return value + '%';
                        }
                    }
                }
            },
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: function (context) {
                            return `Gap: ${context.parsed.x.toFixed(1)}%`;
                        }
                    }
                }
            }
        }
    });
}

// Cluster Pie Chart
function createClusterPieChart() {
    const ctx = document.getElementById('clusterPieChart');
    if (!ctx) return;

    const clusters = window.dashboardData.clusters;

    charts.clusterPie = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: ['Enrolment Frontiers', 'Mature Systems', 'High Verification', 'Dormant'],
            datasets: [{
                data: clusters.values,
                backgroundColor: clusters.colors,
                borderWidth: 2,
                borderColor: '#fff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'right',
                    labels: { padding: 20, usePointStyle: true }
                },
                tooltip: {
                    callbacks: {
                        label: function (context) {
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const pct = ((context.parsed / total) * 100).toFixed(1);
                            return `${context.label}: ${context.parsed} districts (${pct}%)`;
                        }
                    }
                }
            }
        }
    });
}

// Correlation Chart
function createCorrelationChart() {
    const ctx = document.getElementById('correlationChart');
    if (!ctx) return;

    const states = window.dashboardData.states;

    charts.correlation = new Chart(ctx, {
        type: 'scatter',
        data: {
            datasets: [{
                label: 'States',
                data: states.map(s => ({
                    x: s.intensity,
                    y: s.childGap * 100,
                    label: s.state
                })),
                backgroundColor: '#1a73e8',
                pointRadius: 8,
                pointHoverRadius: 12
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            scales: {
                x: {
                    title: { display: true, text: 'Update Intensity' }
                },
                y: {
                    title: { display: true, text: 'Child Attention Gap (%)' }
                }
            },
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: function (context) {
                            const point = context.raw;
                            return `${point.label}: Intensity ${point.x.toFixed(1)}, Gap ${point.y.toFixed(1)}%`;
                        }
                    }
                }
            }
        }
    });
}

/* ========================================
   Chart Interactions
   ======================================== */
function toggleChartType(chartId) {
    const chart = charts.composition;
    if (!chart) return;

    const newType = chart.config.type === 'doughnut' ? 'bar' : 'doughnut';
    chart.config.type = newType;

    if (newType === 'bar') {
        chart.options.cutout = undefined;
        chart.options.indexAxis = 'y';
    } else {
        chart.options.cutout = '65%';
        chart.options.indexAxis = undefined;
    }

    chart.update();
}

function updateTrendChart() {
    const metric = document.getElementById('trendMetric').value;
    const chart = charts.monthlyTrend;
    if (!chart) return;

    const monthly = window.dashboardData.monthly;

    if (metric === 'demographic') {
        chart.data.datasets[0].hidden = false;
        chart.data.datasets[1].hidden = true;
    } else if (metric === 'biometric') {
        chart.data.datasets[0].hidden = true;
        chart.data.datasets[1].hidden = false;
    } else {
        chart.data.datasets[0].hidden = false;
        chart.data.datasets[1].hidden = false;
    }

    chart.update();
}

function updateStateChart() {
    const metric = document.getElementById('stateMetric').value;
    const chart = charts.stateComparison;
    if (!chart) return;

    const states = window.dashboardData.states;

    let data, label, color;
    switch (metric) {
        case 'demographic':
            data = states.map(s => s.demo);
            label = 'Demographic Updates';
            color = '#fb8c00';
            break;
        case 'biometric':
            data = states.map(s => s.bio);
            label = 'Biometric Updates';
            color = '#673ab7';
            break;
        case 'intensity':
            data = states.map(s => s.intensity);
            label = 'Update Intensity';
            color = '#34a853';
            break;
        default:
            data = states.map(s => s.total);
            label = 'Total Updates';
            color = '#1a73e8';
    }

    chart.data.datasets[0].data = data;
    chart.data.datasets[0].label = label;
    chart.data.datasets[0].backgroundColor = color;
    chart.update();
}

function downloadChart(chartId) {
    const chart = charts[chartId.replace('Chart', '').toLowerCase()] ||
        charts[chartId.charAt(0).toLowerCase() + chartId.slice(1).replace('Chart', '')];

    if (!chart) {
        console.log('Chart not found:', chartId);
        return;
    }

    const link = document.createElement('a');
    link.download = `${chartId}.png`;
    link.href = chart.toBase64Image();
    link.click();
}

/* ========================================
   Table Initialization
   ======================================== */
function initTables() {
    populateStateTable();
    populateCriticalTable();
}

function populateStateTable() {
    const tbody = document.getElementById('stateTableBody');
    if (!tbody) return;

    const states = window.dashboardData.states;

    tbody.innerHTML = states.map(s => `
        <tr>
            <td><strong>${s.state}</strong></td>
            <td>${formatNumber(s.enrol)}</td>
            <td>${formatNumber(s.demo)}</td>
            <td>${formatNumber(s.bio)}</td>
            <td>${formatNumber(s.total)}</td>
            <td class="${s.childGap < -0.3 ? 'danger' : s.childGap < -0.2 ? 'warning' : ''}">${(s.childGap * 100).toFixed(1)}%</td>
            <td>${s.intensity.toFixed(2)}</td>
        </tr>
    `).join('');
}

function populateCriticalTable() {
    const tbody = document.getElementById('criticalTableBody');
    if (!tbody) return;

    const critical = window.dashboardData.critical;

    tbody.innerHTML = critical.map(d => `
        <tr>
            <td><strong>${d.rank}</strong></td>
            <td>${d.state}</td>
            <td>${d.district}</td>
            <td class="danger">${(d.gap * 100).toFixed(1)}%</td>
            <td><span class="badge danger">${d.severity}</span></td>
            <td>${d.recommendation}</td>
        </tr>
    `).join('');
}

/* ========================================
   Tab Navigation
   ======================================== */
function initTabNavigation() {
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.table-container');

    tabBtns.forEach(btn => {
        btn.addEventListener('click', function () {
            const targetTab = this.dataset.tab;

            tabBtns.forEach(b => b.classList.remove('active'));
            this.classList.add('active');

            tabContents.forEach(content => {
                content.classList.remove('active');
                if (content.id === targetTab) {
                    content.classList.add('active');
                }
            });
        });
    });
}

/* ========================================
   Modal Functions
   ======================================== */
function initModals() {
    // Close modals on escape
    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape') {
            closeImageModal();
            closeCriticalModal();
            closeMetricModal();
        }
    });
}

function openImageModal(src, alt) {
    const modal = document.getElementById('imageModal');
    const img = document.getElementById('modalImage');
    const caption = document.getElementById('modalCaption');

    img.src = src;
    img.alt = alt;
    caption.textContent = alt;

    modal.classList.add('active');
    document.body.style.overflow = 'hidden';
}

function closeImageModal() {
    const modal = document.getElementById('imageModal');
    if (modal) {
        modal.classList.remove('active');
        document.body.style.overflow = '';
    }
}

function showCriticalDistricts() {
    const modal = document.getElementById('criticalModal');
    const body = document.getElementById('criticalModalBody');

    const critical = window.dashboardData.critical.slice(0, 10);

    body.innerHTML = `
        <p class="modal-description">Districts with most severe child attention gaps requiring immediate intervention:</p>
        <div class="critical-list">
            ${critical.map(d => `
                <div class="critical-item">
                    <div class="critical-rank">#${d.rank}</div>
                    <div class="critical-info">
                        <strong>${d.district}</strong>
                        <span>${d.state}</span>
                    </div>
                    <div class="critical-gap">${(d.gap * 100).toFixed(1)}%</div>
                </div>
            `).join('')}
        </div>
        <button class="btn-primary full-width" onclick="navigateToData()">
            <i class="fas fa-table"></i> View Full Data
        </button>
    `;

    modal.classList.add('active');
    document.body.style.overflow = 'hidden';
}

function closeCriticalModal() {
    const modal = document.getElementById('criticalModal');
    if (modal) {
        modal.classList.remove('active');
        document.body.style.overflow = '';
    }
}

function showMetricDetail(metricKey) {
    const modal = document.getElementById('metricModal');
    const title = document.getElementById('metricModalTitle');
    const body = document.getElementById('metricModalBody');

    const detail = window.dashboardData.metricDetails[metricKey];
    if (!detail) return;

    title.textContent = detail.title;

    body.innerHTML = `
        <div class="metric-detail-value">${detail.value}</div>
        <p class="metric-detail-desc">${detail.description}</p>
        <div class="metric-breakdown">
            <h4>Breakdown</h4>
            ${detail.breakdown.map(b => `
                <div class="breakdown-item">
                    <span class="breakdown-label">${b.label}</span>
                    <span class="breakdown-value">${b.value}</span>
                </div>
            `).join('')}
        </div>
    `;

    modal.classList.add('active');
    document.body.style.overflow = 'hidden';
}

function closeMetricModal() {
    const modal = document.getElementById('metricModal');
    if (modal) {
        modal.classList.remove('active');
        document.body.style.overflow = '';
    }
}

/* ========================================
   Utility Functions
   ======================================== */
function formatNumber(num) {
    if (num >= 1e9) return (num / 1e9).toFixed(1) + 'B';
    if (num >= 1e6) return (num / 1e6).toFixed(1) + 'M';
    if (num >= 1e3) return (num / 1e3).toFixed(1) + 'K';
    return num.toLocaleString();
}

function animateMetrics() {
    const values = document.querySelectorAll('.metric-value');
    values.forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(10px)';
        setTimeout(() => {
            el.style.transition = 'all 0.5s ease';
            el.style.opacity = '1';
            el.style.transform = 'translateY(0)';
        }, Math.random() * 300);
    });
}

function refreshData() {
    // Animate refresh button
    const btn = document.querySelector('.btn-refresh i');
    btn.classList.add('fa-spin');

    // Refresh charts
    Object.values(charts).forEach(chart => {
        if (chart && chart.update) {
            chart.update();
        }
    });

    setTimeout(() => {
        btn.classList.remove('fa-spin');
    }, 1000);
}

function exportDashboard() {
    alert('Export functionality would generate a PDF report of all visualizations and data.');
}

function exportTableCSV(tableId) {
    const table = document.getElementById(tableId);
    if (!table) return;

    let csv = [];
    const rows = table.querySelectorAll('tr');

    rows.forEach(row => {
        const cols = row.querySelectorAll('td, th');
        const rowData = Array.from(cols).map(col => col.textContent.trim());
        csv.push(rowData.join(','));
    });

    const csvContent = csv.join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = `${tableId}.csv`;
    link.click();
}

function navigateToData() {
    closeCriticalModal();

    // Switch to data section
    document.querySelectorAll('.nav-item').forEach(nav => nav.classList.remove('active'));
    document.querySelector('[data-section="data"]').classList.add('active');

    document.querySelectorAll('.dashboard-section').forEach(sec => sec.classList.remove('active'));
    document.getElementById('data').classList.add('active');

    // Switch to critical tab
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelector('[data-tab="criticalTable"]').classList.add('active');

    document.querySelectorAll('.table-container').forEach(tc => tc.classList.remove('active'));
    document.getElementById('criticalTable').classList.add('active');

    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function filterByCluster(clusterId) {
    console.log(`Filtering by cluster ${clusterId}`);
    // This would filter the data table to show only districts in the selected cluster
    alert(`Showing districts in Cluster ${clusterId}. This feature requires cluster data integration.`);
}

function downloadImage(src, filename) {
    const link = document.createElement('a');
    link.href = src;
    link.download = filename + '.png';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}
