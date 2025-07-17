document.addEventListener('DOMContentLoaded', function() {
    // Animate elements on page load
    animateElementsOnLoad();
    
    // Set up event listeners
    setupEventListeners();
    
    // Theme toggle functionality
    setupThemeToggle();
});

function animateElementsOnLoad() {
    const header = document.querySelector('.header');
    const statsCards = document.querySelectorAll('.stats-card');
    const buttons = document.querySelectorAll('button');
    
    // Fade in header with slight delay
    if (header) {
        header.style.opacity = '0';
        header.style.transform = 'translateY(-20px)';
        header.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        
        setTimeout(() => {
            header.style.opacity = '1';
            header.style.transform = 'translateY(0)';
        }, 300);
    }
    
    // Stagger animation for stats cards
    if (statsCards.length) {
        statsCards.forEach((card, index) => {
            card.style.opacity = '0';
            card.style.transform = 'translateY(20px)';
            card.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
            
            setTimeout(() => {
                card.style.opacity = '1';
                card.style.transform = 'translateY(0)';
            }, 400 + (index * 150));
        });
    }
    
    // Buttons animation
    if (buttons.length) {
        buttons.forEach((button, index) => {
            button.style.opacity = '0';
            button.style.transform = 'scale(0.9)';
            button.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
            
            setTimeout(() => {
                button.style.opacity = '1';
                button.style.transform = 'scale(1)';
            }, 800 + (index * 100));
        });
    }
}

function setupEventListeners() {
    // Add ripple effect to buttons
    const buttons = document.querySelectorAll('button');
    buttons.forEach(button => {
        button.addEventListener('click', createRippleEffect);
    });
}

function createRippleEffect(event) {
    const button = event.currentTarget;
    
    const circle = document.createElement('span');
    const diameter = Math.max(button.clientWidth, button.clientHeight);
    const radius = diameter / 2;
    
    circle.style.width = circle.style.height = `${diameter}px`;
    circle.style.left = `${event.clientX - button.offsetLeft - radius}px`;
    circle.style.top = `${event.clientY - button.offsetTop - radius}px`;
    circle.classList.add('ripple');
    
    // Remove existing ripples
    const ripple = button.querySelector('.ripple');
    if (ripple) {
        ripple.remove();
    }
    
    button.appendChild(circle);
}

function setupThemeToggle() {
    // Add theme toggle button if not exists
    if (!document.getElementById('theme-toggle')) {
        const themeToggle = document.createElement('button');
        themeToggle.id = 'theme-toggle';
        themeToggle.innerHTML = '<i class="fas fa-moon"></i>';
        themeToggle.title = 'Toggle Dark/Light Mode';
        themeToggle.classList.add('theme-toggle-btn');
        document.body.appendChild(themeToggle);
        
        // Add theme toggle styles if not exists
        if (!document.querySelector('.theme-toggle-styles')) {
            const themeStyles = document.createElement('style');
            themeStyles.classList.add('theme-toggle-styles');
            themeStyles.textContent = `
                .theme-toggle-btn {
                    position: fixed;
                    bottom: 20px;
                    right: 20px;
                    width: 50px;
                    height: 50px;
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    z-index: 999;
                    padding: 0;
                    font-size: 20px;
                }
                
                .ripple {
                    position: absolute;
                    background: rgba(255, 255, 255, 0.7);
                    border-radius: 50%;
                    transform: scale(0);
                    animation: ripple 0.6s linear;
                    pointer-events: none;
                }
                
                @keyframes ripple {
                    to {
                        transform: scale(4);
                        opacity: 0;
                    }
                }
            `;
            document.head.appendChild(themeStyles);
        }
        
        // Toggle theme on click
        themeToggle.addEventListener('click', toggleTheme);
    }
}

function toggleTheme() {
    const root = document.documentElement;
    const isDarkTheme = root.style.getPropertyValue('--bg-color') === '#f8f9fa';
    const themeToggle = document.getElementById('theme-toggle');
    
    if (isDarkTheme) {
        // Switch to dark theme
        root.style.setProperty('--bg-color', '#1e272e');
        root.style.setProperty('--card-bg', '#2d3436');
        root.style.setProperty('--text-color', '#dfe6e9');
        themeToggle.innerHTML = '<i class="fas fa-sun"></i>';
    } else {
        // Switch to light theme
        root.style.setProperty('--bg-color', '#f8f9fa');
        root.style.setProperty('--card-bg', '#ffffff');
        root.style.setProperty('--text-color', '#2c3e50');
        themeToggle.innerHTML = '<i class="fas fa-moon"></i>';
    }
}

document.getElementById('cacheForm').addEventListener('submit', function(event) {
    event.preventDefault();
    
    const pages = document.getElementById('pages').value.split(',').map(page => page.trim());
    const cacheSize = parseInt(document.getElementById('cache_size').value);
    
    fetch('/simulate-cache', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ pages, cache_size: cacheSize })
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('hits').textContent = `Hits: ${data.hits}`;
        document.getElementById('misses').textContent = `Misses: ${data.misses}`;
        document.getElementById('hit_ratio').textContent = `Hit Ratio: ${data.hit_ratio.toFixed(2)}`;
    })
    .catch(error => console.error('Error:', error));
});
