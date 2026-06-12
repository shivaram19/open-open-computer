/**
 * FAQ
 * Accessible accordion with ARIA support.
 * Only one item open at a time.
 */

(function() {
  'use strict';

  function initFaq() {
    var items = document.querySelectorAll('.faq__item');
    if (!items.length) return;

    items.forEach(function(item) {
      var question = item.querySelector('.faq__question');
      if (!question) return;

      question.addEventListener('click', function() {
        var isOpen = item.classList.contains('is-open');

        // Close all others
        items.forEach(function(other) {
          if (other !== item && other.classList.contains('is-open')) {
            other.classList.remove('is-open');
            var otherQ = other.querySelector('.faq__question');
            if (otherQ) otherQ.setAttribute('aria-expanded', 'false');
          }
        });

        // Toggle current
        item.classList.toggle('is-open');
        question.setAttribute('aria-expanded', !isOpen);
      });

      // Keyboard: Enter or Space toggles
      question.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          question.click();
        }
      });
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initFaq);
  } else {
    initFaq();
  }
})();
