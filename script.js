// === Initialize VANTA Background ===
VANTA.GLOBE({
  el: "#vanta-bg",
  mouseControls: true,
  touchControls: true,
  gyroControls: false,
  minHeight: 200.00,
  minWidth: 200.00,
  scale: 1.00,
  scaleMobile: 1.00,
  color: 0x00ffe1,
  backgroundColor: 0x000814,
});

// === Initialize AOS (Animate On Scroll) ===
AOS.init({
  once: true,
  duration: 1200,
  offset: 100,
});

// === Smooth Scroll for Internal Links ===
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener('click', function (e) {
    e.preventDefault();
    const target = document.querySelector(this.getAttribute('href'));
    if (target) {
      window.scrollTo({
        top: target.offsetTop - 50,
        behavior: 'smooth'
      });
    }
  });
});

// === Subtle Header Fade Animation on Load ===
window.addEventListener('load', () => {
  const header = document.querySelector('header');
  header.style.opacity = 0;
  header.style.transition = 'opacity 1.5s ease-in';
  setTimeout(() => {
    header.style.opacity = 1;
  }, 200);
});
