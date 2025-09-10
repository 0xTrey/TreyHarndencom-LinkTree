// MetricCounter Class for Sobriety Tracker
class MetricCounter {
    constructor(element, initialValue = 0) {
        this.element = element;
        this.currentValue = initialValue;
        this.isVisible = true;
        
        // Initialize the display
        this.updateDisplay(initialValue);
        
        // Set up visibility change detection for performance
        document.addEventListener('visibilitychange', () => {
            this.isVisible = !document.hidden;
            if (this.isVisible) {
                this.fetchAndUpdate();
            }
        });
    }

    updateDisplay(newValue, showAnimation = false) {
        if (this.element) {
            // Add pulse animation if value changed
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
                const data = await response.json();
                return data;
            }
        } catch (error) {
            console.error('Error fetching sobriety data:', error);
        }
        return null;
    }
}

// Sobriety Tracker Manager
class SobrietyTracker {
    constructor() {
        this.counters = {};
        this.updateInterval = null;
        this.isInitialized = false;
    }

    init() {
        // Initialize counters for each metric
        const elements = {
            'days_of_life': document.getElementById('days-of-life'),
            'days_alcohol_free': document.getElementById('days-alcohol-free'),
            'days_marijuana_free': document.getElementById('days-marijuana-free')
        };

        // Create MetricCounter instances
        Object.keys(elements).forEach(key => {
            if (elements[key]) {
                this.counters[key] = new MetricCounter(elements[key]);
            }
        });

        // Initial update
        this.updateCounters();
        
        // Set up periodic updates (every minute)
        this.startPeriodicUpdates();
        
        // Schedule midnight updates for daily transitions
        this.scheduleMidnightUpdate();
        
        this.isInitialized = true;
    }

    async updateCounters() {
        if (Object.keys(this.counters).length === 0) return;
        
        try {
            const response = await fetch('/api/sobriety_data');
            if (response.ok) {
                const data = await response.json();
                
                // Update each counter with animation if value changed
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
        // Update every minute
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
            // Schedule daily updates after first midnight
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

document.addEventListener('DOMContentLoaded', function() {
    // Add click tracking to all social links
    const socialLinks = document.querySelectorAll('.social-link');
    
    socialLinks.forEach(link => {
        link.addEventListener('click', async function(e) {
            const linkName = this.getAttribute('data-link-name');
            
            try {
                // Send click data to server
                const response = await fetch('/track-click', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ link_name: linkName })
                });
                
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                
                console.log(`Click tracked: ${linkName}`);
            } catch (error) {
                console.error('Error tracking click:', error);
            }
        });
    });

    // Initialize sobriety tracker if elements exist
    const sobrietyElements = document.querySelector('.sobriety-tracker');
    if (sobrietyElements) {
        window.sobrietyTracker = new SobrietyTracker();
        window.sobrietyTracker.init();
    }
});
