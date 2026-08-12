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
    document.querySelectorAll('[data-life-counter][data-start-date]').forEach(counter => {
        const days = calculateInclusiveDaysSince(counter.dataset.startDate);
        if (!days) return;

        counter.textContent = days.toLocaleString();
        counter.setAttribute('aria-label', `${days.toLocaleString()} days alive`);
    });
}

function initNavigation() {
    const toggle = document.querySelector('.nav-toggle');
    const nav = document.getElementById('site-nav');
    if (!toggle || !nav) return;

    const closeNavigation = () => {
        nav.classList.remove('is-open');
        document.body.classList.remove('nav-open');
        toggle.setAttribute('aria-expanded', 'false');
        toggle.setAttribute('title', 'Open navigation');
        toggle.querySelector('i')?.classList.replace('fa-xmark', 'fa-bars');
        const label = toggle.querySelector('.sr-only');
        if (label) label.textContent = 'Open navigation';
    };

    toggle.addEventListener('click', () => {
        const willOpen = !nav.classList.contains('is-open');
        nav.classList.toggle('is-open', willOpen);
        document.body.classList.toggle('nav-open', willOpen);
        toggle.setAttribute('aria-expanded', String(willOpen));
        toggle.setAttribute('title', willOpen ? 'Close navigation' : 'Open navigation');
        toggle.querySelector('i')?.classList.replace(willOpen ? 'fa-bars' : 'fa-xmark', willOpen ? 'fa-xmark' : 'fa-bars');
        const label = toggle.querySelector('.sr-only');
        if (label) label.textContent = willOpen ? 'Close navigation' : 'Open navigation';
    });

    nav.querySelectorAll('a').forEach(link => link.addEventListener('click', closeNavigation));

    document.addEventListener('keydown', event => {
        if (event.key === 'Escape' && nav.classList.contains('is-open')) {
            closeNavigation();
            toggle.focus();
        }
    });

    window.addEventListener('resize', () => {
        if (window.innerWidth > 900) closeNavigation();
    });
}

function initRevealAnimations() {
    const targets = document.querySelectorAll('[data-reveal]');
    if (!targets.length) return;

    if (!('IntersectionObserver' in window) || window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
        targets.forEach(target => target.classList.add('is-visible'));
        return;
    }

    const observer = new IntersectionObserver(entries => {
        entries.forEach(entry => {
            if (!entry.isIntersecting) return;
            entry.target.classList.add('is-visible');
            observer.unobserve(entry.target);
        });
    }, {
        threshold: 0.12,
        rootMargin: '0px 0px -36px 0px',
    });

    targets.forEach(target => observer.observe(target));
}

function initLinkTracking() {
    document.querySelectorAll('a[data-link-name]').forEach(link => {
        link.addEventListener('click', async function() {
            const linkName = this.getAttribute('data-link-name');
            if (!linkName) return;

            try {
                await fetch('/track-click', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ link_name: linkName }),
                    keepalive: true,
                });
            } catch (error) {
                // Static exports intentionally have no click-tracking endpoint.
            }
        });
    });
}

document.addEventListener('DOMContentLoaded', () => {
    initNavigation();
    initRevealAnimations();
    initLinkTracking();
    initLifeCounter();

    setInterval(initLifeCounter, 60 * 60 * 1000);
    document.addEventListener('visibilitychange', () => {
        if (!document.hidden) initLifeCounter();
    });
});
