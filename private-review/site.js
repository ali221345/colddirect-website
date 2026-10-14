(() => {
  'use strict';
  const menu = document.getElementById('review-navigation');
  const toggle = document.querySelector('.menu-toggle');
  const mobile = window.matchMedia('(max-width: 900px)');
  function setMenu(open) {
    menu.dataset.mobileCollapsed = String(!open);
    toggle.setAttribute('aria-expanded', String(open));
  }
  if (menu && toggle) {
    setMenu(false);
    toggle.addEventListener('click', () => setMenu(toggle.getAttribute('aria-expanded') !== 'true'));
    document.addEventListener('keydown', e => {
      if (e.key === 'Escape' && mobile.matches && toggle.getAttribute('aria-expanded') === 'true') {
        setMenu(false); toggle.focus();
      }
    });
    menu.addEventListener('click', e => { if (e.target.closest('a') && mobile.matches) setMenu(false); });
    document.addEventListener('click', e => {
      if (mobile.matches && !e.target.closest('.review-header')) setMenu(false);
    });
    mobile.addEventListener('change', () => setMenu(false));
  }
  const search = document.getElementById('service-search');
  const cards = [...document.querySelectorAll('[data-service-card]')];
  const filters = [...document.querySelectorAll('[data-service-filter]')];
  let category = 'all';
  function filterServices() {
    const term = search.value.trim().toLocaleLowerCase();
    let count = 0;
    cards.forEach(card => {
      const visible = (category === 'all' || card.dataset.category === category) && card.textContent.toLocaleLowerCase().includes(term);
      card.hidden = !visible;
      if (visible) count++;
    });
    document.getElementById('results-status').textContent = `${count} ${count === 1 ? 'service' : 'services'} found`;
    document.getElementById('no-results').hidden = count !== 0;
  }
  if (search) {
    search.addEventListener('input', filterServices);
    filters.forEach(button => button.addEventListener('click', () => {
      category = button.dataset.serviceFilter;
      filters.forEach(item => item.setAttribute('aria-pressed', String(item === button)));
      filterServices();
    }));
  }
  const form = document.getElementById('enquiry-form');
  if (form) {
    form.addEventListener('submit', e => {
      e.preventDefault();
      if (!form.reportValidity()) return;
      const data = new FormData(form);
      const value = key => String(data.get(key) || '').trim();
      const message = `Hello ColdDirect,\n\nI'd like to discuss ${value('service')}.\n\nName: ${value('name')}\nBusiness: ${value('business') || 'Not provided'}\nPhone: ${value('phone')}\nEmail: ${value('email')}\nSite postcode: ${value('postcode')}\nEquipment / fault:\n${value('message')}\n\nPlease confirm availability, proposed work and costs.\nThank you.`;
      document.getElementById('draft-text').value = message;
      document.getElementById('email-draft-link').href = `mailto:info@colddirect.co.uk?subject=${encodeURIComponent('ColdDirect enquiry — ' + value('service') + ' — ' + value('postcode'))}&body=${encodeURIComponent(message)}`;
      document.getElementById('draft-result').hidden = false;
      document.getElementById('form-status').textContent = 'Your draft is ready. Open your email app and send it, or copy it into an email. No enquiry has been sent yet.';
      document.getElementById('draft-heading').focus();
    });
    document.getElementById('copy-draft').addEventListener('click', async () => {
      const field = document.getElementById('draft-text');
      try {
        await navigator.clipboard.writeText(field.value);
        document.getElementById('copy-status').textContent = 'Copied. Paste into an email to info@colddirect.co.uk.';
      } catch {
        field.focus(); field.select();
        document.getElementById('copy-status').textContent = 'Draft selected. Copy it and paste into an email to info@colddirect.co.uk.';
      }
    });
    const preselected = new URLSearchParams(location.search).get('service');
    const select = document.getElementById('enquiry-service');
    if (preselected && [...select.options].some(option => option.value === preselected)) select.value = preselected;
  }
})();
