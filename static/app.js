/* A dependency-free, two-page kiosk frontend. No data leaves your network. */
(() => {
  const el = (id) => document.getElementById(id);
  let active = 0;
  let refreshSeconds = 5;
  let rotateSeconds = 12;
  let refreshTimer;
  let rotateTimer;
  let busy = false;

  const set = (id, value) => { el(id).textContent = value; };
  const number = (value) => (value === null || value === undefined || value === '' || !Number.isFinite(Number(value))) ? null : Number(value);
  const percentage = (v) => {
    const n = number(v);
    return n === null ? null : Math.max(0, Math.min(100, n));
  };
  const pct = (v) => percentage(v) === null ? '—' : `${percentage(v).toFixed(1)}%`;
  const bytes = (v) => {
    const n = number(v);
    if (n === null) return '—';
    if (n < 1024) return `${n.toFixed(0)} B`;
    const unit = Math.min(4, Math.floor(Math.log(n) / Math.log(1024)));
    return `${(n / 1024 ** unit).toFixed(1)} ${['B','KB','MB','GB','TB'][unit]}`;
  };
  const uptime = (seconds) => {
    const s = number(seconds);
    if (s === null) return '—';
    const days = Math.floor(s / 86400), hours = Math.floor((s % 86400) / 3600), minutes = Math.floor((s % 3600) / 60);
    return days ? `${days}d ${hours}h` : hours ? `${hours}h ${minutes}m` : `${minutes}m`;
  };
  const temp = (value) => number(value) === null ? '—' : `${Number(value).toFixed(1)}°C`;
  const parts = (id, value, unit) => {
    el(id).replaceChildren(document.createTextNode(value === null ? '—' : Number(value).toFixed(1)));
    if (value !== null) { const small = document.createElement('small'); small.textContent = unit; el(id).appendChild(small); }
  };
  const bar = (id, value) => { el(id).style.width = `${percentage(value) ?? 0}%`; };

  function renderServices(services) {
    const list = el('service-list');
    list.replaceChildren();
    if (!Array.isArray(services) || services.length === 0) {
      const empty = document.createElement('div'); empty.className = 'empty-state';
      empty.textContent = 'No services configured. Add TCP checks in .env → SERVICES_JSON';
      list.appendChild(empty); return;
    }
    for (const service of services) {
      const row = document.createElement('div'); row.className = 'service-row';
      const dot = document.createElement('span'); dot.className = `service-indicator ${service.online ? '' : 'down'}`;
      const info = document.createElement('div');
      const name = document.createElement('strong'); name.textContent = service.name;
      const desc = document.createElement('small'); desc.textContent = `TCP PORT ${service.port}`;
      info.append(name, desc);
      const state = document.createElement('b'); state.className = service.online ? '' : 'down';
      state.textContent = service.online ? `${service.latency_ms ?? '—'} ms` : 'OFFLINE';
      row.append(dot, info, state); list.appendChild(row);
    }
  }

  function render(data) {
    const server = data.server ?? {};
    const pi = data.pi ?? {};
    const stats = server.stats;
    const mode = server.mode === 'remote' ? 'REMOTE SERVER' : 'LOCAL PI MODE';
    const isOffline = server.mode === 'remote' && !server.connected;

    set('source-badge', isOffline ? 'SERVER OFFLINE' : mode);
    el('source-badge').parentElement.classList.toggle('offline', isOffline);
    set('overview-subtitle', server.mode === 'pi'
      ? 'Showing Raspberry Pi stats · connect the optional server agent for remote telemetry.'
      : isOffline ? 'Remote server unavailable · see Network & Services for details.'
      : 'Live telemetry from your remote server.');
    set('node-name', server.mode === 'pi' ? 'Raspberry Pi' : (server.name || 'My Server'));
    set('host-name', stats?.hostname ?? '—');
    set('host-ip', stats?.ip ?? '—');
    set('cpu-cores', stats?.cpu_cores ?? '—');
    set('uptime', uptime(stats?.uptime_seconds));
    parts('cpu-value', percentage(stats?.cpu_percent), '%');
    el('cpu-gauge').style.setProperty('--level', `${percentage(stats?.cpu_percent) ?? 0}%`);
    parts('mem-percent', percentage(stats?.memory_percent), '%');
    set('mem-used', stats ? `${bytes(stats.memory_used)} / ${bytes(stats.memory_total)}` : '— / —');
    bar('mem-bar', stats?.memory_percent);
    parts('disk-percent', percentage(stats?.disk_percent), '%');
    set('disk-used', stats ? `${bytes(stats.disk_used)} / ${bytes(stats.disk_total)}` : '— / —');
    bar('disk-bar', stats?.disk_percent);
    parts('temp-value', number(stats?.temperature_c), '°C');
    set('temp-note', stats?.temperature_c == null ? 'SENSOR NOT AVAILABLE' : 'CPU SENSOR');

    set('server-name', server.name || 'My Server');
    set('connection-status', server.mode === 'pi' ? 'Pi-only mode' : (server.connected ? 'Connected' : 'Disconnected'));
    set('connection-hint', server.mode === 'pi' ? 'Add remote agent details to .env' : (server.connected ? 'Receiving remote telemetry' : 'Cannot reach the remote agent'));
    set('server-latency', server.latency_ms != null ? `${server.latency_ms} ms` : '—');
    set('server-source', server.mode === 'pi' ? 'LOCAL METRICS' : 'REMOTE AGENT');
    el('connection-dot').classList.toggle('down', isOffline);
    renderServices(data.services);
    set('pi-hostname', pi.hostname ?? '—');
    set('pi-ip', pi.ip ?? '—');
    set('pi-cpu', pct(pi.cpu_percent));
    set('pi-memory', pct(pi.memory_percent));
    set('pi-temp', temp(pi.temperature_c));
    set('pi-uptime', uptime(pi.uptime_seconds));
    set('net-recv', bytes(pi.net_recv));
    set('net-sent', bytes(pi.net_sent));
    set('last-updated', 'SYNCED · ' + new Date().toLocaleTimeString([], {hour:'2-digit',minute:'2-digit',second:'2-digit'}));

    const nextRefresh = Number(data.settings?.refresh_seconds);
    const nextRotate = Number(data.settings?.rotate_seconds);
    if (Number.isInteger(nextRefresh) && nextRefresh >= 2 && nextRefresh !== refreshSeconds) { refreshSeconds = nextRefresh; startRefresh(); }
    if (Number.isInteger(nextRotate) && nextRotate >= 4 && nextRotate !== rotateSeconds) { rotateSeconds = nextRotate; startRotation(); }
    set('refresh-speed', `${refreshSeconds}s`);
    set('rotation-speed', `${rotateSeconds}s`);
  }

  async function fetchData() {
    if (busy) return;
    busy = true;
    try {
      const result = await fetch('/api/state', { cache: 'no-store', signal: AbortSignal.timeout(8000) });
      if (!result.ok) throw new Error('Metrics not available');
      render(await result.json());
    } catch (err) {
      set('last-updated', 'DISCONNECTED · RETRYING');
      el('last-updated').classList.add('offline');
    } finally { busy = false; }
  }

  function showPage(index, manual = false) {
    active = (index + 2) % 2;
    for (let i = 0; i < 2; i++) {
      const page = el(i === 0 ? 'page-overview' : 'page-network');
      page.hidden = i !== active;
      page.classList.toggle('active', i === active);
      const dot = document.querySelector(`[data-page="${i}"]`);
      dot.classList.toggle('active', i === active);
      if (i === active) dot.setAttribute('aria-current', 'page');
      else dot.removeAttribute('aria-current');
    }
    set('page-count', `0${active + 1} / 02`);
    if (manual) startRotation();
  }
  function startRefresh() { clearInterval(refreshTimer); refreshTimer = setInterval(fetchData, refreshSeconds * 1000); }
  function startRotation() { clearInterval(rotateTimer); rotateTimer = setInterval(() => showPage(active + 1), rotateSeconds * 1000); }
  function tickClock() {
    const date = new Date();
    set('clock', date.toLocaleTimeString([], { hour:'2-digit', minute:'2-digit', hour12:false }));
    set('date', date.toLocaleDateString([], { weekday:'short', day:'2-digit', month:'short' }).toUpperCase());
  }
  el('prev').addEventListener('click', () => showPage(active - 1, true));
  el('next').addEventListener('click', () => showPage(active + 1, true));
  for (const dot of document.querySelectorAll('[data-page]')) dot.addEventListener('click', () => showPage(Number(dot.dataset.page), true));
  document.addEventListener('keydown', (event) => {
    if (event.key === 'ArrowRight') showPage(active + 1, true);
    if (event.key === 'ArrowLeft') showPage(active - 1, true);
  });
  tickClock(); setInterval(tickClock, 1000); fetchData(); startRefresh(); startRotation();
})();
