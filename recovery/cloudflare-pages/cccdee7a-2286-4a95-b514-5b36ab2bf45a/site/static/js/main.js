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

    initJournalEmbed();
});
