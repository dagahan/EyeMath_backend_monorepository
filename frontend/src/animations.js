// Super Amazing Animations Manager
class AnimationManager {
  constructor() {
    this.init();
  }

  init() {
    this.setupPageTransitions();
    this.setupScrollAnimations();
    this.setupHoverEffects();
    this.setupFormAnimations();
    this.setupLoadingAnimations();
  }

  setupPageTransitions() {
    // Add entrance animation to main container
    const container = document.querySelector('.container');
    if (container) {
      container.classList.add('page-enter');
    }

    // Add staggered animation to cards
    const cards = document.querySelectorAll('.card');
    cards.forEach((card, index) => {
      setTimeout(() => {
        card.classList.add('card-enter');
      }, index * 100);
    });
  }

  setupScrollAnimations() {
    const observerOptions = {
      threshold: 0.1,
      rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.style.animation = 'bounceIn 0.6s cubic-bezier(0.68, -0.55, 0.265, 1.55)';
          entry.target.style.opacity = '1';
        }
      });
    }, observerOptions);

    // Observe all cards and interactive elements
    document.querySelectorAll('.card, .btn, .nav-link').forEach(el => {
      el.style.opacity = '0';
      observer.observe(el);
    });
  }

  setupHoverEffects() {
    // Add interactive class to hoverable elements
    document.querySelectorAll('.btn, .nav-link, .card').forEach(el => {
      el.classList.add('interactive');
    });

    // Special hover effect for logo
    const logo = document.querySelector('.corner-logo');
    if (logo) {
      logo.addEventListener('mouseenter', () => {
        logo.style.animation = 'pulse 0.6s ease-in-out';
      });
      
      logo.addEventListener('animationend', () => {
        logo.style.animation = '';
      });
    }
  }

  setupFormAnimations() {
    const inputs = document.querySelectorAll('.input, .select, textarea');
    
    inputs.forEach(input => {
      // Add focus animation
      input.addEventListener('focus', () => {
        input.style.transform = 'translateY(-2px) scale(1.02)';
        input.style.boxShadow = '0 8px 25px rgba(59, 130, 246, 0.2)';
      });

      // Remove focus animation
      input.addEventListener('blur', () => {
        input.style.transform = '';
        input.style.boxShadow = '';
      });

      // Add typing animation
      input.addEventListener('input', () => {
        input.style.animation = 'pulse 0.3s ease-in-out';
        setTimeout(() => {
          input.style.animation = '';
        }, 300);
      });
    });
  }

  setupLoadingAnimations() {
    // Add loading animation to buttons
    const buttons = document.querySelectorAll('.btn');
    buttons.forEach(btn => {
      btn.addEventListener('click', () => {
        btn.style.animation = 'pulse 0.3s ease-in-out';
        setTimeout(() => {
          btn.style.animation = '';
        }, 300);
      });
    });
  }

  // Method to add glow effect to specific elements
  addGlowEffect(element) {
    if (element) {
      element.classList.add('glow-effect');
      setTimeout(() => {
        element.classList.remove('glow-effect');
      }, 2000);
    }
  }

  // Method to create particle effect
  createParticleEffect(x, y) {
    for (let i = 0; i < 5; i++) {
      const particle = document.createElement('div');
      particle.style.position = 'fixed';
      particle.style.left = x + 'px';
      particle.style.top = y + 'px';
      particle.style.width = '4px';
      particle.style.height = '4px';
      particle.style.background = 'linear-gradient(45deg, var(--primary), var(--accent))';
      particle.style.borderRadius = '50%';
      particle.style.pointerEvents = 'none';
      particle.style.zIndex = '9999';
      
      document.body.appendChild(particle);
      
      // Animate particle
      const angle = (i / 5) * Math.PI * 2;
      const velocity = 50 + Math.random() * 50;
      const vx = Math.cos(angle) * velocity;
      const vy = Math.sin(angle) * velocity;
      
      particle.animate([
        { transform: 'translate(0, 0) scale(1)', opacity: 1 },
        { transform: `translate(${vx}px, ${vy}px) scale(0)`, opacity: 0 }
      ], {
        duration: 1000,
        easing: 'cubic-bezier(0.4, 0, 0.2, 1)'
      }).onfinish = () => {
        particle.remove();
      };
    }
  }
}

// Initialize animations when DOM is loaded
if (!window.animationManager) {
  document.addEventListener('DOMContentLoaded', () => {
    window.animationManager = new AnimationManager();
    
    // Add click particle effects
    document.addEventListener('click', (e) => {
      if (e.target.classList.contains('btn') || e.target.classList.contains('nav-link')) {
        window.animationManager.createParticleEffect(e.clientX, e.clientY);
      }
    });
  });
}

// Export for use in other modules
export default AnimationManager;