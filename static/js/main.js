class MetricCounter {
    constructor(element, initialValue = 0) {
        this.element = element;
        this.currentValue = initialValue;
        this.isVisible = true;
        this.updateDisplay(initialValue);
        document.addEventListener('visibilitychange', () => {
            this.isVisible = !document.hidden;
            if (this.isVisible) {
                this.fetchAndUpdate();
            }
        });
    }

    updateDisplay(newValue, showAnimation = false) {
        if (this.element) {
            if (showAnimation && newValue !== this.currentValue) {
                this.element.classList.add('pulse-animation');
                setTimeout(() => {
                    this.element.classList.remove('pulse-animation');
                }, 600);
            }
            this.element.textContent = newValue.toLocaleString();
            this.currentValue = newValue;
        }
    }

    async fetchAndUpdate() {
        if (!this.isVisible) return;
        try {
            const response = await fetch('/api/sobriety_data');
            if (response.ok) {
                return await response.json();
            }
        } catch (error) {
            console.error('Error fetching sobriety data:', error);
        }
        return null;
    }
}

class SobrietyTracker {
    constructor() {
        this.counters = {};
        this.updateInterval = null;
        this.isInitialized = false;
    }

    init() {
        const elements = {
            'days_of_life': document.getElementById('days-of-life'),
            'days_alcohol_free': document.getElementById('days-alcohol-free'),
            'days_marijuana_free': document.getElementById('days-marijuana-free')
        };

        Object.keys(elements).forEach(key => {
            if (elements[key]) {
                this.counters[key] = new MetricCounter(elements[key]);
            }
        });

        if (Object.keys(this.counters).length === 0) return;

        this.updateCounters();
        this.startPeriodicUpdates();
        this.scheduleMidnightUpdate();
        this.isInitialized = true;
    }

    async updateCounters() {
        if (Object.keys(this.counters).length === 0) return;
        try {
            const response = await fetch('/api/sobriety_data');
            if (response.ok) {
                const data = await response.json();
                Object.keys(this.counters).forEach(key => {
                    if (data[key] !== undefined) {
                        const showAnimation = this.isInitialized && data[key] !== this.counters[key].currentValue;
                        this.counters[key].updateDisplay(data[key], showAnimation);
                    }
                });
            }
        } catch (error) {
            console.error('Error updating counters:', error);
        }
    }

    startPeriodicUpdates() {
        this.updateInterval = setInterval(() => {
            this.updateCounters();
        }, 60000);
    }

    scheduleMidnightUpdate() {
        const now = new Date();
        const tomorrow = new Date(now);
        tomorrow.setDate(tomorrow.getDate() + 1);
        tomorrow.setHours(0, 0, 0, 0);
        const msUntilMidnight = tomorrow.getTime() - now.getTime();
        setTimeout(() => {
            this.updateCounters();
            setInterval(() => {
                this.updateCounters();
            }, 24 * 60 * 60 * 1000);
        }, msUntilMidnight);
    }

    destroy() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
        }
    }
}

function initJournalEmbed() {
    const iframe = document.getElementById('journal-iframe');
    const loading = document.getElementById('journal-loading');
    const fallback = document.getElementById('journal-fallback');

    if (!iframe) return;

    let loaded = false;

    iframe.addEventListener('load', () => {
        loaded = true;
        if (loading) loading.style.display = 'none';
        iframe.style.display = 'block';
    });

    setTimeout(() => {
        if (!loaded) {
            if (loading) loading.style.display = 'none';
            if (fallback) fallback.style.display = 'block';
            iframe.style.display = 'none';
        }
    }, 8000);
}

document.addEventListener('DOMContentLoaded', function() {
    const socialLinks = document.querySelectorAll('.social-link');
    socialLinks.forEach(link => {
        link.addEventListener('click', async function(e) {
            const linkName = this.getAttribute('data-link-name');
            if (!linkName) return;
            try {
                await fetch('/track-click', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ link_name: linkName })
                });
            } catch (error) {
                console.error('Error tracking click:', error);
            }
        });
    });

    const statsElements = document.querySelector('.metrics-grid');
    if (statsElements && document.getElementById('days-of-life')) {
        window.sobrietyTracker = new SobrietyTracker();
        window.sobrietyTracker.init();
    }

    initJournalEmbed();
});
