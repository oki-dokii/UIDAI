/* ========================================
   UIDAI Analytics Dashboard - JavaScript
   Interactive Navigation & Features
   ======================================== */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize Dashboard
    initNavigation();
    initChartActions();
    initImageModal();
});

/* ========================================
   Navigation System
   ======================================== */
function initNavigation() {
    const navItems = document.querySelectorAll('.nav-item');
    const sections = document.querySelectorAll('.dashboard-section');
    
    navItems.forEach(item => {
        item.addEventListener('click', function() {
            const targetSection = this.dataset.section;
            
            // Update active nav item
            navItems.forEach(nav => nav.classList.remove('active'));
            this.classList.add('active');
            
            // Update active section
            sections.forEach(section => {
                section.classList.remove('active');
                if (section.id === targetSection) {
                    section.classList.add('active');
                    // Scroll to top of section
                    window.scrollTo({ top: 0, behavior: 'smooth' });
                }
            });
            
            // Update page title based on section
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
        'advanced': 'Advanced Analytics'
    };
    
    const pageTitle = document.querySelector('.page-title');
    if (pageTitle && titles[sectionId]) {
        pageTitle.textContent = titles[sectionId];
    }
}

/* ========================================
   Chart Actions (Download & Fullscreen)
   ======================================== */
function initChartActions() {
    // Download buttons
    document.querySelectorAll('.btn-icon[title="Download"]').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.stopPropagation();
            const chartContainer = this.closest('.chart-container');
            const img = chartContainer.querySelector('.chart-image');
            if (img) {
                downloadImage(img.src, img.alt || 'chart');
            }
        });
    });
    
    // Fullscreen buttons
    document.querySelectorAll('.btn-icon[title="Fullscreen"]').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.stopPropagation();
            const chartContainer = this.closest('.chart-container');
            const img = chartContainer.querySelector('.chart-image');
            if (img) {
                openImageModal(img.src, img.alt);
            }
        });
    });
}

function downloadImage(src, filename) {
    const link = document.createElement('a');
    link.href = src;
    link.download = filename.replace(/[^a-z0-9]/gi, '_') + '.png';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

/* ========================================
   Image Modal (Lightbox)
   ======================================== */
function initImageModal() {
    // Create modal element
    const modal = document.createElement('div');
    modal.className = 'image-modal';
    modal.innerHTML = `
        <div class="modal-overlay"></div>
        <div class="modal-content">
            <button class="modal-close">&times;</button>
            <img class="modal-image" src="" alt="">
            <p class="modal-caption"></p>
        </div>
    `;
    document.body.appendChild(modal);
    
    // Add modal styles
    const modalStyles = document.createElement('style');
    modalStyles.textContent = `
        .image-modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: 1000;
        }
        
        .image-modal.active {
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .modal-overlay {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.9);
            backdrop-filter: blur(4px);
        }
        
        .modal-content {
            position: relative;
            max-width: 90%;
            max-height: 90%;
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        
        .modal-close {
            position: absolute;
            top: -40px;
            right: -40px;
            width: 40px;
            height: 40px;
            border: none;
            background: rgba(255, 255, 255, 0.1);
            color: white;
            font-size: 24px;
            border-radius: 50%;
            cursor: pointer;
            transition: all 0.2s;
        }
        
        .modal-close:hover {
            background: rgba(255, 255, 255, 0.2);
            transform: scale(1.1);
        }
        
        .modal-image {
            max-width: 100%;
            max-height: 80vh;
            border-radius: 8px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
        }
        
        .modal-caption {
            color: rgba(255, 255, 255, 0.8);
            margin-top: 16px;
            font-size: 14px;
            text-align: center;
        }
    `;
    document.head.appendChild(modalStyles);
    
    // Close modal on overlay click
    modal.querySelector('.modal-overlay').addEventListener('click', closeImageModal);
    modal.querySelector('.modal-close').addEventListener('click', closeImageModal);
    
    // Close on escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') closeImageModal();
    });
    
    // Click on images to enlarge
    document.querySelectorAll('.chart-image').forEach(img => {
        img.style.cursor = 'pointer';
        img.addEventListener('click', function() {
            openImageModal(this.src, this.alt);
        });
    });
}

function openImageModal(src, alt) {
    const modal = document.querySelector('.image-modal');
    const modalImage = modal.querySelector('.modal-image');
    const modalCaption = modal.querySelector('.modal-caption');
    
    modalImage.src = src;
    modalImage.alt = alt;
    modalCaption.textContent = alt;
    
    modal.classList.add('active');
    document.body.style.overflow = 'hidden';
}

function closeImageModal() {
    const modal = document.querySelector('.image-modal');
    modal.classList.remove('active');
    document.body.style.overflow = '';
}

/* ========================================
   Utility Functions
   ======================================== */

// Smooth scroll to element
function scrollToElement(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}

// Format large numbers
function formatNumber(num) {
    if (num >= 1e9) return (num / 1e9).toFixed(1) + 'B';
    if (num >= 1e6) return (num / 1e6).toFixed(1) + 'M';
    if (num >= 1e3) return (num / 1e3).toFixed(1) + 'K';
    return num.toString();
}

// Debounce function for performance
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

/* ========================================
   Animation on Scroll
   ======================================== */
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const fadeInObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
        }
    });
}, observerOptions);

// Apply animations to cards and charts
document.querySelectorAll('.metric-card, .chart-container, .insights-panel').forEach(el => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(20px)';
    el.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
    fadeInObserver.observe(el);
});

/* ========================================
   Print Functionality
   ======================================== */
function printDashboard() {
    window.print();
}

// Add print button if needed
// document.querySelector('.header-right').innerHTML += '<button onclick="printDashboard()" class="btn-icon" title="Print"><i class="fas fa-print"></i></button>';
