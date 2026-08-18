(function ($) {
  const translations = {
    az: {home:'Ana səhifə', catalog:'Kataloq', about:'Haqqımızda', contacts:'Əlaqə', viewer360:'360° baxış'},
    en: {home:'Home', catalog:'Catalog', about:'About', contacts:'Contacts', viewer360:'360° view'},
    ru: {home:'Главная', catalog:'Каталог', about:'О нас', contacts:'Контакты', viewer360:'360° обзор'}
  };

  function swapLocalContent(lang) {
    $('[data-i18n]').each(function () {
      const key = $(this).data('i18n');
      if (translations[lang] && translations[lang][key]) {
        $(this).text(translations[lang][key]);
      }
    });
    $('[data-name-az], [data-name-ru], [data-name-en]').each(function () {
      const value = $(this).data('name-' + lang);
      if (value) $(this).text(value);
    });
    $('[data-description-az], [data-description-ru], [data-description-en]').each(function () {
      const value = $(this).data('description-' + lang);
      if (value) $(this).text(value);
    });
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
        window.location.reload();
      }
    });
  });

  $('.nav-toggle').on('click', function () {
    $('.main-nav').toggleClass('open');
  });
})(jQuery);
