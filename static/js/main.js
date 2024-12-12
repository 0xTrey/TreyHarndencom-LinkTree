document.addEventListener('DOMContentLoaded', function() {
    // Add click tracking to all social links
    const socialLinks = document.querySelectorAll('.social-link');
    
    socialLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            const linkName = this.getAttribute('data-link-name');
            console.log(`Clicked: ${linkName}`);
            
            // You could implement actual tracking here
            // For now, we're just logging to console
        });
    });
});
