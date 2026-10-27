// NO | EN switch for the simpler pages (index.html has its own, which also
// re-renders the list and map). The initial language is set in the layout's
// <head> from ?lang=, then the saved choice, else Norwegian.
(function () {
  const buttons = document.querySelectorAll('.lang-btn');

  function setLang(next) {
    const lang = next === 'en' ? 'en' : 'nb';
    document.documentElement.dataset.lang = lang;
    document.documentElement.lang = lang;
    try { localStorage.setItem('omhm-lang', lang); } catch (e) {}
    buttons.forEach(b => b.classList.toggle('selected', b.dataset.setLang === lang));
    // Attributes can't hold two languages, so they carry data-<attr>-nb/-en
    document.querySelectorAll('[data-placeholder-nb]').forEach(el => {
      el.placeholder = el.dataset['placeholder' + (lang === 'en' ? 'En' : 'Nb')];
    });
    const url = new URL(location.href);
    if (lang === 'en') url.searchParams.set('lang', 'en'); else url.searchParams.delete('lang');
    history.replaceState(null, '', url);
    document.dispatchEvent(new CustomEvent('omhm:lang', { detail: lang }));
  }

  buttons.forEach(b => b.addEventListener('click', () => setLang(b.dataset.setLang)));
  setLang(document.documentElement.dataset.lang);
})();
