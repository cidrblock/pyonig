// TypeScript Dashboard Application
// Modern type-safe implementation

interface MetricData {
    users: number;
    revenue: number;
    requests: number;
    uptime: number;
    timestamp: Date;
}

interface APIConfig {
    endpoint: string;
    timeout: number;
    maxRetries: number;
    headers?: Record<string, string>;
}

interface ChartConfig {
    type: 'line' | 'bar' | 'pie' | 'doughnut';
    data: number[];
    labels: string[];
    options?: ChartOptions;
}

interface ChartOptions {
    responsive: boolean;
    maintainAspectRatio: boolean;
    animation?: AnimationConfig;
}

interface AnimationConfig {
    duration: number;
    easing: 'linear' | 'easeInOut' | 'easeIn' | 'easeOut';
}

type NotificationType = 'success' | 'error' | 'warning' | 'info';

enum MetricType {
    USERS = 'users',
    REVENUE = 'revenue',
    REQUESTS = 'requests',
    UPTIME = 'uptime'
}

class APIError extends Error {
    constructor(
        message: string,
        public statusCode: number,
        public response?: any
    ) {
        super(message);
        this.name = 'APIError';
    }
}

class DashboardAPI {
    private config: APIConfig;
    private retryCount: number = 0;

    constructor(config: APIConfig) {
        this.config = config;
    }

    async fetchMetrics(): Promise<MetricData> {
        try {
            const response = await this.makeRequest<MetricData>('/metrics');
            this.retryCount = 0;
            return {
                ...response,
                timestamp: new Date()
            };
        } catch (error) {
            if (this.retryCount < this.config.maxRetries) {
                this.retryCount++;
                await this.sleep(1000 * this.retryCount);
                return this.fetchMetrics();
            }
            throw error;
        }
    }

    private async makeRequest<T>(path: string): Promise<T> {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), this.config.timeout);

        try {
            const response = await fetch(`${this.config.endpoint}${path}`, {
                headers: {
                    'Content-Type': 'application/json',
                    ...this.config.headers
                },
                signal: controller.signal
            });

            if (!response.ok) {
                throw new APIError(
                    `HTTP error! status: ${response.status}`,
                    response.status,
                    await response.json()
                );
            }

            return await response.json();
        } finally {
            clearTimeout(timeoutId);
        }
    }

    private sleep(ms: number): Promise<void> {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}

class MetricsRenderer {
    private metrics: MetricData | null = null;

    render(metrics: MetricData): void {
        this.metrics = metrics;
        this.renderCards();
        this.renderCharts();
    }

    private renderCards(): void {
        if (!this.metrics) return;

        const cards = document.querySelectorAll<HTMLElement>('.metric-card');
        const values = Object.values(this.metrics) as number[];

        cards.forEach((card, index) => {
            const metricElement = card.querySelector<HTMLElement>('.metric');
            if (metricElement) {
                this.animateValue(metricElement, 0, values[index], 1000);
            }
        });
    }

    private renderCharts(): void {
        // Chart rendering logic would go here
        console.log('Rendering charts with data:', this.metrics);
    }

    private animateValue(
        element: HTMLElement,
        start: number,
        end: number,
        duration: number
    ): void {
        const startTime = performance.now();

        const update = (currentTime: number): void => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            const easeProgress = this.easeInOutCubic(progress);

            const currentValue = Math.floor(start + (end - start) * easeProgress);
            element.textContent = this.formatNumber(currentValue);

            if (progress < 1) {
                requestAnimationFrame(update);
            }
        };

        requestAnimationFrame(update);
    }

    private easeInOutCubic(t: number): number {
        return t < 0.5
            ? 4 * t * t * t
            : 1 - Math.pow(-2 * t + 2, 3) / 2;
    }

    private formatNumber(num: number): string {
        if (num >= 1_000_000) {
            return `${(num / 1_000_000).toFixed(1)}M`;
        } else if (num >= 1_000) {
            return `${(num / 1_000).toFixed(1)}K`;
        }
        return num.toString();
    }
}

class NotificationService {
    private container: HTMLElement;

    constructor() {
        this.container = this.createContainer();
    }

    private createContainer(): HTMLElement {
        const container = document.createElement('div');
        container.className = 'notification-container';
        document.body.appendChild(container);
        return container;
    }

    show(message: string, type: NotificationType = 'info'): void {
        const notification = this.createNotification(message, type);
        this.container.appendChild(notification);

        setTimeout(() => notification.classList.add('show'), 10);

        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }

    private createNotification(message: string, type: NotificationType): HTMLElement {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        return notification;
    }
}

class DashboardController {
    private api: DashboardAPI;
    private renderer: MetricsRenderer;
    private notifications: NotificationService;
    private updateInterval: number | null = null;

    constructor(config: APIConfig) {
        this.api = new DashboardAPI(config);
        this.renderer = new MetricsRenderer();
        this.notifications = new NotificationService();
    }

    async init(): Promise<void> {
        try {
            console.log('Initializing dashboard...');
            
            await this.loadAndRender();
            this.setupEventListeners();
            this.startAutoRefresh();
            
            this.notifications.show('Dashboard loaded successfully', 'success');
        } catch (error) {
            console.error('Initialization failed:', error);
            this.notifications.show('Failed to load dashboard', 'error');
        }
    }

    private async loadAndRender(): Promise<void> {
        const metrics = await this.api.fetchMetrics();
        this.renderer.render(metrics);
    }

    private setupEventListeners(): void {
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.stopAutoRefresh();
            } else {
                this.startAutoRefresh();
            }
        });
    }

    private startAutoRefresh(): void {
        if (this.updateInterval !== null) return;

        this.updateInterval = window.setInterval(async () => {
            try {
                await this.loadAndRender();
            } catch (error) {
                console.error('Auto-refresh failed:', error);
            }
        }, 30000);
    }

    private stopAutoRefresh(): void {
        if (this.updateInterval !== null) {
            clearInterval(this.updateInterval);
            this.updateInterval = null;
        }
    }

    destroy(): void {
        this.stopAutoRefresh();
        console.log('Dashboard destroyed');
    }
}

// Initialize application
const main = async (): Promise<void> => {
    const config: APIConfig = {
        endpoint: '/api/v1',
        timeout: 5000,
        maxRetries: 3,
        headers: {
            'Authorization': `Bearer ${localStorage.getItem('token') || ''}`
        }
    };

    const dashboard = new DashboardController(config);
    await dashboard.init();

    // Make available globally for debugging
    (window as any).dashboard = dashboard;
};

// Run when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', main);
} else {
    main();
}

export { DashboardController, DashboardAPI, MetricsRenderer, NotificationService };
export type { MetricData, APIConfig, ChartConfig, NotificationType };

