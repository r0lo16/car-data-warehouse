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
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Car DW Dashboard</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <style>
    :root {
      --bg: #eef3f8;
      --panel: #ffffff;
      --ink: #10243e;
      --muted: #516179;
      --accent: #0b84f3;
      --accent-2: #1bb987;
      --border: #dbe3ec;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: "Segoe UI", "Inter", sans-serif;
      background: radial-gradient(circle at top right, #e2f4ff 0, var(--bg) 50%);
      color: var(--ink);
    }
    .wrap {
      max-width: 1180px;
      margin: 0 auto;
      padding: 24px 18px 36px;
    }
    .head { margin-bottom: 16px; }
    .head h1 { margin: 0 0 6px; font-size: 28px; }
    .head p { margin: 0; color: var(--muted); }
    .grid-kpi {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 12px;
      margin-bottom: 14px;
    }
    .kpi {
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: 14px;
      padding: 14px;
      box-shadow: 0 10px 30px rgba(16, 36, 62, 0.06);
    }
    .kpi .label { color: var(--muted); font-size: 12px; }
    .kpi .value { font-size: 26px; font-weight: 700; margin-top: 6px; }
    .grid-charts {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 12px;
    }
    .card {
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: 14px;
      padding: 14px;
      min-height: 310px;
      box-shadow: 0 10px 30px rgba(16, 36, 62, 0.06);
    }
    .card h3 { margin: 0 0 10px; font-size: 16px; }
    .card canvas {
      width: 100% !important;
      height: 260px !important;
      max-height: 260px !important;
      display: block;
    }
    @media (max-width: 920px) {
      .grid-charts { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body>
  <div class="wrap">
    <div class="head">
      <h1>Used Cars - Wroclaw Data Warehouse</h1>
      <p>Live stats from FastAPI endpoints and PostgreSQL warehouse.</p>
    </div>

    <section class="grid-kpi">
      <article class="kpi"><div class="label">Total offers</div><div id="kpi-total" class="value">-</div></article>
      <article class="kpi"><div class="label">Average price (PLN)</div><div id="kpi-price" class="value">-</div></article>
      <article class="kpi"><div class="label">Average mileage</div><div id="kpi-mileage" class="value">-</div></article>
      <article class="kpi"><div class="label">Top brand</div><div id="kpi-brand" class="value">-</div></article>
      <article class="kpi"><div class="label">Top fuel</div><div id="kpi-fuel" class="value">-</div></article>
    </section>

    <section class="grid-charts">
      <article class="card">
        <h3>Top Brands (offers count)</h3>
        <canvas id="topBrands"></canvas>
      </article>
      <article class="card">
        <h3>Fuel Share (%)</h3>
        <canvas id="fuelShare"></canvas>
      </article>
      <article class="card">
        <h3>Avg Price by Year (PLN)</h3>
        <canvas id="priceByYear"></canvas>
      </article>
      <article class="card">
        <h3>Avg Price by Brand (Top 15)</h3>
        <canvas id="priceByBrand"></canvas>
      </article>
    </section>
  </div>

<script>
const money = (v) => new Intl.NumberFormat('pl-PL', { maximumFractionDigits: 0 }).format(v);
const num = (v) => new Intl.NumberFormat('pl-PL', { maximumFractionDigits: 0 }).format(v);

async function getJson(path) {
  const r = await fetch(path);
  if (!r.ok) throw new Error(`${path}: ${r.status}`);
  return r.json();
}

function barChart(id, labels, values, color) {
  return new Chart(document.getElementById(id), {
    type: 'bar',
    data: { labels, datasets: [{ data: values, backgroundColor: color, borderRadius: 8 }] },
    options: { responsive: true, maintainAspectRatio: true, aspectRatio: 2.4, plugins: { legend: { display: false } } }
  });
}

function lineChart(id, labels, values, color) {
  return new Chart(document.getElementById(id), {
    type: 'line',
    data: { labels, datasets: [{ data: values, borderColor: color, backgroundColor: color + '33', fill: true, tension: 0.25 }] },
    options: { responsive: true, maintainAspectRatio: true, aspectRatio: 2.4, plugins: { legend: { display: false } } }
  });
}

function doughnutChart(id, labels, values) {
  return new Chart(document.getElementById(id), {
    type: 'doughnut',
    data: {
      labels,
      datasets: [{ data: values, backgroundColor: ['#0b84f3','#1bb987','#ff9f43','#ed6a5e','#9b59b6','#607d8b'] }]
    },
    options: { responsive: true, maintainAspectRatio: true, aspectRatio: 2.4, plugins: { legend: { position: 'bottom' } } }
  });
}

async function init() {
  const [kpi, topBrands, fuelShare, priceByYear, priceByBrand] = await Promise.all([
    getJson('/reports/kpi'),
    getJson('/reports/top-brands'),
    getJson('/reports/fuel-share'),
    getJson('/reports/price-by-year'),
    getJson('/reports/avg-price-by-brand')
  ]);

  document.getElementById('kpi-total').textContent = num(kpi.total_offers);
  document.getElementById('kpi-price').textContent = money(kpi.avg_price);
  document.getElementById('kpi-mileage').textContent = num(kpi.avg_mileage);
  document.getElementById('kpi-brand').textContent = kpi.top_brand;
  document.getElementById('kpi-fuel').textContent = kpi.top_fuel;

  barChart('topBrands', topBrands.map(x => x.brand), topBrands.map(x => x.offers_count), '#0b84f3');
  doughnutChart('fuelShare', fuelShare.slice(0, 6).map(x => x.fuel_type), fuelShare.slice(0, 6).map(x => x.share_pct));
  lineChart('priceByYear', priceByYear.map(x => x.year), priceByYear.map(x => x.avg_price), '#1bb987');
  barChart('priceByBrand', priceByBrand.slice(0, 15).map(x => x.brand), priceByBrand.slice(0, 15).map(x => x.avg_price), '#ff9f43');
}

init().catch((err) => {
  document.body.innerHTML = `<pre style="padding:20px;color:#b00020">Dashboard load error: ${err.message}</pre>`;
});
</script>
</body>
</html>
"""
