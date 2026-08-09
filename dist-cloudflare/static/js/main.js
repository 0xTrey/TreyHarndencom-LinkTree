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

function getCentralDate() {
    const parts = new Intl.DateTimeFormat('en-US', {
        timeZone: 'America/Chicago',
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
    }).formatToParts(new Date());

    const dateParts = Object.fromEntries(
        parts
            .filter(part => ['year', 'month', 'day'].includes(part.type))
            .map(part => [part.type, Number(part.value)])
    );

    return Date.UTC(dateParts.year, dateParts.month - 1, dateParts.day);
}

function calculateInclusiveDaysSince(startDateValue) {
    const [year, month, day] = startDateValue.split('-').map(Number);
    if (!year || !month || !day) return null;

    const startDate = Date.UTC(year, month - 1, day);
    const today = getCentralDate();
    const daysElapsed = Math.floor((today - startDate) / 86400000);
    return daysElapsed >= 0 ? daysElapsed + 1 : null;
}

function initLifeCounter() {
    const counters = document.querySelectorAll('[data-life-counter][data-start-date]');
    counters.forEach(counter => {
        const days = calculateInclusiveDaysSince(counter.dataset.startDate);
        if (!days) return;

        counter.textContent = days.toLocaleString();
        counter.setAttribute('aria-label', `${days.toLocaleString()} days alive`);
    });
}

function scheduleLifeCounterUpdates() {
    setInterval(initLifeCounter, 60 * 60 * 1000);
    document.addEventListener('visibilitychange', () => {
        if (!document.hidden) initLifeCounter();
    });
}

document.addEventListener('DOMContentLoaded', function() {
    const socialLinks = document.querySelectorAll('a[data-link-name]');
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

    initLifeCounter();
    scheduleLifeCounterUpdates();
    initJournalEmbed();
});
