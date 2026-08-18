(function ($) {
  const viewer = $('#viewer360');
  const booking = $('.booking-block');
  const lang = ['az', 'en', 'ru'].includes($('html').attr('lang')) ? $('html').attr('lang') : 'az';
  const locale = {az: 'az-AZ', en: 'en-US', ru: 'ru-RU'}[lang];

  const text = {
    az: {
      selectDates: 'Tarixləri seçin',
      chooseColor: 'Əvvəl rəng seçin.',
      chooseSize: 'Əvvəl ölçü seçin.',
      choosePeriod: 'Əvvəl tarix aralığını seçin.',
      unavailable: 'Seçilmiş tarix aralığında artıq bron olunmuş gün var.',
      invalid: 'Bron yaratmaq mümkün olmadı. Məlumatları yoxlayın.',
      sent: 'Sorğunuz qəbul edildi. Təsdiqdən sonra bron qüvvəyə minəcək.',
      code: 'Bron kodu',
      days: 'gün',
      loading: 'Mövcud tarixlər yoxlanılır…'
    },
    en: {
      selectDates: 'Select dates',
      chooseColor: 'Choose a color first.',
      chooseSize: 'Choose a size first.',
      choosePeriod: 'Select a date range first.',
      unavailable: 'The selected range contains unavailable dates.',
      invalid: 'Could not create the booking. Check the details.',
      sent: 'Request received. The booking becomes active after confirmation.',
      code: 'Booking code',
      days: 'days',
      loading: 'Checking availability…'
    },
    ru: {
      selectDates: 'Выберите даты',
      chooseColor: 'Сначала выберите цвет.',
      chooseSize: 'Сначала выберите размер.',
      choosePeriod: 'Сначала выберите период.',
      unavailable: 'В выбранном периоде уже есть занятые даты.',
      invalid: 'Не удалось создать бронь. Проверьте данные.',
      sent: 'Заявка принята. Бронь вступит в силу после подтверждения.',
      code: 'Код брони',
      days: 'дн.',
      loading: 'Проверяем свободные даты…'
    }
  }[lang];

  const framesByColor = viewer.length ? (viewer.data('frames') || {}) : {};
  let activeFrames = [];
  let frameIndex = 0;
  let dragStartX = null;

  const productId = booking.data('product-id');
  let blockedRanges = [];
  let calDate = new Date();
  calDate.setHours(0, 0, 0, 0);
  calDate.setDate(1);
  let start = null;
  let end = null;
  let selectedColorId = '';
  let availabilityRequest = null;

  function setFrames(colorId) {
    activeFrames = framesByColor[String(colorId)] || framesByColor.default || Object.values(framesByColor)[0] || [];
    frameIndex = 0;
    renderFrame();
  }

  function renderFrame() {
    if (!activeFrames.length) return;
    const frame = activeFrames[frameIndex];
    $('#viewerImage').attr('src', frame.url);
    $('#viewerAngle').text(frame.angle + '°');
    $('#viewerProgress').css('width', ((frameIndex + 1) / activeFrames.length * 100) + '%');
  }

  function stepFrame(delta) {
    if (!activeFrames.length) return;
    frameIndex = (frameIndex + delta + activeFrames.length) % activeFrames.length;
    renderFrame();
  }

  if (viewer.length) {
    viewer.on('mousedown touchstart', function (event) {
      const point = event.originalEvent.touches ? event.originalEvent.touches[0] : event;
      dragStartX = point.clientX;
    });

    $(document)
      .on('mousemove touchmove', function (event) {
        if (dragStartX === null) return;
        const point = event.originalEvent.touches ? event.originalEvent.touches[0] : event;
        const diff = point.clientX - dragStartX;
        if (Math.abs(diff) > 24) {
          stepFrame(diff > 0 ? -1 : 1);
          dragStartX = point.clientX;
        }
      })
      .on('mouseup touchend touchcancel', function () {
        dragStartX = null;
      });
  }

  function iso(dateObject) {
    const year = dateObject.getFullYear();
    const month = String(dateObject.getMonth() + 1).padStart(2, '0');
    const day = String(dateObject.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  }

  function fromIso(value) {
    const [year, month, day] = value.split('-').map(Number);
    return new Date(year, month - 1, day);
  }

  function formatDate(dateObject) {
    return dateObject.toLocaleDateString(locale, {day: '2-digit', month: 'short', year: 'numeric'});
  }

  function isBlocked(dateObject) {
    const day = iso(dateObject);
    return blockedRanges.some(range => day >= range.start && day <= range.end);
  }

  function inSelected(dateObject) {
    if (!start) return false;
    const timestamp = dateObject.getTime();
    if (!end) return timestamp === start.getTime();
    return timestamp >= start.getTime() && timestamp <= end.getTime();
  }

  function rangeHasBlocked(firstDate, lastDate) {
    const cursor = new Date(firstDate);
    while (cursor <= lastDate) {
      if (isBlocked(cursor)) return true;
      cursor.setDate(cursor.getDate() + 1);
    }
    return false;
  }

  function selectedDays() {
    if (!start || !end) return 0;
    return Math.floor((end.getTime() - start.getTime()) / 86400000) + 1;
  }

  function resetRange() {
    start = null;
    end = null;
    $('#startDate, #endDate').val('');
    updateSummary();
  }

  function updateSummary() {
    if (!start) {
      $('#dateSummary').html(`<span>${text.selectDates}</span>`);
      return;
    }

    $('#startDate').val(iso(start));
    $('#endDate').val(end ? iso(end) : '');

    if (!end) {
      $('#dateSummary').html(`<span>${formatDate(start)}</span><b>→</b><span>…</span>`);
      return;
    }

    $('#dateSummary').html(
      `<span>${formatDate(start)}</span><b>→</b><span>${formatDate(end)}</span><em>${selectedDays()} ${text.days}</em>`
    );
  }

  function currentMonthKey(dateObject) {
    return dateObject.getFullYear() * 12 + dateObject.getMonth();
  }

  function renderCalendar() {
    if (!booking.length) return;

    $('#calTitle').text(calDate.toLocaleDateString(locale, {month: 'long', year: 'numeric'}));
    const grid = $('#bookingCalendar').empty();
    const first = new Date(calDate.getFullYear(), calDate.getMonth(), 1);
    const offset = (first.getDay() + 6) % 7;

    for (let index = 0; index < offset; index += 1) {
      grid.append('<span class="cal-day empty"></span>');
    }

    const totalDays = new Date(calDate.getFullYear(), calDate.getMonth() + 1, 0).getDate();
    const today = new Date();
    today.setHours(0, 0, 0, 0);

    for (let day = 1; day <= totalDays; day += 1) {
      const dateObject = new Date(calDate.getFullYear(), calDate.getMonth(), day);
      const past = dateObject < today;
      const blocked = isBlocked(dateObject);
      const button = $('<button type="button" class="cal-day"></button>')
        .text(day)
        .attr('data-date', iso(dateObject));

      if (past) {
        button.prop('disabled', true).addClass('past');
      } else if (blocked) {
        button.prop('disabled', true).addClass('blocked');
      } else {
        button.addClass('free');
      }

      if (inSelected(dateObject)) button.addClass('selected');
      if (dateObject.getTime() === today.getTime()) button.addClass('today');

      grid.append(button);
    }

    const thisMonth = new Date();
    thisMonth.setDate(1);
    thisMonth.setHours(0, 0, 0, 0);
    $('#calPrev').prop('disabled', currentMonthKey(calDate) <= currentMonthKey(thisMonth));
  }

  function showMessage(message, type) {
    $('#reservationMessage')
      .removeClass('error success muted')
      .addClass(type || '')
      .html(message || '');
  }

  function availabilityUrl() {
    let url = `/ajax/products/${productId}/booked-dates/`;
    if (selectedColorId) url += `?color=${encodeURIComponent(selectedColorId)}`;
    return url;
  }

  function loadAvailability(silent) {
    if (!booking.length) return;

    if ($('.swatch').length && !selectedColorId) {
      blockedRanges = [];
      renderCalendar();
      return;
    }

    if (availabilityRequest) availabilityRequest.abort();

    booking.addClass('is-loading');
    if (!silent) showMessage(text.loading, 'muted');

    availabilityRequest = $.ajax({
      url: availabilityUrl(),
      method: 'GET',
      success: function (data) {
        blockedRanges = data.ranges || [];
        resetRange();
        renderCalendar();
        if (!silent) showMessage('', '');
      },
      error: function () {
        blockedRanges = [];
        resetRange();
        renderCalendar();
        if (!silent) showMessage(text.invalid, 'error');
      },
      complete: function () {
        booking.removeClass('is-loading');
        availabilityRequest = null;
      }
    });
  }

  $('.swatch').on('click', function () {
    $('.swatch').removeClass('active');
    $(this).addClass('active');

    selectedColorId = String($(this).data('color-id') || '');
    const colorName = $(this).data('color-' + lang) || $(this).data('color-ru') || '';

    $('#selectedColorInput').val(selectedColorId);
    $('#selectedColorName').text(colorName);
    $('#bookingColorLabel').text(colorName);
    setFrames(selectedColorId);

    if (booking.length) loadAvailability();
  });

  $('#bookingSize').on('change', function () {
    $('#selectedSizeInput').val($(this).val());
  });

  if ($('.swatch').length) {
    $('.swatch').first().trigger('click');
  } else {
    setFrames('default');
    if (booking.length) loadAvailability();
  }

  $('#bookingCalendar').on('click', '.cal-day.free:not(:disabled)', function () {
    const chosen = fromIso($(this).data('date'));

    if (!start || end || chosen < start) {
      start = chosen;
      end = null;
      showMessage('', '');
    } else {
      if (rangeHasBlocked(start, chosen)) {
        showMessage(text.unavailable, 'error');
        return;
      }
      end = chosen;
      showMessage('', '');
    }

    updateSummary();
    renderCalendar();
  });

  $('#calPrev').on('click', function () {
    if ($(this).prop('disabled')) return;
    calDate.setMonth(calDate.getMonth() - 1);
    renderCalendar();
  });

  $('#calNext').on('click', function () {
    calDate.setMonth(calDate.getMonth() + 1);
    renderCalendar();
  });

  $('#reservationForm').on('submit', function (event) {
    event.preventDefault();

    if ($('.swatch').length && !selectedColorId) {
      showMessage(text.chooseColor, 'error');
      return;
    }
    if (!$('#bookingSize').val()) {
      showMessage(text.chooseSize, 'error');
      return;
    }
    if (!start || !end) {
      showMessage(text.choosePeriod, 'error');
      return;
    }

    $('#selectedSizeInput').val($('#bookingSize').val());
    const submitButton = $('#reservationSubmit').prop('disabled', true);

    $.ajax({
      url: `/ajax/products/${productId}/reserve/`,
      method: 'POST',
      data: $(this).serialize(),
      success: function (data) {
        showMessage(
          `<strong>${text.sent}</strong><span class="booking-code">${text.code}: ${data.booking_code}</span>`,
          'success'
        );
        resetRange();
        loadAvailability(true);
      },
      error: function (xhr) {
        const payload = xhr.responseJSON || {};
        let message = text.invalid;
        const errors = payload.errors || {};
        if (errors.start_date || errors.end_date) message = text.unavailable;
        if (errors.color) message = text.chooseColor;
        if (errors.size) message = text.chooseSize;
        showMessage(message, 'error');
        loadAvailability(true);
      },
      complete: function () {
        submitButton.prop('disabled', false);
      }
    });
  });

  updateSummary();
  renderCalendar();
})(jQuery);
