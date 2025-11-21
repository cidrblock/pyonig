// Dashboard Application - Main JavaScript
'use strict';

// Configuration
const CONFIG = {
    apiEndpoint: '/api/v1',
    refreshInterval: 30000,
    maxRetries: 3,
    timeout: 5000
};

// API Service
class APIService {
    constructor(baseURL) {
        this.baseURL = baseURL;
        this.retryCount = 0;
    }

    async fetchMetrics() {
        try {
            const response = await fetch(`${this.baseURL}/metrics`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.getToken()}`
                },
                timeout: CONFIG.timeout
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            this.retryCount = 0;
            return data;
        } catch (error) {
            console.error('Error fetching metrics:', error);
            
            if (this.retryCount < CONFIG.maxRetries) {
                this.retryCount++;
                console.log(`Retrying... (${this.retryCount}/${CONFIG.maxRetries})`);
                await this.sleep(1000 * this.retryCount);
                return this.fetchMetrics();
            }
            
            throw error;
        }
    }

    getToken() {
        return localStorage.getItem('auth_token') || '';
    }

    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}

// Dashboard Controller
class Dashboard {
    constructor() {
        this.api = new APIService(CONFIG.apiEndpoint);
        this.metrics = {};
        this.charts = {};
        this.updateInterval = null;
    }

    async init() {
        console.log('Initializing dashboard...');
        
        try {
            await this.loadMetrics();
            this.renderMetrics();
            this.setupEventListeners();
            this.startAutoRefresh();
            
            console.log('Dashboard initialized successfully');
        } catch (error) {
            console.error('Failed to initialize dashboard:', error);
            this.showError('Failed to load dashboard data');
        }
    }

    async loadMetrics() {
        const data = await this.api.fetchMetrics();
        this.metrics = {
            users: data.users || 0,
            revenue: data.revenue || 0,
            requests: data.requests || 0,
            uptime: data.uptime || 0
        };
    }

    renderMetrics() {
        const metricCards = document.querySelectorAll('.metric-card');
        
        metricCards.forEach((card, index) => {
            const metric = Object.values(this.metrics)[index];
            const metricElement = card.querySelector('.metric');
            
            if (metricElement) {
                this.animateValue(metricElement, 0, metric, 1000);
            }
        });
    }

    animateValue(element, start, end, duration) {
        const startTime = performance.now();
        
        const updateValue = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            const currentValue = Math.floor(start + (end - start) * progress);
            element.textContent = this.formatNumber(currentValue);
            
            if (progress < 1) {
                requestAnimationFrame(updateValue);
            }
        };
        
        requestAnimationFrame(updateValue);
    }

    formatNumber(num) {
        if (num >= 1000000) {
            return (num / 1000000).toFixed(1) + 'M';
        } else if (num >= 1000) {
            return (num / 1000).toFixed(1) + 'K';
        }
        return num.toString();
    }

    setupEventListeners() {
        // Refresh button
        const refreshBtn = document.getElementById('refresh-btn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.handleRefresh());
        }

        // Export button
        const exportBtn = document.getElementById('export-btn');
        if (exportBtn) {
            exportBtn.addEventListener('click', () => this.handleExport());
        }

        // Theme toggle
        const themeToggle = document.getElementById('theme-toggle');
        if (themeToggle) {
            themeToggle.addEventListener('change', (e) => {
                this.toggleTheme(e.target.checked);
            });
        }

        // Handle visibility change
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.stopAutoRefresh();
            } else {
                this.startAutoRefresh();
            }
        });
    }

    async handleRefresh() {
        console.log('Refreshing dashboard...');
        
        try {
            await this.loadMetrics();
            this.renderMetrics();
            this.showSuccess('Dashboard refreshed successfully');
        } catch (error) {
            this.showError('Failed to refresh dashboard');
        }
    }

    handleExport() {
        const data = JSON.stringify(this.metrics, null, 2);
        const blob = new Blob([data], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        
        const link = document.createElement('a');
        link.href = url;
        link.download = `dashboard-metrics-${Date.now()}.json`;
        link.click();
        
        URL.revokeObjectURL(url);
        this.showSuccess('Metrics exported successfully');
    }

    toggleTheme(isDark) {
        document.body.classList.toggle('dark-theme', isDark);
        localStorage.setItem('theme', isDark ? 'dark' : 'light');
    }

    startAutoRefresh() {
        if (this.updateInterval) {
            return;
        }
        
        this.updateInterval = setInterval(() => {
            this.loadMetrics().then(() => {
                this.renderMetrics();
            }).catch(error => {
                console.error('Auto-refresh failed:', error);
            });
        }, CONFIG.refreshInterval);
        
        console.log(`Auto-refresh started (${CONFIG.refreshInterval}ms)`);
    }

    stopAutoRefresh() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
            this.updateInterval = null;
            console.log('Auto-refresh stopped');
        }
    }

    showError(message) {
        this.showNotification(message, 'error');
    }

    showSuccess(message) {
        this.showNotification(message, 'success');
    }

    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.classList.add('show');
        }, 10);
        
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }

    destroy() {
        this.stopAutoRefresh();
        console.log('Dashboard destroyed');
    }
}

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => {
    const dashboard = new Dashboard();
    dashboard.init();
    
    // Store reference for debugging
    window.dashboard = dashboard;
});

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { Dashboard, APIService };
}

