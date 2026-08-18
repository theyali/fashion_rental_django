(function ($) {
  const translations = {
    ru: {home:'Главная', catalog:'Каталог', about:'О нас', contacts:'Контакты', viewer360:'360° обзор'},
    en: {home:'Home', catalog:'Catalog', about:'About', contacts:'Contacts', viewer360:'360° view'}
  };

  function swapLocalContent(lang) {
    $('[data-i18n]').each(function () {
      const key = $(this).data('i18n');
      if (translations[lang] && translations[lang][key]) $(this).text(translations[lang][key]);
    });
    $('[data-name-ru]').each(function () { $(this).text($(this).data('name-' + lang)); });
    $('[data-description-ru]').each(function () { $(this).text($(this).data('description-' + lang)); });
  }

  $('.lang-btn').on('click', function () {
    const lang = $(this).data('lang');
    $.ajax({
      url: '/ajax/language/',
      method: 'POST',
      data: {lang, csrfmiddlewaretoken: window.CSRF_TOKEN},
      success: function () {
        $('.lang-btn').removeClass('active');
        $('.lang-btn[data-lang="' + lang + '"]').addClass('active');
        swapLocalContent(lang);
        // Reload to translate server-rendered prices, forms and categories consistently.
        window.location.reload();
      }
    });
  });

  $('.nav-toggle').on('click', function () { $('.main-nav').toggleClass('open'); });
})(jQuery);
