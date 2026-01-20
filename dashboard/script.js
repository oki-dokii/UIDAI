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
    renderAnalyticalOutputs();
    animateMetrics();
});

/* ========================================
   Navigation System
   ======================================== */
/* ========================================
   Navigation System
   ======================================== */
/* ========================================
   Navigation System (Scroll-Spy & Smooth Scroll)
   ======================================== */
function initNavigation() {
    const navItems = document.querySelectorAll('.nav-item');

    // Click Handler: Smooth Scroll to Section
    navItems.forEach(item => {
        item.addEventListener('click', function (e) {
            e.preventDefault(); // Prevent default anchor jump if present
            const targetId = this.dataset.section;
            const targetSection = document.getElementById(targetId);

            if (targetSection) {
                targetSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
                // We let the ScrollSpy handle the visual active state update
                // to ensure perfect sync between click-scroll and manual-scroll.
            }
        });
    });

    // Initialize Scroll Spy
    initScrollSpy();
}

function initScrollSpy() {
    const sections = document.querySelectorAll('.dashboard-section');
    const navItems = document.querySelectorAll('.nav-item');

    const observerOptions = {
        root: null,
        rootMargin: '-20% 0px -60% 0px', // Trigger when section is near top/center
        threshold: 0
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const sectionId = entry.target.id;

                // Update Sidebar Visuals
                updateSidebarState(sectionId);

                // Update Page Title
                updatePageTitle(sectionId);

                // Ensure charts in this section are resized (just in case)
                // Even though they are visible, a forced layout check is good for layout shifts
                const canvasElements = entry.target.querySelectorAll('canvas');
                canvasElements.forEach(canvas => {
                    const chart = Chart.getChart(canvas);
                    if (chart) chart.resize();
                });
            }
        });
    }, observerOptions);

    sections.forEach(section => observer.observe(section));
}

