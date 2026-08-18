(function ($) {
  const viewer = $('#viewer360');
  if (!viewer.length) return;

  const framesByColor = viewer.data('frames') || {};
  let activeFrames = [];
  let frameIndex = 0;
  let dragStartX = null;
  let blockedRanges = [];
  let calDate = new Date();
  calDate.setDate(1);
  let start = null;
  let end = null;

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

  function step(delta) {
    if (!activeFrames.length) return;
    frameIndex = (frameIndex + delta + activeFrames.length) % activeFrames.length;
    renderFrame();
  }

  viewer.on('mousedown touchstart', function (event) {
    const p = event.originalEvent.touches ? event.originalEvent.touches[0] : event;
    dragStartX = p.clientX;
  });
  $(document).on('mousemove touchmove', function (event) {
    if (dragStartX === null) return;
    const p = event.originalEvent.touches ? event.originalEvent.touches[0] : event;
    const diff = p.clientX - dragStartX;
    if (Math.abs(diff) > 24) { step(diff > 0 ? -1 : 1); dragStartX = p.clientX; }
  }).on('mouseup touchend', function () { dragStartX = null; });

  $('.swatch').on('click', function () {
    $('.swatch').removeClass('active');
    $(this).addClass('active');
    const id = $(this).data('color-id');
    $('#selectedColorInput').val(id);
    const lang = $('html').attr('lang') || 'ru';
    $('#selectedColorName').text($(this).data('color-' + lang));
    setFrames(id);
  });
  $('.swatch').first().trigger('click');

  const booking = $('.booking-block');
  if (!booking.length) return;
  const productId = booking.data('product-id');

  function iso(d) {
    const y = d.getFullYear();
    const m = String(d.getMonth() + 1).padStart(2, '0');
    const day = String(d.getDate()).padStart(2, '0');
    return `${y}-${m}-${day}`;
  }
  function fromIso(s) { const [y,m,d] = s.split('-').map(Number); return new Date(y, m-1, d); }
  function isBlocked(d) {
    const day = iso(d);
    return blockedRanges.some(r => day >= r.start && day <= r.end);
  }
  function inSelected(d) {
    if (!start) return false;
    const t = d.getTime();
    if (!end) return t === start.getTime();
    return t >= start.getTime() && t <= end.getTime();
  }
  function rangeHasBlocked(a, b) {
    let d = new Date(a);
    while (d <= b) { if (isBlocked(d)) return true; d.setDate(d.getDate()+1); }
    return false;
  }
  function renderCalendar() {
    const lang = $('html').attr('lang') === 'en' ? 'en-US' : 'ru-RU';
    $('#calTitle').text(calDate.toLocaleDateString(lang, {month:'long', year:'numeric'}));
    const grid = $('#bookingCalendar').empty();
    const first = new Date(calDate.getFullYear(), calDate.getMonth(), 1);
    let offset = (first.getDay() + 6) % 7;
    for (let i=0; i<offset; i++) grid.append('<span class="cal-day empty"></span>');
    const days = new Date(calDate.getFullYear(), calDate.getMonth()+1, 0).getDate();
    const today = new Date(); today.setHours(0,0,0,0);
    for (let day=1; day<=days; day++) {
      const d = new Date(calDate.getFullYear(), calDate.getMonth(), day);
      const disabled = d < today || isBlocked(d);
      const el = $('<button type="button" class="cal-day"></button>').text(day).data('date', iso(d));
      if (disabled) el.prop('disabled', true).addClass('blocked');
      if (inSelected(d)) el.addClass('selected');
      grid.append(el);
    }
  }
  function updateSummary() {
    $('#startDate').val(start ? iso(start) : '');
    $('#endDate').val(end ? iso(end) : '');
    $('#dateSummary').text(start ? (iso(start) + (end ? ' → ' + iso(end) : ' → …')) : 'Выберите даты / Select dates');
  }

  $('#bookingCalendar').on('click', '.cal-day:not(:disabled)', function () {
    const d = fromIso($(this).data('date'));
    if (!start || end || d < start) { start = d; end = null; }
    else {
      if (rangeHasBlocked(start, d)) {
        $('#reservationMessage').text('В выбранном диапазоне есть занятые даты / Some dates are unavailable').addClass('error');
        return;
      }
      end = d;
      $('#reservationMessage').text('').removeClass('error');
    }
    updateSummary(); renderCalendar();
  });
  $('#calPrev').on('click', function(){ calDate.setMonth(calDate.getMonth()-1); renderCalendar(); });
  $('#calNext').on('click', function(){ calDate.setMonth(calDate.getMonth()+1); renderCalendar(); });

  $.get(`/ajax/products/${productId}/booked-dates/`, function (data) { blockedRanges = data.ranges || []; renderCalendar(); });

  $('#reservationForm').on('submit', function (e) {
    e.preventDefault();
    if (!start || !end) { $('#reservationMessage').text('Сначала выберите период / Select a date range first').addClass('error'); return; }
    $.ajax({
      url: `/ajax/products/${productId}/reserve/`,
      method: 'POST',
      data: $(this).serialize(),
      success: function () {
        $('#reservationMessage').text('Заявка отправлена. Мы подтвердим бронь / Request sent.').removeClass('error').addClass('success');
        $.get(`/ajax/products/${productId}/booked-dates/`, function (data) { blockedRanges = data.ranges || []; renderCalendar(); });
      },
      error: function (xhr) {
        const text = xhr.responseJSON?.error || 'Проверьте поля / Check the form';
        $('#reservationMessage').text(text).removeClass('success').addClass('error');
      }
    });
  });
})(jQuery);
