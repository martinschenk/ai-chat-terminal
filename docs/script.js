// Copy install command to clipboard
function copyInstall() {
    const command = document.getElementById('install-cmd').textContent.trim();
    navigator.clipboard.writeText(command).then(() => {
        const btn = document.getElementById('copy-btn');
        const originalHTML = btn.innerHTML;

        // Show success feedback
        btn.innerHTML = `
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="20 6 9 17 4 12"></polyline>
            </svg>
        `;
        btn.style.background = '#10b981';

        // Reset after 2 seconds
        setTimeout(() => {
            btn.innerHTML = originalHTML;
            btn.style.background = '';
        }, 2000);
    });
}

// Fetch live GitHub stats
async function fetchGitHubStats() {
    try {
        const response = await fetch('https://api.github.com/repos/martinschenk/ai-chat-terminal');
        const data = await response.json();

        // Update stars count
        const starsEl = document.getElementById('stars-count');
        if (starsEl && data.stargazers_count) {
            animateNumber(starsEl, data.stargazers_count);
        }

        // Fetch download count from releases
        try {
            const releasesResponse = await fetch('https://api.github.com/repos/martinschenk/ai-chat-terminal/releases');
            const releases = await releasesResponse.json();

            let totalDownloads = 0;
            releases.forEach(release => {
                if (release.assets) {
                    release.assets.forEach(asset => {
                        totalDownloads += asset.download_count || 0;
                    });
                }
            });

            const downloadsEl = document.getElementById('downloads-count');
            if (downloadsEl) {
                animateNumber(downloadsEl, totalDownloads > 0 ? totalDownloads : 130);
            }
        } catch (e) {
            console.log('Could not fetch download stats:', e);
        }

    } catch (error) {
        console.log('Could not fetch GitHub stats:', error);
    }
}

// Animate number counting
function animateNumber(element, target) {
    const start = parseInt(element.textContent) || 0;
    const duration = 1000; // 1 second
    const increment = (target - start) / (duration / 16); // 60fps

    let current = start;
    const timer = setInterval(() => {
        current += increment;
        if ((increment > 0 && current >= target) || (increment < 0 && current <= target)) {
            element.textContent = target;
            clearInterval(timer);
        } else {
            element.textContent = Math.floor(current);
        }
    }, 16);
}

// Smooth scroll for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            const navHeight = document.querySelector('.nav').offsetHeight;
            const targetPosition = target.offsetTop - navHeight - 20;

            window.scrollTo({
                top: targetPosition,
                behavior: 'smooth'
            });
        }
    });
});

// Intersection Observer for fade-in animations
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
        }
    });
}, observerOptions);

// Observe feature cards
document.addEventListener('DOMContentLoaded', () => {
    // Fetch GitHub stats on load
    fetchGitHubStats();

    // Add fade-in animation to feature cards
    const cards = document.querySelectorAll('.feature-card');
    cards.forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        card.style.transition = 'opacity 0.6s, transform 0.6s';
        observer.observe(card);
    });

    // Add fade-in to workflow steps
    const steps = document.querySelectorAll('.workflow-step');
    steps.forEach(step => {
        step.style.opacity = '0';
        step.style.transform = 'translateY(20px)';
        step.style.transition = 'opacity 0.6s, transform 0.6s';
        observer.observe(step);
    });
});

// Track outbound links (optional - for analytics)
document.querySelectorAll('a[href^="http"]').forEach(link => {
    link.addEventListener('click', (e) => {
        // You can add analytics tracking here if needed
        console.log('External link clicked:', link.href);
    });
});
