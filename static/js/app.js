// Echo Chamber Explorer - JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Character counter for content textarea
    const contentTextarea = document.getElementById('content');
    if (contentTextarea) {
        const charCounter = document.createElement('div');
        charCounter.className = 'form-text text-end';
        charCounter.id = 'char-counter';
        contentTextarea.parentNode.appendChild(charCounter);

        function updateCharCounter() {
            const length = contentTextarea.value.length;
            charCounter.textContent = `${length.toLocaleString()} characters`;
            
            if (length < 100) {
                charCounter.className = 'form-text text-end text-warning';
                charCounter.textContent += ' (minimum 100 characters recommended)';
            } else {
                charCounter.className = 'form-text text-end text-muted';
            }
        }

        contentTextarea.addEventListener('input', updateCharCounter);
        updateCharCounter();
    }

    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Copy bias score to clipboard
    const biasScoreBadges = document.querySelectorAll('.badge');
    biasScoreBadges.forEach(badge => {
        badge.style.cursor = 'pointer';
        badge.title = 'Click to copy score';
        badge.addEventListener('click', function() {
            const score = this.textContent.trim();
            if (navigator.clipboard) {
                navigator.clipboard.writeText(score).then(() => {
                    // Show temporary feedback
                    const originalText = this.textContent;
                    this.textContent = 'Copied!';
                    setTimeout(() => {
                        this.textContent = originalText;
                    }, 1000);
                });
            }
        });
    });
});
