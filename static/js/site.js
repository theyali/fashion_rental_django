(function ($) {
  const translations = {
    az: {home:'Ana səhifə', catalog:'Kataloq', about:'Haqqımızda', contacts:'Əlaqə', viewer360:'360° baxış'},
    en: {home:'Home', catalog:'Catalog', about:'About', contacts:'Contacts', viewer360:'360° view'},
    ru: {home:'Главная', catalog:'Каталог', about:'О нас', contacts:'Контакты', viewer360:'360° обзор'}
  };

  function swapLocalContent(lang) {
    $('[data-i18n]').each(function () {
      const key = $(this).data('i18n');
      if (translations[lang] && translations[lang][key]) $(this).text(translations[lang][key]);
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

  const navToggle = $('.nav-toggle');
  const mainNav = $('.main-nav');

  navToggle.on('click', function () {
    const isOpen = mainNav.toggleClass('open').hasClass('open');
    navToggle.attr('aria-expanded', isOpen ? 'true' : 'false');
  });

  mainNav.on('click', 'a', function () {
    mainNav.removeClass('open');
    navToggle.attr('aria-expanded', 'false');
  });

  $('.flash-stack').on('click', '.flash-close', function () {
    $(this).closest('.flash-message').fadeOut(180, function () { $(this).remove(); });
  });

  window.setTimeout(function () {
    $('.flash-message').fadeOut(250, function () { $(this).remove(); });
  }, 7000);

  function updateHeader() {
    $('#siteHeader').toggleClass('is-scrolled', window.scrollY > 10);
  }
  updateHeader();
  $(window).on('scroll', updateHeader);
})(jQuery);
