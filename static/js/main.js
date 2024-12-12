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
});
