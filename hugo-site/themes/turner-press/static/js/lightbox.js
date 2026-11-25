(function () {
  'use strict';

  var list = document.querySelector('[data-lightbox]');
  var dialog = document.querySelector('dialog.lightbox');
  if (!list || !dialog || typeof dialog.showModal !== 'function') {
    return;
  }

  var links = Array.prototype.slice.call(list.querySelectorAll('a[data-index]'));
  var image = dialog.querySelector('img');
  var caption = dialog.querySelector('figcaption');
  var previous = dialog.querySelector('.lightbox-prev');
  var next = dialog.querySelector('.lightbox-next');
  var current = 0;

  function show(index) {
    current = index;
    var link = links[index];
    var thumb = link.querySelector('img');
    var source = link.parentNode.querySelector('.work-caption');
    image.src = link.href;
    image.alt = thumb ? thumb.alt : '';
    caption.innerHTML = source ? source.innerHTML : '';
    previous.disabled = index === 0;
    next.disabled = index === links.length - 1;
  }

  function step(delta) {
    var target = current + delta;
    if (target >= 0 && target < links.length) {
      show(target);
    }
  }

  links.forEach(function (link, index) {
    link.addEventListener('click', function (event) {
      event.preventDefault();
      show(index);
      dialog.showModal();
    });
  });

  previous.addEventListener('click', function () { step(-1); });
  next.addEventListener('click', function () { step(1); });
  dialog.querySelector('.lightbox-close').addEventListener('click', function () { dialog.close(); });
  dialog.addEventListener('click', function (event) {
    if (event.target === dialog) {
      dialog.close();
    }
  });
  dialog.addEventListener('keydown', function (event) {
    if (event.key === 'ArrowLeft') { step(-1); }
    if (event.key === 'ArrowRight') { step(1); }
  });
})();
