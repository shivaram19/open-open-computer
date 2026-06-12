/**
 * NAVIGATION
 * Mobile menu toggle, active page highlighting, focus trapping.
 */

(function() {
  'use strict';

  function initNavigation() {
    var menuBtn = document.querySelector('.nav__menu-btn');
    var mobileMenu = document.querySelector('.nav__mobile');
    var mobileLinks = mobileMenu ? mobileMenu.querySelectorAll('.nav__mobile-link') : [];
    var focusableSelector = 'a, button, input, textarea, select, [tabindex]:not([tabindex="-1"])';

    if (!menuBtn || !mobileMenu) return;

    // Store last focused element before opening menu
    var lastFocused = null;

    menuBtn.addEventListener('click', function() {
      var isOpen = mobileMenu.classList.toggle('is-open');
      menuBtn.setAttribute('aria-expanded', isOpen);
      menuBtn.setAttribute('aria-label', isOpen ? 'Close menu' : 'Open menu');
      document.body.style.overflow = isOpen ? 'hidden' : '';

      if (isOpen) {
        lastFocused = document.activeElement;
        // Focus first link
        var firstLink = mobileMenu.querySelector('.nav__mobile-link');
        if (firstLink) firstLink.focus();
      } else if (lastFocused) {
        lastFocused.focus();
      }
    });

    // Close on link click
    Array.from(mobileLinks).forEach(function(link) {
      link.addEventListener('click', function() {
        mobileMenu.classList.remove('is-open');
        menuBtn.setAttribute('aria-expanded', 'false');
        menuBtn.setAttribute('aria-label', 'Open menu');
        document.body.style.overflow = '';
      });
    });

    // Focus trap inside mobile menu
    mobileMenu.addEventListener('keydown', function(e) {
      if (e.key !== 'Tab' || !mobileMenu.classList.contains('is-open')) return;

      var focusables = Array.from(mobileMenu.querySelectorAll(focusableSelector));
      if (!focusables.length) return;

      var first = focusables[0];
      var last = focusables[focusables.length - 1];

      if (e.shiftKey && document.activeElement === first) {
        e.preventDefault();
        last.focus();
      } else if (!e.shiftKey && document.activeElement === last) {
        e.preventDefault();
        first.focus();
      }
    });

    // Close on Escape
    document.addEventListener('keydown', function(e) {
      if (e.key === 'Escape' && mobileMenu.classList.contains('is-open')) {
        mobileMenu.classList.remove('is-open');
        menuBtn.setAttribute('aria-expanded', 'false');
        menuBtn.setAttribute('aria-label', 'Open menu');
        document.body.style.overflow = '';
        menuBtn.focus();
      }
    });

    // Highlight current page
    var currentFile = window.location.pathname.split('/').pop() || 'index.html';
    Sukha.$$('.nav__link, .nav__mobile-link').forEach(function(link) {
      var href = link.getAttribute('href');
      if (href && href.indexOf(currentFile) !== -1) {
        link.setAttribute('aria-current', 'page');
      }
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initNavigation);
  } else {
    initNavigation();
  }
})();
