// Intersection Observer for scroll animations
document.addEventListener('DOMContentLoaded', function() {
  const categoryCards = document.querySelectorAll('.category-card');
  
  const observerOptions = {
    threshold: 0.2, // Trigger when 20% of section is visible
    rootMargin: '0px 0px -100px 0px' // Start slightly before it's fully in view
  };
  
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('animate-in');
        observer.unobserve(entry.target); // Only animate once
      }
    });
  }, observerOptions);
  
  // Observe each card
  categoryCards.forEach(card => {
    observer.observe(card);
  });
});