/**
 * CORE
 * Shared utilities. Zero dependencies. Plain scripts (no modules).
 * Works on file://, localhost, and any server.
 */

(function() {
  'use strict';

  window.Sukha = window.Sukha || {};

  Sukha.$ = function(selector, scope) {
    return (scope || document).querySelector(selector);
  };

  Sukha.$$ = function(selector, scope) {
    return Array.from((scope || document).querySelectorAll(selector));
  };

  Sukha.on = function(el, event, handler, opts) {
    el.addEventListener(event, handler, opts || false);
    return function() {
      el.removeEventListener(event, handler, opts || false);
    };
  };

  Sukha.throttle = function(fn, wait) {
    var last = 0;
    return function() {
      var now = Date.now();
      if (now - last >= wait) {
        last = now;
        fn.apply(this, arguments);
      }
    };
  };

  Sukha.prefersReducedMotion = function() {
    return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  };
})();
