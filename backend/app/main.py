from fastapi import FastAPI
from fastapi.responses import HTMLResponse, RedirectResponse

from backend.app.routers.health import router as health_router
from backend.app.routers.offers import router as offers_router
from backend.app.routers.reports import router as reports_router

app = FastAPI(title="Car Data Warehouse API", version="1.0.0")

app.include_router(health_router)
app.include_router(offers_router)
app.include_router(reports_router)


@app.get("/", include_in_schema=False)
def root() -> RedirectResponse:
    return RedirectResponse(url="/dashboard")


@app.get("/dashboard", include_in_schema=False, response_class=HTMLResponse)
def dashboard() -> str:
    return """
<!doctype html>
<html lang="pl">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;600;700;800&display=swap" rel="stylesheet">
  <title>Hurtownia danych - rynek aut używanych</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <style>
    :root {
      --bg0: #0a0f18;
      --bg1: #0f1724;
      --panel: rgba(16, 24, 38, 0.88);
      --panel-strong: rgba(20, 30, 48, 0.96);
      --ink: #e8eef8;
      --muted: #9aa9c0;
      --border: rgba(102, 124, 160, 0.35);
      --accent: #58a6ff;
      --accent-2: #32d3a4;
      --accent-3: #ffb65f;
      --accent-4: #ff7d86;
      --shadow: 0 10px 28px rgba(0, 0, 0, 0.35);
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: "IBM Plex Sans", "Segoe UI", "Arial", sans-serif;
      color: var(--ink);
      background:
        radial-gradient(1200px 450px at 8% -8%, #1a2b43 0%, transparent 60%),
        radial-gradient(900px 380px at 95% -10%, #16273d 0%, transparent 65%),
        linear-gradient(180deg, var(--bg1), var(--bg0));
      min-height: 100vh;
    }
    .wrap {
      max-width: 1260px;
      margin: 0 auto;
      padding: 22px 16px 32px;
    }
    .head {
      background: linear-gradient(140deg, var(--panel-strong), var(--panel));
      border: 1px solid var(--border);
      border-radius: 16px;
      box-shadow: var(--shadow);
      padding: 16px 18px;
      margin-bottom: 14px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 10px;
      flex-wrap: wrap;
    }
    .head h1 {
      margin: 0;
      font-size: 24px;
      letter-spacing: 0.01em;
    }
    .head p {
      margin: 6px 0 0;
      color: var(--muted);
      font-size: 14px;
    }
    .head-right {
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .chip {
      border: 1px solid var(--border);
      background: rgba(88, 166, 255, 0.12);
      border-radius: 999px;
      padding: 7px 11px;
      font-size: 12px;
      color: #c9ddff;
      font-weight: 700;
      letter-spacing: 0.02em;
    }
    .btn {
      border: 1px solid rgba(88, 166, 255, 0.5);
      border-radius: 11px;
      padding: 8px 12px;
      background: linear-gradient(180deg, #3f86df, #2f6ec2);
      color: #f2f7ff;
      cursor: pointer;
      font-weight: 700;
      transition: transform 0.15s ease, filter 0.15s ease;
    }
    .btn:hover {
      filter: brightness(1.06);
      transform: translateY(-1px);
    }
    .filters {
      margin-bottom: 12px;
      display: grid;
      grid-template-columns: repeat(4, minmax(120px, 1fr));
      gap: 8px;
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: 13px;
      box-shadow: var(--shadow);
      padding: 11px;
    }
    .filters label {
      display: block;
      font-size: 12px;
      color: var(--muted);
      margin-bottom: 4px;
      font-weight: 700;
      letter-spacing: 0.02em;
    }
    .filters select,
    .filters input {
      width: 100%;
      border: 1px solid rgba(109, 132, 170, 0.55);
      border-radius: 9px;
      padding: 8px;
      background: rgba(9, 15, 26, 0.85);
      color: var(--ink);
      outline: none;
    }
    .filters select:focus,
    .filters input:focus {
      border-color: rgba(88, 166, 255, 0.75);
      box-shadow: 0 0 0 2px rgba(88, 166, 255, 0.18);
    }
    .kpis {
      display: grid;
      grid-template-columns: repeat(5, minmax(150px, 1fr));
      gap: 10px;
      margin-bottom: 12px;
    }
    .kpi {
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: 13px;
      box-shadow: var(--shadow);
      padding: 12px;
    }
    .kpi .label {
      font-size: 12px;
      color: var(--muted);
      letter-spacing: 0.02em;
    }
    .kpi .value {
      margin-top: 6px;
      font-size: 25px;
      font-weight: 800;
      color: #f2f7ff;
    }
    .grid {
      display: grid;
      grid-template-columns: repeat(2, minmax(300px, 1fr));
      gap: 10px;
      margin-bottom: 12px;
    }
    .grid-3 {
      grid-template-columns: repeat(3, minmax(250px, 1fr));
    }
    .card {
      background: linear-gradient(170deg, var(--panel-strong), var(--panel));
      border: 1px solid var(--border);
      border-radius: 14px;
      box-shadow: var(--shadow);
      padding: 12px;
      min-height: 320px;
      display: flex;
      flex-direction: column;
    }
    .card h3 {
      margin: 0 0 8px;
      font-size: 15px;
      color: #eaf1fd;
      font-weight: 700;
      letter-spacing: 0.01em;
    }
    .chart-box {
      flex: 1;
      min-height: 250px;
      position: relative;
    }
    canvas {
      width: 100% !important;
      height: 100% !important;
      max-height: none !important;
      display: block;
    }
    .table-wrap {
      border: 1px solid var(--border);
      border-radius: 10px;
      overflow: auto;
      flex: 1;
      min-height: 260px;
      background: rgba(9, 15, 26, 0.7);
    }
    .full-span {
      grid-column: 1 / -1;
    }
    table {
      width: 100%;
      border-collapse: collapse;
      font-size: 13px;
      color: #dce7f8;
    }
    th, td {
      padding: 9px;
      border-bottom: 1px solid rgba(102, 124, 160, 0.2);
      text-align: left;
      white-space: nowrap;
    }
    th {
      position: sticky;
      top: 0;
      background: rgba(31, 46, 71, 0.95);
      color: #e8f0ff;
      z-index: 1;
    }
    tr:hover td {
      background: rgba(88, 166, 255, 0.06);
    }
    @media (max-width: 950px) {
      .grid, .grid-3 { grid-template-columns: 1fr; }
      .filters { grid-template-columns: 1fr 1fr; }
      .kpis { grid-template-columns: repeat(2, minmax(140px, 1fr)); }
    }
  </style>
</head>
<body>
  <div class="wrap">
    <section class="head">
      <div>
        <h1>Hurtownia danych rynku aut używanych - Wrocław</h1>
        <p>Porównanie danych ofertowych (CSV) i rejestracyjnych (CEPiK).</p>
      </div>
      <div class="head-right">
        <select id="currencySelect" style="border:1px solid var(--border);border-radius:10px;padding:7px 10px;background:rgba(9,15,26,.85);color:var(--ink);font-weight:700;">
          <option value="PLN">PLN</option>
        </select>
        <span id="fxBadge" class="chip">NBP: -</span>
        <span id="syncBadge" class="chip">Aktualizacja: -</span>
        <button id="refreshBtn" class="btn">Odśwież</button>
      </div>
    </section>

    <section class="filters">
      <div>
        <label for="brandFilter">Marka</label>
        <select id="brandFilter"><option value="">Wszystkie</option></select>
      </div>
      <div>
        <label for="fuelFilter">Paliwo</label>
        <select id="fuelFilter"><option value="">Wszystkie</option></select>
      </div>
      <div>
        <label for="cityFilter">Miasto (fragment)</label>
        <input id="cityFilter" placeholder="np. Wroclaw" />
      </div>
      <div>
        <label for="modelFilter">Model (fragment)</label>
        <input id="modelFilter" placeholder="np. Octavia" />
      </div>
    </section>

    <section class="kpis">
      <article class="kpi"><div class="label">Liczba ofert (CSV)</div><div id="kpiOffers" class="value">-</div></article>
      <article class="kpi"><div class="label">Liczba rejestracji (CEPiK)</div><div id="kpiRegs" class="value">-</div></article>
      <article class="kpi"><div class="label">Współczynnik ofert/rejestracji</div><div id="kpiRatio" class="value">-</div></article>
      <article class="kpi"><div id="kpiPriceLabel" class="label">Średnia cena (PLN)</div><div id="kpiPrice" class="value">-</div></article>
      <article class="kpi"><div class="label">Średni przebieg</div><div id="kpiMileage" class="value">-</div></article>
      <article class="kpi"><div class="label">Najpopularniejsza marka</div><div id="kpiBrand" class="value">-</div></article>
      <article class="kpi"><div class="label">Najpopularniejsze paliwo</div><div id="kpiTopFuel" class="value">-</div></article>
      <article class="kpi"><div class="label">Udział top marki</div><div id="kpiTopBrandShare" class="value">-</div></article>
      <article class="kpi"><div class="label">Rejestracje / 1000 ofert</div><div id="kpiRegsPer1000" class="value">-</div></article>
      <article class="kpi"><div class="label">Dostępne waluty NBP</div><div id="kpiNbpCurrencies" class="value">-</div></article>
    </section>

    <section class="grid grid-3">
      <article class="card">
        <h3>Top marki - liczba ofert</h3>
        <div class="chart-box"><canvas id="topBrands"></canvas></div>
      </article>
      <article class="card">
        <h3>Udział paliw</h3>
        <div class="chart-box"><canvas id="fuelShare"></canvas></div>
      </article>
      <article class="card">
        <h3>Średnia cena wg rocznika</h3>
        <div class="chart-box"><canvas id="priceByYear"></canvas></div>
      </article>
    </section>

    <section class="grid grid-3">
      <article class="card">
        <h3>Średnia cena wg marki</h3>
        <div class="chart-box"><canvas id="avgPriceByBrand"></canvas></div>
      </article>
      <article class="card">
        <h3>Oferty (CSV) vs rejestracje (CEPiK) wg marki</h3>
        <div class="chart-box"><canvas id="offersVsRegs"></canvas></div>
      </article>
      <article class="card">
        <h3>Rejestracje na 1000 ofert wg marki</h3>
        <div class="chart-box"><canvas id="regsPer1000"></canvas></div>
      </article>
    </section>

    <section class="grid grid-3">
      <article class="card">
        <h3>Top miasta (po filtrach)</h3>
        <div class="chart-box"><canvas id="cityShare"></canvas></div>
      </article>
      <article class="card">
        <h3>Udział rejestracji wg marki (Top 15)</h3>
        <div class="chart-box"><canvas id="regsShareByBrand"></canvas></div>
      </article>
      <article class="card">
        <h3>Udział pojemności silnika (po filtrach)</h3>
        <div class="chart-box"><canvas id="engineCapacityShare"></canvas></div>
      </article>
      <article class="card full-span">
        <h3>Oferty po filtrach</h3>
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Marka</th>
                <th>Model</th>
                <th>Paliwo</th>
                <th>Miasto</th>
                <th>Śr. cena</th>
                <th>Liczba ofert</th>
              </tr>
            </thead>
            <tbody id="offersBody"></tbody>
          </table>
        </div>
      </article>
    </section>
  </div>

<script>
const fmtNum = (v) => new Intl.NumberFormat('pl-PL', { maximumFractionDigits: 0 }).format(v ?? 0);
const fmtMoney = (v) => new Intl.NumberFormat('pl-PL', { maximumFractionDigits: 0 }).format(v ?? 0);
const safe = (x) => (x ?? '').toString();

const state = {
  offers: [],
  filtered: [],
  currency: 'PLN',
  rates: { PLN: 1, EUR: 1, USD: 1 },
  rateSource: '-',
};
const charts = {};
const PALETTE = {
  blue: '#58a6ff',
  green: '#32d3a4',
  amber: '#ffb65f',
  red: '#ff7d86',
  violet: '#8e9bff',
  steel: '#8da5c3',
  grid: 'rgba(125, 149, 186, 0.22)',
  text: '#dce8fa',
};

Chart.defaults.color = PALETTE.text;
Chart.defaults.borderColor = PALETTE.grid;

function getSelectedCurrency() {
  return state.currency || 'PLN';
}

function getRate(currency) {
  if (currency === 'PLN') return 1;
  const rate = Number(state.rates[currency]);
  return Number.isFinite(rate) && rate > 0 ? rate : 1;
}

function convertFromPln(value, currency) {
  const amount = Number(value || 0);
  const rate = getRate(currency);
  if (!rate || !Number.isFinite(rate)) return 0;
  if (currency === 'PLN') return amount;
  return amount / rate;
}

function formatMoneyByCurrency(value, currency) {
  const opts = currency === 'PLN'
    ? { maximumFractionDigits: 0 }
    : { minimumFractionDigits: 2, maximumFractionDigits: 2 };
  const symbol = currency === 'PLN' ? 'PLN' : currency;
  return `${new Intl.NumberFormat('pl-PL', opts).format(value ?? 0)} ${symbol}`;
}

function rebuildCurrencySelect() {
  const select = document.getElementById('currencySelect');
  const current = getSelectedCurrency();
  const rateCodes = Object.keys(state.rates || {}).filter((c) => c !== 'PLN').sort();
  const allCodes = ['PLN', ...rateCodes];
  select.innerHTML = allCodes.map((code) => `<option value="${code}">${code}</option>`).join('');
  if (allCodes.includes(current)) {
    select.value = current;
  } else {
    state.currency = 'PLN';
    select.value = 'PLN';
  }
}

function renderFxBadge() {
  const fxBadge = document.getElementById('fxBadge');
  if (!fxBadge) return;
  const entries = Object.entries(state.rates || {})
    .filter(([code]) => code !== 'PLN')
    .sort((a, b) => a[0].localeCompare(b[0]));
  if (!entries.length) {
    fxBadge.textContent = `NBP: brak kursów (${state.rateSource})`;
    return;
  }
  const top = entries.slice(0, 4).map(([code, value]) => `${code} ${Number(value).toFixed(4)}`).join(' | ');
  const suffix = entries.length > 4 ? ` +${entries.length - 4}` : '';
  fxBadge.textContent = `NBP ${top}${suffix} (${state.rateSource})`;
}

async function getJson(path) {
  const r = await fetch(path);
  if (!r.ok) throw new Error(`${path}: ${r.status}`);
  return r.json();
}

function setChart(id, cfg) {
  if (charts[id]) charts[id].destroy();
  charts[id] = new Chart(document.getElementById(id), cfg);
}

function bar(id, labels, values, color) {
  setChart(id, {
    type: 'bar',
    data: { labels, datasets: [{ data: values, backgroundColor: color, borderRadius: 8 }] },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: { y: { beginAtZero: true, grid: { color: PALETTE.grid } } },
    },
  });
}

function line(id, labels, values, color) {
  setChart(id, {
    type: 'line',
    data: { labels, datasets: [{ data: values, borderColor: color, backgroundColor: color + '33', fill: true, tension: 0.2 }] },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: { y: { beginAtZero: true, grid: { color: PALETTE.grid } } },
    },
  });
}

function doughnut(id, labels, values) {
  setChart(id, {
    type: 'doughnut',
    data: {
      labels: labels.length ? labels : ['Brak danych'],
      datasets: [{ data: values.length ? values : [1], backgroundColor: [PALETTE.blue, PALETTE.green, PALETTE.amber, PALETTE.red, PALETTE.violet, PALETTE.steel] }],
    },
    options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'bottom' } } },
  });
}

function horizontalBar(id, labels, values, color) {
  setChart(id, {
    type: 'bar',
    data: {
      labels,
      datasets: [{ data: values, backgroundColor: color, borderRadius: 6 }],
    },
    options: {
      indexAxis: 'y',
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: { x: { beginAtZero: true, grid: { color: PALETTE.grid } } },
    },
  });
}

function groupedBar(id, labels, offersValues, regsValues) {
  setChart(id, {
    type: 'bar',
    data: {
      labels,
      datasets: [
        {
          label: 'Oferty (CSV)',
          data: offersValues,
          backgroundColor: PALETTE.blue,
          borderRadius: 6,
        },
        {
          label: 'Rejestracje (CEPiK)',
          data: regsValues,
          backgroundColor: PALETTE.red,
          borderRadius: 6,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { mode: 'index', intersect: false },
      scales: {
        y: {
          beginAtZero: true,
          title: { display: true, text: 'Liczba (ta sama skala dla obu źródeł)' },
          grid: { color: PALETTE.grid },
        },
      },
    },
  });
}

function topBy(rows, key, valueKey = 'offers_count', limit = 8) {
  const map = new Map();
  rows.forEach((r) => {
    const label = safe(r[key]) || 'Brak';
    map.set(label, (map.get(label) || 0) + (Number(r[valueKey]) || 0));
  });
  return [...map.entries()].sort((a, b) => b[1] - a[1]).slice(0, limit);
}

function getEngineCapacityBucket(value) {
  const cc = Number(value);
  if (!Number.isFinite(cc) || cc <= 0) return 'Brak danych';
  if (cc <= 1200) return '<= 1200';
  if (cc <= 1600) return '1201 - 1600';
  if (cc <= 2000) return '1601 - 2000';
  if (cc <= 2500) return '2001 - 2500';
  return '> 2500';
}

function engineCapacityBuckets(rows) {
  const labels = ['<= 1200', '1201 - 1600', '1601 - 2000', '2001 - 2500', '> 2500', 'Brak danych'];
  const totals = new Map(labels.map((l) => [l, 0]));
  rows.forEach((r) => {
    const bucket = getEngineCapacityBucket(r.engine_capacity);
    const count = Number(r.offers_count) || 0;
    totals.set(bucket, (totals.get(bucket) || 0) + count);
  });
  return labels
    .map((label) => [label, totals.get(label) || 0])
    .filter(([, value]) => value > 0);
}

function buildFilters() {
  const brands = [...new Set(state.offers.map((x) => safe(x.brand)).filter(Boolean))].sort();
  const fuels = [...new Set(state.offers.map((x) => safe(x.fuel_type)).filter(Boolean))].sort();
  document.getElementById('brandFilter').innerHTML = '<option value="">Wszystkie</option>' + brands.map((v) => `<option value="${v}">${v}</option>`).join('');
  document.getElementById('fuelFilter').innerHTML = '<option value="">Wszystkie</option>' + fuels.map((v) => `<option value="${v}">${v}</option>`).join('');
}

function applyFilters() {
  const brand = document.getElementById('brandFilter').value;
  const fuel = document.getElementById('fuelFilter').value;
  const city = document.getElementById('cityFilter').value.trim().toLowerCase();
  const model = document.getElementById('modelFilter').value.trim().toLowerCase();
  state.filtered = state.offers.filter((r) => {
    if (brand && safe(r.brand) !== brand) return false;
    if (fuel && safe(r.fuel_type) !== fuel) return false;
    if (city && !safe(r.city).toLowerCase().includes(city)) return false;
    if (model && !safe(r.model).toLowerCase().includes(model)) return false;
    return true;
  });
  renderFiltered();
}

function renderFiltered() {
  const rows = state.filtered;
  const currency = getSelectedCurrency();
  const cityTop = topBy(rows, 'city', 'offers_count', 7);
  const engineTop = engineCapacityBuckets(rows);
  doughnut('cityShare', cityTop.map((x) => x[0]), cityTop.map((x) => x[1]));
  doughnut('engineCapacityShare', engineTop.map((x) => x[0]), engineTop.map((x) => x[1]));

  const tbody = document.getElementById('offersBody');
  tbody.innerHTML = rows
    .slice()
    .sort((a, b) => (Number(b.offers_count) || 0) - (Number(a.offers_count) || 0))
    .slice(0, 40)
    .map((r) => `
      <tr>
        <td>${safe(r.brand)}</td>
        <td>${safe(r.model)}</td>
        <td>${safe(r.fuel_type)}</td>
        <td>${safe(r.city)}</td>
        <td>${formatMoneyByCurrency(convertFromPln(Number(r.avg_price_pln) || 0, currency), currency)}</td>
        <td>${fmtNum(Number(r.offers_count) || 0)}</td>
      </tr>
    `)
    .join('');
}

async function loadData() {
  const [fx, kpi, topBrands, fuelShare, priceByYear, comparison, offers, avgPriceByBrand] = await Promise.all([
    getJson('/reports/exchange-rates?codes=EUR,USD,GBP,CHF,CZK,NOK,SEK'),
    getJson('/reports/kpi'),
    getJson('/reports/top-brands'),
    getJson('/reports/fuel-share'),
    getJson('/reports/price-by-year'),
    getJson('/reports/offers-vs-registrations'),
    getJson('/offers?limit=500'),
    getJson('/reports/avg-price-by-brand'),
  ]);

  state.rates = { ...(fx.rates || {}), PLN: 1 };
  state.rateSource = safe(fx.source) || 'unknown';
  rebuildCurrencySelect();
  const currency = getSelectedCurrency();
  const avgPriceConverted = convertFromPln(kpi.avg_price, currency);
  const topBrandOffers = Number((topBrands[0] && topBrands[0].offers_count) || 0);
  const topBrandSharePct = kpi.total_offers ? (100 * topBrandOffers / kpi.total_offers) : 0;
  const regsPer1000 = kpi.total_offers ? (1000 * kpi.total_registrations / kpi.total_offers) : 0;
  const nbpCurrenciesCount = Object.keys(state.rates || {}).filter((code) => code !== 'PLN').length;

  document.getElementById('kpiOffers').textContent = fmtNum(kpi.total_offers);
  document.getElementById('kpiRegs').textContent = fmtNum(kpi.total_registrations);
  document.getElementById('kpiRatio').textContent = kpi.offers_to_registrations_ratio;
  document.getElementById('kpiPrice').textContent = formatMoneyByCurrency(avgPriceConverted, currency);
  document.getElementById('kpiPriceLabel').textContent = `Średnia cena (${currency})`;
  document.getElementById('kpiMileage').textContent = fmtNum(kpi.avg_mileage);
  document.getElementById('kpiBrand').textContent = kpi.top_brand;
  document.getElementById('kpiTopFuel').textContent = kpi.top_fuel;
  document.getElementById('kpiTopBrandShare').textContent = `${topBrandSharePct.toFixed(2)}%`;
  document.getElementById('kpiRegsPer1000').textContent = regsPer1000.toFixed(2);
  document.getElementById('kpiNbpCurrencies').textContent = fmtNum(nbpCurrenciesCount);

  bar('topBrands', topBrands.map((x) => x.brand), topBrands.map((x) => x.offers_count), PALETTE.blue);
  doughnut('fuelShare', fuelShare.slice(0, 6).map((x) => x.fuel_type), fuelShare.slice(0, 6).map((x) => x.share_pct));
  line(
    'priceByYear',
    priceByYear.map((x) => x.year),
    priceByYear.map((x) => convertFromPln(x.avg_price, currency)),
    PALETTE.green,
  );
  horizontalBar(
    'avgPriceByBrand',
    avgPriceByBrand.slice(0, 10).map((x) => x.brand),
    avgPriceByBrand.slice(0, 10).map((x) => convertFromPln(x.avg_price, currency)),
    PALETTE.amber,
  );
  groupedBar(
    'offersVsRegs',
    comparison.map((x) => x.brand),
    comparison.map((x) => x.offers_count),
    comparison.map((x) => x.registrations_count),
  );
  bar(
    'regsPer1000',
    comparison.map((x) => x.brand),
    comparison.map((x) => x.registrations_per_1000_offers),
    PALETTE.red,
  );
  doughnut(
    'regsShareByBrand',
    comparison.map((x) => x.brand),
    comparison.map((x) => x.registrations_share_pct),
  );

  state.offers = offers;
  buildFilters();
  state.filtered = [...offers];
  renderFiltered();

  renderFxBadge();
  document.getElementById('syncBadge').textContent = 'Aktualizacja: ' + new Date().toLocaleString('pl-PL');
}

async function init() {
  document.getElementById('refreshBtn').addEventListener('click', () => {
    loadData().catch((e) => alert('Błąd odświeżania: ' + e.message));
  });
  document.getElementById('currencySelect').addEventListener('change', (event) => {
    state.currency = event.target.value;
    loadData().catch((e) => alert('Błąd przeliczenia walut: ' + e.message));
  });
  ['brandFilter', 'fuelFilter', 'cityFilter', 'modelFilter'].forEach((id) => {
    document.getElementById(id).addEventListener('input', applyFilters);
    document.getElementById(id).addEventListener('change', applyFilters);
  });
  await loadData();
}

init().catch((e) => {
  document.body.innerHTML = '<pre style="padding:20px;color:#b00020">Błąd dashboardu: ' + e.message + '</pre>';
});
</script>
</body>
</html>
"""
