// Language toggle (ru default) with a brief neubrutalist loader stamp.
(function () {
  var KEY = 'dk-lang';
  var body = document.body;
  var btn = document.getElementById('langToggle');
  var loader = document.getElementById('loader');

  function apply(lang) {
    body.classList.toggle('en', lang === 'en');
    if (btn) btn.textContent = lang === 'en' ? 'RU' : 'EN';
    document.documentElement.lang = lang;
  }

  var saved;
  try { saved = localStorage.getItem(KEY); } catch (e) { /* private mode */ }
  apply(saved === 'en' ? 'en' : 'ru');

  if (btn) btn.addEventListener('click', function () {
    var next = body.classList.contains('en') ? 'ru' : 'en';
    if (loader && !matchMedia('(prefers-reduced-motion: reduce)').matches) {
      loader.classList.add('on');
      setTimeout(function () { apply(next); loader.classList.remove('on'); }, 450);
    } else {
      apply(next);
    }
    try { localStorage.setItem(KEY, next); } catch (e) { /* ignore */ }
  });
})();
