/**
 * PARALLAX
 * Smooth parallax scrolling for depth layers.
 * Only activates when data-parallax-speed elements exist.
 */

(function() {
  'use strict';

  function initParallax() {
    if (Sukha.prefersReducedMotion()) return;

    var layers = document.querySelectorAll('[data-parallax-speed]');
    if (!layers.length) return;

    function update() {
      var scrollY = window.scrollY;
      layers.forEach(function(layer) {
        var speed = parseFloat(layer.dataset.parallaxSpeed) || 0.5;
        var offset = scrollY * speed * 0.3;
        layer.style.transform = 'translate3d(0, ' + offset + 'px, 0)';
      });
    }

    var throttled = Sukha.throttle(update, 16);
    window.addEventListener('scroll', throttled, { passive: true });
    update();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initParallax);
  } else {
    initParallax();
  }
})();
