(function ($) {
  const viewer = $('#viewer360');
  const booking = $('.booking-block');
  const lang = ['az', 'en', 'ru'].includes($('html').attr('lang')) ? $('html').attr('lang') : 'az';
  const locale = {az: 'az-AZ', en: 'en-US', ru: 'ru-RU'}[lang];

  const text = {
    az: {selectDates:'Tarixləri seçin',chooseColor:'Əvvəl rəng seçin.',chooseSize:'Əvvəl ölçü seçin.',choosePeriod:'Əvvəl tarix aralığını seçin.',unavailable:'Seçilmiş tarix aralığında artıq bron olunmuş gün var.',invalid:'Bron yaratmaq mümkün olmadı. Məlumatları yoxlayın.',sent:'Sorğunuz qəbul edildi. Təsdiqdən sonra bron qüvvəyə minəcək.',code:'Bron kodu',days:'gün',day:'gün',total:'Ümumi',loading:'Mövcud tarixlər yoxlanılır…'},
    en: {selectDates:'Select dates',chooseColor:'Choose a color first.',chooseSize:'Choose a size first.',choosePeriod:'Select a date range first.',unavailable:'The selected range contains unavailable dates.',invalid:'Could not create the booking. Check the details.',sent:'Request received. The booking becomes active after confirmation.',code:'Booking code',days:'days',day:'day',total:'Total',loading:'Checking availability…'},
    ru: {selectDates:'Выберите даты',chooseColor:'Сначала выберите цвет.',chooseSize:'Сначала выберите размер.',choosePeriod:'Сначала выберите период.',unavailable:'В выбранном периоде уже есть занятые даты.',invalid:'Не удалось создать бронь. Проверьте данные.',sent:'Заявка принята. Бронь вступит в силу после подтверждения.',code:'Код брони',days:'дн.',day:'день',total:'Итого',loading:'Проверяем свободные даты…'}
  }[lang];

  let mediaByColor = {};
  const mediaDataNode = document.getElementById('productMediaData');
  if (mediaDataNode) {
    try { mediaByColor = JSON.parse(mediaDataNode.textContent || '{}'); } catch (error) { mediaByColor = {}; }
  }

  const coverUrl = viewer.data('cover-url') || '';
  let activeMedia = {photos: [], frames: []};
  let mediaMode = 'photos';
  let photoIndex = 0;
  let frameIndex = 0;
  let dragStartX = null;
  let dragPointerId = null;

  function firstMediaBucket() { return Object.values(mediaByColor).find(bucket => (bucket.photos || []).length || (bucket.frames || []).length) || {photos: [], frames: []}; }
  function bucketForColor(colorId) { return mediaByColor[String(colorId)] || mediaByColor.default || firstMediaBucket(); }
  function setMediaForColor(colorId) {
    const bucket = bucketForColor(colorId);
    activeMedia = {photos: Array.isArray(bucket.photos) ? bucket.photos : [], frames: Array.isArray(bucket.frames) ? bucket.frames : []};
    photoIndex = 0; frameIndex = 0; renderMedia();
  }
  function setMediaMode(mode) { mediaMode = mode === 'spin' ? 'spin' : 'photos'; renderMedia(); }
  function setViewerImage(url) {
    const image = $('#viewerImage');
    if (url) image.attr('src', url).prop('hidden', false); else image.removeAttr('src').prop('hidden', true);
  }
  function renderThumbs() {
    const thumbs = $('#galleryThumbs').empty();
    if (mediaMode !== 'photos' || !activeMedia.photos.length) { thumbs.prop('hidden', true); return; }
    thumbs.prop('hidden', false);
    activeMedia.photos.forEach(function (photo, index) {
      const button = $('<button type="button" class="media-thumb"></button>').toggleClass('active', index === photoIndex).attr('aria-label', `Photo ${index + 1}`).on('click', function () { photoIndex = index; renderMedia(); });
      $('<img alt="">').attr('src', photo.url).appendTo(button); thumbs.append(button);
    });
  }
  function renderPhotos() {
    const photos = activeMedia.photos; const photo = photos[photoIndex] || null; setViewerImage(photo ? photo.url : coverUrl);
    $('#viewerHint, #spinUnavailable, #viewerProgressWrap').prop('hidden', true);
    $('#mediaPrev, #mediaNext').prop('hidden', photos.length <= 1);
    $('#mediaCounter').prop('hidden', photos.length <= 1).text(photos.length ? `${photoIndex + 1} / ${photos.length}` : '');
    viewer.removeClass('is-spin is-dragging').addClass('is-photo'); renderThumbs();
  }
  function renderSpin() {
    const frames = activeMedia.frames;
    $('#mediaPrev, #mediaNext, #mediaCounter, #galleryThumbs').prop('hidden', true); viewer.removeClass('is-photo').addClass('is-spin');
    if (!frames.length) {
      const fallbackPhoto = activeMedia.photos[photoIndex] || activeMedia.photos[0]; setViewerImage(fallbackPhoto ? fallbackPhoto.url : coverUrl);
      $('#viewerHint, #viewerProgressWrap').prop('hidden', true); $('#spinUnavailable').prop('hidden', false); return;
    }
    frameIndex = (frameIndex + frames.length) % frames.length;
    const frame = frames[frameIndex]; setViewerImage(frame.url); $('#spinUnavailable').prop('hidden', true); $('#viewerHint, #viewerProgressWrap').prop('hidden', false);
    $('#viewerAngle').text(`${frame.angle}°`); $('#viewerProgress').css('width', `${((frameIndex + 1) / frames.length) * 100}%`);
  }
  function renderMedia() { $('.media-mode-btn').removeClass('active'); $(`.media-mode-btn[data-media-mode="${mediaMode}"]`).addClass('active'); if (mediaMode === 'spin') renderSpin(); else renderPhotos(); }
  function stepFrame(delta) { if (mediaMode !== 'spin' || activeMedia.frames.length < 2) return; frameIndex = (frameIndex + delta + activeMedia.frames.length) % activeMedia.frames.length; renderSpin(); }

  $('.media-mode-btn').on('click', function () { setMediaMode($(this).data('media-mode')); });
  $('#mediaPrev').on('click', function () { if (activeMedia.photos.length <= 1) return; photoIndex = (photoIndex - 1 + activeMedia.photos.length) % activeMedia.photos.length; renderMedia(); });
  $('#mediaNext').on('click', function () { if (activeMedia.photos.length <= 1) return; photoIndex = (photoIndex + 1) % activeMedia.photos.length; renderMedia(); });

  if (viewer.length) {
    viewer.on('pointerdown', function (event) {
      if (mediaMode !== 'spin' || activeMedia.frames.length < 2) return;
      const original = event.originalEvent; dragStartX = original.clientX; dragPointerId = original.pointerId; viewer.addClass('is-dragging');
      if (this.setPointerCapture && dragPointerId !== undefined) this.setPointerCapture(dragPointerId);
    });
    viewer.on('pointermove', function (event) {
      if (dragStartX === null || mediaMode !== 'spin') return;
      const original = event.originalEvent; const diff = original.clientX - dragStartX;
      if (Math.abs(diff) >= 18) { stepFrame(diff > 0 ? -1 : 1); dragStartX = original.clientX; }
    });
    viewer.on('pointerup pointercancel lostpointercapture', function () { dragStartX = null; dragPointerId = null; viewer.removeClass('is-dragging'); });
  }

  const productId = booking.data('product-id');
  let dailyPrice = parseFloat(String(booking.attr('data-daily-price') || '0').replace(',', '.')) || 0;
  let blockedRanges = [];
  let calDate = new Date(); calDate.setHours(0,0,0,0); calDate.setDate(1);
  let start = null; let end = null; let selectedColorId = ''; let availabilityRequest = null;

  function iso(dateObject) { const year=dateObject.getFullYear(); const month=String(dateObject.getMonth()+1).padStart(2,'0'); const day=String(dateObject.getDate()).padStart(2,'0'); return `${year}-${month}-${day}`; }
  function fromIso(value) { const [year,month,day]=value.split('-').map(Number); return new Date(year,month-1,day); }
  function formatDate(dateObject) { return dateObject.toLocaleDateString(locale,{day:'2-digit',month:'short',year:'numeric'}); }
  function formatMoney(value) { return `${new Intl.NumberFormat(locale,{minimumFractionDigits:0,maximumFractionDigits:2}).format(value)} ₼`; }
  function isBlocked(dateObject) { const day=iso(dateObject); return blockedRanges.some(range => day >= range.start && day <= range.end); }
  function inSelected(dateObject) { if (!start) return false; const timestamp=dateObject.getTime(); if (!end) return timestamp===start.getTime(); return timestamp>=start.getTime() && timestamp<=end.getTime(); }
  function rangeHasBlocked(firstDate,lastDate) { const cursor=new Date(firstDate); while(cursor<=lastDate){ if(isBlocked(cursor)) return true; cursor.setDate(cursor.getDate()+1);} return false; }
  function selectedDays() { if(!start||!end) return 0; return Math.floor((end.getTime()-start.getTime())/86400000)+1; }
  function resetRange() { start=null; end=null; $('#startDate, #endDate').val(''); updateSummary(); }

  function updateSummary() {
    const rate = `<span>${formatMoney(dailyPrice)} / ${text.day}</span>`;
    if (!start) {
      $('#dateSummary').html(`<div class="date-summary__dates"><span>${text.selectDates}</span></div><div class="rental-price-calc">${rate}<strong>—</strong></div>`); return;
    }
    $('#startDate').val(iso(start)); $('#endDate').val(end ? iso(end) : '');
    if (!end) {
      $('#dateSummary').html(`<div class="date-summary__dates"><span>${formatDate(start)}</span><b>→</b><span>…</span></div><div class="rental-price-calc">${rate}<strong>—</strong></div>`); return;
    }
    const days=selectedDays(); const total=dailyPrice*days;
    $('#dateSummary').html(`<div class="date-summary__dates"><span>${formatDate(start)}</span><b>→</b><span>${formatDate(end)}</span><em>${days} ${text.days}</em></div><div class="rental-price-calc"><span>${formatMoney(dailyPrice)} × ${days} ${text.days}</span><strong>${formatMoney(total)}</strong></div>`);
  }

  function currentMonthKey(dateObject) { return dateObject.getFullYear()*12+dateObject.getMonth(); }
  function renderCalendar() {
    if (!booking.length) return;
    $('#calTitle').text(calDate.toLocaleDateString(locale,{month:'long',year:'numeric'})); const grid=$('#bookingCalendar').empty(); const first=new Date(calDate.getFullYear(),calDate.getMonth(),1); const offset=(first.getDay()+6)%7;
    for(let index=0;index<offset;index+=1) grid.append('<span class="cal-day empty"></span>');
    const totalDays=new Date(calDate.getFullYear(),calDate.getMonth()+1,0).getDate(); const today=new Date(); today.setHours(0,0,0,0);
    for(let day=1;day<=totalDays;day+=1){
      const dateObject=new Date(calDate.getFullYear(),calDate.getMonth(),day); const past=dateObject<today; const blocked=isBlocked(dateObject); const button=$('<button type="button" class="cal-day"></button>').text(day).attr('data-date',iso(dateObject));
      if(past) button.prop('disabled',true).addClass('past'); else if(blocked) button.prop('disabled',true).addClass('blocked'); else button.addClass('free');
      if(inSelected(dateObject)) button.addClass('selected'); if(dateObject.getTime()===today.getTime()) button.addClass('today'); grid.append(button);
    }
    const thisMonth=new Date(); thisMonth.setDate(1); thisMonth.setHours(0,0,0,0); $('#calPrev').prop('disabled',currentMonthKey(calDate)<=currentMonthKey(thisMonth));
  }

  function showMessage(message,type){ $('#reservationMessage').removeClass('error success muted').addClass(type||'').html(message||''); }
  function availabilityUrl(){ let url=`/ajax/products/${productId}/booked-dates/`; if(selectedColorId) url+=`?color=${encodeURIComponent(selectedColorId)}`; return url; }
  function loadAvailability(silent){
    if(!booking.length) return;
    if($('.swatch').length && !selectedColorId){ blockedRanges=[]; renderCalendar(); return; }
    if(availabilityRequest) availabilityRequest.abort(); booking.addClass('is-loading'); if(!silent) showMessage(text.loading,'muted');
    availabilityRequest=$.ajax({url:availabilityUrl(),method:'GET',success:function(data){ blockedRanges=data.ranges||[]; const serverPrice=parseFloat(String(data.daily_price||dailyPrice).replace(',','.')); if(!Number.isNaN(serverPrice)) dailyPrice=serverPrice; resetRange(); renderCalendar(); if(!silent) showMessage('','');},error:function(){blockedRanges=[];resetRange();renderCalendar();if(!silent)showMessage(text.invalid,'error');},complete:function(){booking.removeClass('is-loading');availabilityRequest=null;}});
  }

  $('.swatch').on('click',function(){ $('.swatch').removeClass('active'); $(this).addClass('active'); selectedColorId=String($(this).data('color-id')||''); const colorName=$(this).data('color-'+lang)||$(this).data('color-ru')||''; $('#selectedColorInput').val(selectedColorId); $('#selectedColorName').text(colorName); $('#bookingColorLabel').text(colorName); setMediaForColor(selectedColorId); if(booking.length) loadAvailability(); });
  $('#bookingSize').on('change',function(){ $('#selectedSizeInput').val($(this).val()); });
  if($('.swatch').length) $('.swatch').first().trigger('click'); else { setMediaForColor('default'); if(booking.length) loadAvailability(); }

  $('#bookingCalendar').on('click','.cal-day.free:not(:disabled)',function(){ const chosen=fromIso($(this).data('date')); if(!start||end||chosen<start){start=chosen;end=null;showMessage('','');}else{if(rangeHasBlocked(start,chosen)){showMessage(text.unavailable,'error');return;}end=chosen;showMessage('','');} updateSummary();renderCalendar(); });
  $('#calPrev').on('click',function(){ if($(this).prop('disabled'))return;calDate.setMonth(calDate.getMonth()-1);renderCalendar(); });
  $('#calNext').on('click',function(){ calDate.setMonth(calDate.getMonth()+1);renderCalendar(); });

  $('#reservationForm').on('submit',function(event){
    event.preventDefault();
    if($('.swatch').length&&!selectedColorId){showMessage(text.chooseColor,'error');return;} if(!$('#bookingSize').val()){showMessage(text.chooseSize,'error');return;} if(!start||!end){showMessage(text.choosePeriod,'error');return;}
    $('#selectedSizeInput').val($('#bookingSize').val()); const submitButton=$('#reservationSubmit').prop('disabled',true);
    $.ajax({url:`/ajax/products/${productId}/reserve/`,method:'POST',data:$(this).serialize(),success:function(data){ const total=parseFloat(String(data.total_price||dailyPrice*selectedDays()).replace(',','.'))||0; showMessage(`<strong>${text.sent}</strong><span class="booking-code">${text.code}: ${data.booking_code}</span><span class="booking-price-confirm">${text.total}: ${formatMoney(total)}</span>`,'success'); resetRange();loadAvailability(true);},error:function(xhr){const payload=xhr.responseJSON||{};let message=text.invalid;const errors=payload.errors||{};if(errors.start_date||errors.end_date)message=text.unavailable;if(errors.color)message=text.chooseColor;if(errors.size)message=text.chooseSize;showMessage(message,'error');loadAvailability(true);},complete:function(){submitButton.prop('disabled',false);}});
  });

  setMediaMode('photos'); updateSummary(); renderCalendar();
})(jQuery);
