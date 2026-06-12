/**
 * MOTION
 * Scroll-triggered reveals, smooth scroll, back-to-top.
 * Uses Intersection Observer for performance.
 */

(function() {
  'use strict';

  var REVEAL_SELECTOR = '.reveal, .reveal-stagger, .reveal-left, .reveal-right, .reveal-scale';
  var VISIBLE_CLASS = 'is-visible';

  function initMotion() {
    if (Sukha.prefersReducedMotion()) {
      Sukha.$$(REVEAL_SELECTOR).forEach(function(el) {
        el.classList.add(VISIBLE_CLASS);
      });
      return;
    }

    var observer = new IntersectionObserver(function(entries) {
      entries.forEach(function(entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add(VISIBLE_CLASS);
          observer.unobserve(entry.target);
        }
      });
    }, {
      threshold: 0.08,
      rootMargin: '0px 0px -48px 0px'
    });

    Sukha.$$(REVEAL_SELECTOR).forEach(function(el) {
      observer.observe(el);
    });
  }

  function initSmoothScroll() {
    Sukha.$$('a[href^="#"]').forEach(function(anchor) {
      anchor.addEventListener('click', function(e) {
        var href = this.getAttribute('href');
        if (href === '#') return;
        var target = document.querySelector(href);
        if (target) {
          e.preventDefault();
          target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
      });
    });
  }

  function initBackToTop() {
    var btn = document.querySelector('.back-to-top');
    if (!btn) return;

    function toggle() {
      btn.classList.toggle('is-visible', window.scrollY > 600);
    }

    window.addEventListener('scroll', Sukha.throttle(toggle, 100), { passive: true });
    btn.addEventListener('click', function() {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
    toggle();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() {
      initMotion();
      initSmoothScroll();
      initBackToTop();
    });
  } else {
    initMotion();
    initSmoothScroll();
    initBackToTop();
  }
})();
