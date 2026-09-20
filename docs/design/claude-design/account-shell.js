/* Shared nav + sidebar injector for goimg account screens.
   Each page sets window.__page = { key: 'upload'|'photos'|'albums'|'edit-profile'|'account'|'notifications'|'insights'|'edit-photo', title: '...' }
   before this script runs. */
(function(){
  const p = window.__page || {};

  const SIDE = [
    { group: 'Library', items: [
      { key: 'photos',       label: 'My Photos',   href: 'My Photos.html',       count: '312',
        svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="14" rx="2"/><circle cx="9" cy="11" r="2"/><path d="m21 15-5-4-9 7"/></svg>' },
      { key: 'albums',       label: 'Albums',      href: 'My Albums.html',       count: '24',
        svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7" rx="1.5"/><rect x="14" y="3" width="7" height="7" rx="1.5"/><rect x="3" y="14" width="7" height="7" rx="1.5"/><rect x="14" y="14" width="7" height="7" rx="1.5"/></svg>' },
      { key: 'upload',       label: 'Upload',      href: 'Upload Studio.html',
        svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3v13"/><path d="m7 8 5-5 5 5"/><path d="M5 21h14"/></svg>' },
      { key: 'insights',     label: 'Insights',    href: 'Photo Insights.html',
        svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M3 3v18h18"/><path d="M7 14l4-4 3 3 5-7"/></svg>' },
    ]},
    { group: 'Account', items: [
      { key: 'edit-profile', label: 'Edit Profile', href: 'Edit Profile.html',
        svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="8" r="4"/><path d="M4 21c0-4 4-7 8-7s8 3 8 7"/></svg>' },
      { key: 'account',      label: 'Account',      href: 'Account Settings.html',
        svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.7 1.7 0 0 0 .3 1.8l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.7 1.7 0 0 0-1.8-.3 1.7 1.7 0 0 0-1 1.5V21a2 2 0 0 1-4 0v-.1a1.7 1.7 0 0 0-1.1-1.5 1.7 1.7 0 0 0-1.8.3l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1a1.7 1.7 0 0 0 .3-1.8 1.7 1.7 0 0 0-1.5-1H3a2 2 0 0 1 0-4h.1a1.7 1.7 0 0 0 1.5-1.1 1.7 1.7 0 0 0-.3-1.8l-.1-.1a2 2 0 1 1 2.8-2.8l.1.1a1.7 1.7 0 0 0 1.8.3h0a1.7 1.7 0 0 0 1-1.5V3a2 2 0 0 1 4 0v.1a1.7 1.7 0 0 0 1 1.5 1.7 1.7 0 0 0 1.8-.3l.1-.1a2 2 0 1 1 2.8 2.8l-.1.1a1.7 1.7 0 0 0-.3 1.8v0a1.7 1.7 0 0 0 1.5 1H21a2 2 0 0 1 0 4h-.1a1.7 1.7 0 0 0-1.5 1z"/></svg>' },
      { key: 'notifications',label: 'Notifications & Privacy', href: 'Notifications.html',
        svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9"/><path d="M10.3 21a1.94 1.94 0 0 0 3.4 0"/></svg>' },
    ]},
  ];

  const navHtml = `
    <header class="nav">
      <a class="brand" href="Lumen Atlas Gallery.html">
        <span class="brand-mark" aria-hidden="true"></span>
        <span class="brand-name"><b>go</b><span>img</span></span>
      </a>
      <label class="nav-search" aria-label="Search">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="16" height="16"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>
        <input placeholder="Search your library…" />
      </label>
      <div class="nav-actions">
        <button class="icon-btn" aria-label="Notifications">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9"/><path d="M10.3 21a1.94 1.94 0 0 0 3.4 0"/></svg>
        </button>
        <a class="icon-btn" href="Upload Studio.html" aria-label="Upload">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3v13"/><path d="m7 8 5-5 5 5"/><path d="M5 21h14"/></svg>
        </a>
        <span class="avatar">MK</span>
      </div>
    </header>`;

  const sideSections = SIDE.map(sec => `
    <div class="side-section">
      <div class="side-section-title">${sec.group}</div>
    </div>
    ${sec.items.map(it => `
      <a class="side-link${it.key === p.key ? ' active' : ''}" href="${it.href}">
        <span class="ico">${it.svg}</span>
        <span>${it.label}</span>
        ${it.count ? `<span class="aside">${it.count}</span>` : ''}
      </a>
    `).join('')}
  `).join('');

  const sidebarHtml = `
    <aside class="sidebar" aria-label="Account sections">
      ${sideSections}
      <div class="side-section"><div class="side-section-title">Help</div></div>
      <a class="side-link" href="#">
        <span class="ico"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><path d="M9.1 9a3 3 0 0 1 5.8 1c0 2-3 3-3 3"/><path d="M12 17h.01"/></svg></span>
        <span>Help &amp; Support</span>
      </a>
      <a class="side-link" href="Lumen Atlas Gallery.html">
        <span class="ico"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="m15 18-6-6 6-6"/></svg></span>
        <span>Back to gallery</span>
      </a>
    </aside>`;

  // Mobile select for account navigation
  const flat = SIDE.flatMap(s => s.items);
  const mobileSelect = `
    <div class="mobile-header-menu">
      <select onchange="if(this.value) location.href=this.value">
        ${flat.map(it => `<option value="${it.href}"${it.key === p.key ? ' selected' : ''}>${it.label}</option>`).join('')}
      </select>
    </div>`;

  const mobileTabs = `
    <nav class="mobile-tabs" aria-label="Mobile navigation">
      <a class="tab-m" href="Lumen Atlas Gallery.html" aria-label="Home">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"><path d="m3 11 9-8 9 8"/><path d="M5 10v10h14V10"/></svg>Home
      </a>
      <a class="tab-m${p.key === 'photos' ? ' active' : ''}" href="My Photos.html" aria-label="Library">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="14" rx="2"/><circle cx="9" cy="11" r="2"/><path d="m21 15-5-4-9 7"/></svg>Library
      </a>
      <a class="tab-m${p.key === 'upload' ? ' active' : ''}" href="Upload Studio.html" aria-label="Upload">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M12 5v14M5 12h14"/></svg>Upload
      </a>
      <a class="tab-m${p.key === 'insights' ? ' active' : ''}" href="Photo Insights.html" aria-label="Insights">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"><path d="M3 3v18h18"/><path d="M7 14l4-4 3 3 5-7"/></svg>Insights
      </a>
      <a class="tab-m${['edit-profile','account','notifications'].includes(p.key) ? ' active' : ''}" href="Edit Profile.html" aria-label="Profile">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="8" r="4"/><path d="M4 21c0-4 4-7 8-7s8 3 8 7"/></svg>You
      </a>
    </nav>`;

  // Inject
  const navHolder = document.getElementById('nav-slot');
  if (navHolder) navHolder.outerHTML = navHtml;
  const sideHolder = document.getElementById('sidebar-slot');
  if (sideHolder) sideHolder.outerHTML = sidebarHtml;
  const mobileHeaderHolder = document.getElementById('mobile-header-slot');
  if (mobileHeaderHolder) mobileHeaderHolder.outerHTML = mobileSelect;
  const mobileTabHolder = document.getElementById('mobile-tabs-slot');
  if (mobileTabHolder) mobileTabHolder.outerHTML = mobileTabs;
})();