// Helper to update Sidebar Visual State (Tailwind)
function updateSidebarState(activeSectionId) {
    const navItems = document.querySelectorAll('.nav-item');

    const activeClasses = ['bg-blue-50/50', 'dark:bg-blue-900/20', 'border-l-4', 'border-blue-500', 'active'];
    const inactiveClasses = ['hover:bg-slate-50', 'dark:hover:bg-slate-800/50', 'border-l-4', 'border-transparent', 'hover:border-slate-300', 'dark:hover:border-slate-600'];

    navItems.forEach(item => {
        const itemTarget = item.dataset.section;

        // Helper functions from previous scope (or defined here)
        // Re-implementing for clarity/scope safety
        const setInactive = (el) => {
            activeClasses.forEach(c => el.classList.remove(c));
            inactiveClasses.forEach(c => el.classList.add(c));
            const icon = el.querySelector('i');
            if (icon) {
                icon.classList.remove('text-blue-600', 'dark:text-blue-400');
                icon.classList.add('text-slate-400');
            }
            const text = el.querySelector('span');
            if (text) {
                text.classList.remove('text-slate-800', 'dark:text-white', 'font-bold');
                text.classList.add('text-slate-600', 'dark:text-slate-300');
            }
        };

        const setActive = (el) => {
            inactiveClasses.forEach(c => el.classList.remove(c));
            activeClasses.forEach(c => el.classList.add(c));
            const icon = el.querySelector('i');
            if (icon) {
                icon.classList.remove('text-slate-400');
                icon.classList.add('text-blue-600', 'dark:text-blue-400');
            }
            const text = el.querySelector('span');
            if (text) {
                text.classList.remove('text-slate-600', 'dark:text-slate-300');
                text.classList.add('text-slate-800', 'dark:text-white', 'font-bold');
            }
        };

        if (itemTarget === activeSectionId) {
            setActive(item);
        } else {
            setInactive(item);
        }
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
            maintainAspectRatio: false, // FIX: Lock container dimensions, prevent resize jump
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

/* ========================================
   Analytical Outputs Rendering (Curated Experience)
   ======================================== */
function renderAnalyticalOutputs() {
    const container = document.getElementById('outputsContainer');
    if (!container || !window.plotsManifest) return;

    // 1. Render Insight Highlights Strategy Strip
    const strategyHTML = `
        <div class="mb-12 bg-gradient-to-r from-slate-900 to-slate-800 rounded-2xl p-8 text-white relative overflow-hidden shadow-2xl">
            <div class="absolute top-0 right-0 w-64 h-64 bg-white/5 rounded-full blur-3xl transform translate-x-1/2 -translate-y-1/2"></div>
            <div class="relative z-10">
                <div class="flex items-center gap-3 mb-6">
                    <span class="px-3 py-1 rounded-full bg-blue-500/20 text-blue-300 border border-blue-500/30 text-xs font-bold uppercase tracking-wider">Executive Summary</span>
                    <h3 class="text-xl font-display font-bold">Key Analytical Findings</h3>
                </div>
                <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
                    <div class="space-y-2">
                        <div class="flex items-center gap-2 text-emerald-400 font-bold">
                            <i class="fas fa-check-circle"></i> <span>System Dominance</span>
                        </div>
                        <p class="text-sm text-slate-300 leading-relaxed">Biometric updates now constitute <strong class="text-white">82% of operational load</strong>, signaling a shift from enrolment to maintenance phase.</p>
                    </div>
                    <div class="space-y-2">
                        <div class="flex items-center gap-2 text-amber-400 font-bold">
                            <i class="fas fa-exclamation-triangle"></i> <span>Equity Risk</span>
                        </div>
                        <p class="text-sm text-slate-300 leading-relaxed">~60 Districts show <strong class="text-white">stagnant child updates</strong> despite high birth rates, indicating excluded populations.</p>
                    </div>
                    <div class="space-y-2">
                        <div class="flex items-center gap-2 text-blue-400 font-bold">
                            <i class="fas fa-chart-line"></i> <span>Future Trend</span>
                        </div>
                        <p class="text-sm text-slate-300 leading-relaxed">Forecasts predict a <strong class="text-white">15% surge</strong> in mandatory biometric updates in urban clusters over Q3-Q4.</p>
                    </div>
                </div>
            </div>
        </div>
    `;

    // 2. Render Navigation Chips (Sticky)
    const navHTML = `
        <div class="sticky top-[88px] z-30 bg-white/95 dark:bg-slate-900/95 backdrop-blur-md py-4 mb-8 border-b border-slate-200 dark:border-slate-800 -mx-8 px-8 flex gap-3 overflow-x-auto no-scrollbar" id="outputNav">
            ${window.plotsManifest.map((cat, idx) => `
                <button onclick="document.getElementById('cat-${idx}').scrollIntoView({behavior: 'smooth', block: 'center'})" 
                        class="whitespace-nowrap px-4 py-2 rounded-full text-sm font-medium transition-all ${idx === 0 ? 'bg-blue-600 text-white shadow-md shadow-blue-500/20' : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 hover:bg-slate-200 dark:hover:bg-slate-700'}">
                    ${cat.category}
                </button>
            `).join('')}
        </div>
    `;

    // 3. Render Categories & Plots
    const contentHTML = window.plotsManifest.map((category, idx) => {
        return `
        <div id="cat-${idx}" class="output-category scroll-mt-32 mb-16 border-b border-slate-100 dark:border-slate-800/50 pb-16 last:border-0">
            <!-- Category Header with Context -->
            <div class="flex flex-col md:flex-row md:items-start md:justify-between gap-6 mb-8 group">
                <div class="flex-1">
                    <div class="flex items-center gap-3 mb-2">
                         <div class="h-8 w-1 bg-blue-500 rounded-full group-hover:h-12 transition-all duration-300"></div>
                         <h3 class="text-2xl font-display font-bold text-slate-800 dark:text-white">${category.category}</h3>
                    </div>
                    <p class="text-slate-500 dark:text-slate-400 max-w-2xl text-lg">${category.description}</p>
                </div>
                
                <!-- Context Pill -->
                <div class="flex gap-4 text-xs bg-slate-50 dark:bg-slate-800/50 p-4 rounded-xl border border-slate-100 dark:border-slate-700">
                    <div class="space-y-1">
                        <span class="text-slate-400 uppercase tracking-wider font-bold">What</span>
                        <p class="font-medium text-slate-700 dark:text-slate-300">${category.context.what}</p>
                    </div>
                    <div class="w-px bg-slate-200 dark:bg-slate-700"></div>
                     <div class="space-y-1">
                        <span class="text-slate-400 uppercase tracking-wider font-bold">Why</span>
                        <p class="font-medium text-slate-700 dark:text-slate-300">${category.context.why}</p>
                    </div>
                     <div class="w-px bg-slate-200 dark:bg-slate-700"></div>
                     <div class="space-y-1">
                        <span class="text-slate-400 uppercase tracking-wider font-bold">When</span>
                        <p class="font-medium text-slate-700 dark:text-slate-300">${category.context.when}</p>
                    </div>
                </div>
            </div>
            
            <!-- Plot Grid -->
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 auto-rows-[minmax(300px,auto)]">
                ${category.plots.map(plot => {
            const isFeatured = plot.featured === true;
            // Prepare images list for this category for modal nav
            const catImages = JSON.stringify(category.plots.map(p => ({ src: p.path, alt: p.title, desc: p.desc })));

            return `
                    <div class="group relative bg-white dark:bg-slate-800 rounded-xl border ${isFeatured ? 'border-blue-100 dark:border-blue-900/30' : 'border-slate-200 dark:border-slate-700'} overflow-hidden hover:shadow-xl hover:shadow-blue-500/5 transition-all duration-300 ${isFeatured ? 'md:col-span-2 md:row-span-2' : ''}">
                        
                        ${isFeatured ? '<div class="absolute top-4 left-4 z-10 px-3 py-1 bg-blue-600 text-white text-xs font-bold rounded-full shadow-lg">Featured Insight</div>' : ''}

                        <!-- Image -->
                        <div class="relative w-full ${isFeatured ? 'h-[400px]' : 'h-[240px]'} bg-slate-100 dark:bg-slate-900 overflow-hidden cursor-zoom-in"
                             onclick='openImageModal("${plot.path}", "${plot.title}", "${plot.desc}")'>
                            <img src="${plot.path}" 
                                 alt="${plot.title}" 
                                 class="w-full h-full object-contain p-4 transform group-hover:scale-105 transition-transform duration-500"
                                 loading="lazy"
                                 onerror="this.parentElement.innerHTML='<div class=\'flex flex-col items-center justify-center h-full text-slate-400 bg-slate-50 dark:bg-slate-800\'><i class=\'fas fa-image-slash text-2xl mb-2 opacity-50\'></i><span class=\'text-xs font-mono opacity-50\'>${plot.path.split('/').pop()}</span></div>'">
                        </div>
                        
                        <!-- Descriptor -->
                        <div class="p-6 border-t border-slate-100 dark:border-slate-700/50 h-full">
                            <h4 class="${isFeatured ? 'text-xl' : 'text-base'} font-bold text-slate-800 dark:text-white mb-2 group-hover:text-blue-600 transition-colors">
                                ${plot.title}
                            </h4>
                            <p class="text-sm text-slate-500 dark:text-slate-400 leading-relaxed mb-4">
                                ${plot.desc || 'Analytical output visualizing key trend metrics.'}
                            </p>
                             <button class="text-xs font-bold text-blue-600 dark:text-blue-400 hover:underline flex items-center gap-1 mt-auto"
                                onclick='openImageModal("${plot.path}", "${plot.title}", "${plot.desc}")'>
                                View Analysis <i class="fas fa-arrow-right transform group-hover:translate-x-1 transition-transform"></i>
                            </button>
                        </div>
                    </div>
                `}).join('')}
            </div>
        </div>
    `}).join('');

    container.innerHTML = strategyHTML + navHTML + contentHTML;
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

    tbody.innerHTML = states.map(s => {
        // Conditional Logic
        const gapColor = s.childGap < -0.2 ? 'text-red-600 dark:text-red-400 font-bold' : 'text-slate-600 dark:text-slate-400';
        const intensityColor = s.intensity > 1.2 ? 'text-emerald-600 dark:text-emerald-400 font-bold' : 'text-slate-600 dark:text-slate-400';

        return `
        <tr class="hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors border-b border-slate-100 dark:border-slate-800 last:border-0">
            <td class="px-6 py-4">
                <div class="font-semibold text-slate-800 dark:text-white">${s.state}</div>
            </td>
            <td class="px-6 py-4 text-right font-mono text-sm text-slate-600 dark:text-slate-400 tabular-nums">${formatNumber(s.enrol)}</td>
            <td class="px-6 py-4 text-right font-mono text-sm text-slate-600 dark:text-slate-400 tabular-nums">${formatNumber(s.demo)}</td>
            <td class="px-6 py-4 text-right font-mono text-sm text-slate-600 dark:text-slate-400 tabular-nums">${formatNumber(s.bio)}</td>
            <td class="px-6 py-4 text-right font-mono text-sm font-semibold text-blue-600 dark:text-blue-400 tabular-nums bg-blue-50/30 dark:bg-blue-900/10">${formatNumber(s.total)}</td>
            <td class="px-6 py-4 text-right font-mono text-sm tabular-nums ${gapColor}">${(s.childGap * 100).toFixed(1)}%</td>
            <td class="px-6 py-4 text-right font-mono text-sm tabular-nums ${intensityColor}">${s.intensity.toFixed(2)}</td>
        </tr>
    `}).join('');
}

function populateCriticalTable() {
    const tbody = document.getElementById('criticalTableBody');
    if (!tbody) return;

    const critical = window.dashboardData.critical;

    tbody.innerHTML = critical.map(d => {
        // Severity Logic
        let severityClass = d.severity === 'Critical' ? 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400' : 'bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-300';
        let icon = d.severity === 'Critical' ? '<i class="fas fa-exclamation-circle mr-1"></i>' : '<i class="fas fa-exclamation-triangle mr-1"></i>';

        return `
        <tr class="hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors border-b border-slate-100 dark:border-slate-800 last:border-0">
            <td class="px-6 py-4 font-mono text-sm text-slate-400 dark:text-slate-500">#${d.rank}</td>
            <td class="px-6 py-4">
                <div class="font-bold text-slate-800 dark:text-white">${d.district}</div>
                <div class="text-xs text-slate-500 dark:text-slate-400 font-medium uppercase tracking-wide">${d.state}</div>
            </td>
            <td class="px-6 py-4 text-right">
                <span class="font-mono font-bold text-red-600 dark:text-red-400 text-base">${(d.gap * 100).toFixed(1)}%</span>
            </td>
            <td class="px-6 py-4">
                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${severityClass}">
                    ${icon} ${d.severity}
                </span>
            </td>
            <td class="px-6 py-4 text-sm text-slate-600 dark:text-slate-300">
                <div class="flex items-center gap-2">
                    <i class="fas fa-arrow-right text-blue-500 text-xs"></i>
                    ${d.recommendation.replace('Increase', 'Boost').replace('Immediate', 'Urgent')}
                </div>
            </td>
        </tr>
    `}).join('');
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

function openImageModal(src, alt, desc = '') {
    const modal = document.getElementById('imageModal');
    const img = document.getElementById('modalImage');
    const caption = document.getElementById('modalCaption');

    img.src = src;
    img.alt = alt;

    // Rich Caption
    caption.innerHTML = `
        <div class="flex flex-col gap-1">
            <span class="text-lg font-bold text-gray-900">${alt}</span>
            ${desc ? `<span class="text-sm text-gray-500">${desc}</span>` : ''}
        </div>
    `;

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
        <div class="text-center py-6 border-b border-slate-100 dark:border-slate-700/50 mb-6">
            <div class="metric-detail-value text-5xl font-display font-bold text-blue-600 dark:text-blue-400 tracking-tight">${detail.value}</div>
            <p class="metric-detail-desc text-slate-500 dark:text-slate-400 mt-2 max-w-md mx-auto text-sm leading-relaxed">${detail.description}</p>
        </div>
        
        <div class="metric-breakdown space-y-3">
            <h4 class="text-xs font-bold text-slate-400 dark:text-slate-500 uppercase tracking-widest mb-4 flex items-center gap-2">
                <i class="fas fa-layer-group text-slate-300"></i> Component Analysis
            </h4>
            ${detail.breakdown.map(b => `
                <div class="breakdown-item group flex items-center justify-between p-4 rounded-xl bg-slate-50 dark:bg-slate-800/50 hover:bg-white dark:hover:bg-slate-800 border border-transparent hover:border-slate-200 dark:hover:border-slate-700 hover:shadow-md transition-all duration-200 cursor-default">
                    <div class="flex items-center gap-3">
                        <div class="w-1.5 h-1.5 rounded-full bg-slate-300 dark:bg-slate-600 group-hover:bg-blue-500 transition-colors"></div>
                        <span class="text-sm font-medium text-slate-600 dark:text-slate-300 group-hover:text-slate-900 dark:group-hover:text-white transition-colors">${b.label}</span>
                    </div>
                    <span class="font-mono font-bold text-slate-800 dark:text-white text-base bg-white dark:bg-slate-900/50 px-3 py-1 rounded-lg border border-slate-100 dark:border-slate-700/50 group-hover:border-blue-100 dark:group-hover:border-blue-900/30 transition-colors">${b.value}</span>
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
