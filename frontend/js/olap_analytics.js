/**
 * SafeTour OLAP Multi-Dimensional Analytics & 3D Cube Controller
 * Handles Roll-Up, Drill-Down, Slice, Dice, and Pivot operations on SQLite telemetry.
 */

const OlapAnalytics = (() => {
  let isCubeSpinning = true;
  let currentCubeRotX = -24;
  let currentCubeRotY = 32;

  // DOM Elements
  const modal = () => document.getElementById('olapAnalysisModal');
  const cubeElem = () => document.getElementById('olap3dCube');
  const sliceLaser = () => document.getElementById('olapSliceLaser');

  function init() {
    bindEvents();
    initCubeDrag();
  }

  function bindEvents() {
    const navBtn = document.getElementById('btnNavAnalysis');
    const mobileBtn = document.getElementById('mobileBtnAnalysis');
    const moreBtn = document.getElementById('openAnalysisModalBtn');
    const closeBtn = document.getElementById('closeOlapModalBtn');
    const modalOverlay = modal();

    if (navBtn) navBtn.addEventListener('click', openModal);
    if (mobileBtn) mobileBtn.addEventListener('click', () => {
      // Close mobile drawer if open
      const drawer = document.getElementById('mobileDrawer');
      if (drawer) drawer.classList.remove('open');
      openModal();
    });
    if (moreBtn) moreBtn.addEventListener('click', openModal);
    if (closeBtn) closeBtn.addEventListener('click', closeModal);

    if (modalOverlay) {
      modalOverlay.addEventListener('click', (e) => {
        if (e.target === modalOverlay) closeModal();
      });
    }

    const opSelect = document.getElementById('olapOperationSelect');
    if (opSelect) {
      opSelect.addEventListener('change', onOperationChange);
    }

    const btnExec = document.getElementById('btnExecuteOlap');
    if (btnExec) {
      btnExec.addEventListener('click', executeOlapQuery);
    }

    const spinToggle = document.getElementById('toggleCubeSpinBtn');
    if (spinToggle) {
      spinToggle.addEventListener('click', toggleCubeSpin);
    }
  }

  function openModal() {
    const m = modal();
    if (!m) return;
    m.classList.add('active');
    document.body.style.overflow = 'hidden';
    onOperationChange();
    executeOlapQuery();
  }

  function closeModal() {
    const m = modal();
    if (!m) return;
    m.classList.remove('active');
    document.body.style.overflow = '';
  }

  function toggleCubeSpin() {
    isCubeSpinning = !isCubeSpinning;
    const c = cubeElem();
    const btn = document.getElementById('toggleCubeSpinBtn');
    if (c) {
      if (isCubeSpinning) {
        c.classList.add('animate-spin');
        if (btn) btn.innerHTML = '<i class="fa-solid fa-pause"></i> Pause 3D Spin';
      } else {
        c.classList.remove('animate-spin');
        c.style.transform = `rotateX(${currentCubeRotX}deg) rotateY(${currentCubeRotY}deg)`;
        if (btn) btn.innerHTML = '<i class="fa-solid fa-play"></i> Auto Rotate';
      }
    }
  }

  function initCubeDrag() {
    const stage = document.getElementById('olapCubeStage');
    const cube = cubeElem();
    if (!stage || !cube) return;

    let isDragging = false;
    let startX = 0;
    let startY = 0;

    stage.addEventListener('mousedown', (e) => {
      isDragging = true;
      startX = e.clientX;
      startY = e.clientY;
      cube.classList.remove('animate-spin');
      isCubeSpinning = false;
      const btn = document.getElementById('toggleCubeSpinBtn');
      if (btn) btn.innerHTML = '<i class="fa-solid fa-play"></i> Auto Rotate';
    });

    window.addEventListener('mousemove', (e) => {
      if (!isDragging) return;
      const deltaX = e.clientX - startX;
      const deltaY = e.clientY - startY;
      currentCubeRotY += deltaX * 0.6;
      currentCubeRotX -= deltaY * 0.6;
      cube.style.transform = `rotateX(${currentCubeRotX}deg) rotateY(${currentCubeRotY}deg)`;
      startX = e.clientX;
      startY = e.clientY;
    });

    window.addEventListener('mouseup', () => {
      isDragging = false;
    });
  }

  function onOperationChange() {
    const op = document.getElementById('olapOperationSelect').value;
    const filterContainer = document.getElementById('olapDynamicFilters');
    const banner = document.getElementById('olapOperationBannerText');
    const laser = sliceLaser();

    if (laser) laser.classList.remove('show');

    let html = '';
    if (op === 'cube') {
      banner.innerHTML = '<strong>OLAP Multi-Dimensional Cube:</strong> Viewing full 3D aggregate across Region × Category × Risk Tier with combined capacity & risk telemetry.';
    } else if (op === 'rollup') {
      banner.innerHTML = '<strong>Roll-Up (Aggregate Up):</strong> Summarizing granular spot telemetry into macro dimensions to evaluate high-level traffic and safety patterns.';
      html = `
        <div class="olap-control-group">
          <label><i class="fa-solid fa-layer-group"></i> Roll-Up Dimension</label>
          <select id="olapRollUpDim" class="olap-select">
            <option value="region">Region (North, South, East, West)</option>
            <option value="category">Category (Heritage, Mountain, Beach...)</option>
            <option value="risk_tier">Risk Tier (Low, Moderate, High)</option>
          </select>
        </div>
      `;
    } else if (op === 'drilldown') {
      banner.innerHTML = '<strong>Drill-Down (Decomposition):</strong> Navigating from regional aggregates down into specific categories to identify localized safety and crowd hotspots.';
      html = `
        <div class="olap-control-group">
          <label><i class="fa-solid fa-map-location-dot"></i> Parent Region</label>
          <select id="olapDrillParent" class="olap-select">
            <option value="North India">North India</option>
            <option value="South India">South India</option>
            <option value="West India">West India</option>
            <option value="East & North-East India">East & North-East India</option>
          </select>
        </div>
        <div class="olap-control-group">
          <label><i class="fa-solid fa-arrow-down-wide-short"></i> Drill into Child</label>
          <select id="olapDrillChild" class="olap-select">
            <option value="category">Category (Forts, Mountains, Spiritual...)</option>
            <option value="risk_tier">Risk Tier</option>
          </select>
        </div>
      `;
    } else if (op === 'slice') {
      banner.innerHTML = '<strong>Slice (2D Cut):</strong> Fixing one single dimension to extract a 2D cross-section of data across the remaining two dimensions.';
      html = `
        <div class="olap-control-group">
          <label><i class="fa-solid fa-scissors"></i> Slice Dimension</label>
          <select id="olapSliceDim" class="olap-select" onchange="OlapAnalytics.onSliceDimChange()">
            <option value="region">Region</option>
            <option value="category">Category</option>
            <option value="risk_tier">Risk Tier</option>
          </select>
        </div>
        <div class="olap-control-group">
          <label><i class="fa-solid fa-filter"></i> Slice Value</label>
          <select id="olapSliceVal" class="olap-select">
            <option value="North India">North India</option>
            <option value="South India">South India</option>
            <option value="West India">West India</option>
            <option value="East & North-East India">East & North-East India</option>
          </select>
        </div>
      `;
    } else if (op === 'dice') {
      banner.innerHTML = '<strong>Dice (Sub-Cube Selection):</strong> Filtering multiple dimensions simultaneously to isolate a specific analytical domain.';
      html = `
        <div class="olap-control-group">
          <label><i class="fa-solid fa-map"></i> Region Filter</label>
          <select id="olapDiceRegion" class="olap-select">
            <option value="North India">North India</option>
            <option value="South India">South India</option>
            <option value="West India">West India</option>
            <option value="East & North-East India">East & North-East India</option>
          </select>
        </div>
        <div class="olap-control-group">
          <label><i class="fa-solid fa-tag"></i> Category Filter</label>
          <select id="olapDiceCategory" class="olap-select">
            <option value="Heritage & Forts">Heritage & Forts</option>
            <option value="Mountain & Adventure">Mountain & Adventure</option>
            <option value="Beach & Coastal">Beach & Coastal</option>
            <option value="Spiritual & Sacred">Spiritual & Sacred</option>
            <option value="Wildlife & Nature">Wildlife & Nature</option>
          </select>
        </div>
      `;
    } else if (op === 'pivot') {
      banner.innerHTML = '<strong>Pivot (Cross-Tabulation):</strong> Rotating dimensions across Rows and Columns to cross-analyze metrics in a 2D matrix.';
      html = `
        <div class="olap-control-group">
          <label><i class="fa-solid fa-arrows-split-up-and-left"></i> Measure (Metric)</label>
          <select id="olapPivotMeasure" class="olap-select">
            <option value="avg_safety_score">Average Safety Score (0-100)</option>
            <option value="total_capacity">Total Footfall Capacity</option>
            <option value="avg_crowd_density">Average Crowd Density (%)</option>
            <option value="avg_crime_index">Average Crime Index</option>
            <option value="avg_scam_index">Average Scam Index</option>
          </select>
        </div>
      `;
    }

    filterContainer.innerHTML = html;
  }

  function onSliceDimChange() {
    const dim = document.getElementById('olapSliceDim').value;
    const valSelect = document.getElementById('olapSliceVal');
    if (!valSelect) return;

    if (dim === 'region') {
      valSelect.innerHTML = `
        <option value="North India">North India</option>
        <option value="South India">South India</option>
        <option value="West India">West India</option>
        <option value="East & North-East India">East & North-East India</option>
      `;
    } else if (dim === 'category') {
      valSelect.innerHTML = `
        <option value="Heritage & Forts">Heritage & Forts</option>
        <option value="Mountain & Adventure">Mountain & Adventure</option>
        <option value="Beach & Coastal">Beach & Coastal</option>
        <option value="Spiritual & Sacred">Spiritual & Sacred</option>
        <option value="Wildlife & Nature">Wildlife & Nature</option>
        <option value="Urban & Culture">Urban & Culture</option>
      `;
    } else if (dim === 'risk_tier') {
      valSelect.innerHTML = `
        <option value="Low Risk (Safe)">Low Risk (Safe)</option>
        <option value="Moderate Risk">Moderate Risk</option>
        <option value="High Risk">High Risk</option>
      `;
    }
  }

  async function executeOlapQuery() {
    const op = document.getElementById('olapOperationSelect').value;
    const tableHost = document.getElementById('olapTableHost');
    const laser = sliceLaser();

    tableHost.innerHTML = '<div style="padding:40px;text-align:center;color:#94a3b8;"><i class="fa-solid fa-spinner fa-spin fa-2x"></i><p style="margin-top:10px;">Computing OLAP Multi-Dimensional Aggregation...</p></div>';

    const apiBase = (window.location.port === '8000' || window.location.port === '') ? '' : 'http://127.0.0.1:8000';
    let url = `${apiBase}/api/analytics/olap/cube`;

    if (op === 'rollup') {
      const dim = document.getElementById('olapRollUpDim')?.value || 'region';
      url = `${apiBase}/api/analytics/olap/roll-up?dimension=${encodeURIComponent(dim)}`;
    } else if (op === 'drilldown') {
      const parentVal = document.getElementById('olapDrillParent')?.value || 'North India';
      const childDim = document.getElementById('olapDrillChild')?.value || 'category';
      url = `${apiBase}/api/analytics/olap/drill-down?parent_dim=region&parent_value=${encodeURIComponent(parentVal)}&child_dim=${encodeURIComponent(childDim)}`;
    } else if (op === 'slice') {
      const dim = document.getElementById('olapSliceDim')?.value || 'region';
      const val = document.getElementById('olapSliceVal')?.value || 'North India';
      url = `${apiBase}/api/analytics/olap/slice?dimension=${encodeURIComponent(dim)}&value=${encodeURIComponent(val)}`;
      if (laser) laser.classList.add('show');
    } else if (op === 'dice') {
      const reg = document.getElementById('olapDiceRegion')?.value || 'North India';
      const cat = document.getElementById('olapDiceCategory')?.value || 'Heritage & Forts';
      url = `${apiBase}/api/analytics/olap/dice?region=${encodeURIComponent(reg)}&category=${encodeURIComponent(cat)}`;
    } else if (op === 'pivot') {
      const measure = document.getElementById('olapPivotMeasure')?.value || 'avg_safety_score';
      url = `${apiBase}/api/analytics/olap/pivot?row_dim=region&col_dim=category&measure=${encodeURIComponent(measure)}`;
    }

    try {
      const res = await fetch(url);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      renderOlapData(op, data);
    } catch (err) {
      tableHost.innerHTML = `<div style="padding:30px;color:#f87171;text-align:center;"><i class="fa-solid fa-triangle-exclamation"></i> Error loading OLAP analytics: ${err.message}</div>`;
    }
  }

  function renderOlapData(op, data) {
    // Update KPI Cards
    const totals = data.totals || {};
    document.getElementById('olapKpiUsers').textContent = (totals.total_registered_users ?? '—') + ' Users';
    document.getElementById('olapKpiTraffic').textContent = (totals.total_capacity ? totals.total_capacity.toLocaleString() : '—') + ' Capacity';
    document.getElementById('olapKpiSafety').textContent = (totals.avg_safety_score ? totals.avg_safety_score + '/100' : '—');
    document.getElementById('olapKpiDests').textContent = (totals.destination_count ?? '—') + ' Spots';

    const tableHost = document.getElementById('olapTableHost');

    if (op === 'pivot') {
      renderPivotTable(data, tableHost);
      return;
    }

    const cells = data.cells || [];
    const dims = data.dimensions || ['region', 'category', 'risk_tier'];

    if (!cells.length) {
      tableHost.innerHTML = '<div style="padding:30px;color:#94a3b8;text-align:center;">No matching data found for this OLAP slice.</div>';
      return;
    }

    let thead = '<tr>';
    dims.forEach(d => {
      thead += `<th>${formatDimName(d)}</th>`;
    });
    thead += `
      <th>Destinations</th>
      <th>Total Capacity</th>
      <th>Avg Safety</th>
      <th>Crime Index</th>
      <th>Scam Index</th>
      <th>Weather Risk</th>
      <th>Night Safety</th>
      <th>Crowd Density</th>
    </tr>`;

    let tbody = '';
    cells.forEach(row => {
      tbody += '<tr>';
      dims.forEach(d => {
        tbody += `<td><strong>${row[d] || '—'}</strong></td>`;
      });
      const score = row.avg_safety_score || 0;
      let scoreBadge = 'high';
      if (score < 60) scoreBadge = 'low';
      else if (score < 75) scoreBadge = 'mid';

      tbody += `
        <td><span class="olap-tag-pill">${row.destination_count || 1}</span></td>
        <td>${(row.total_capacity || 0).toLocaleString()}</td>
        <td><span class="score-badge ${scoreBadge}">${score} / 100</span></td>
        <td>${row.avg_crime_index ?? '—'}</td>
        <td>${row.avg_scam_index ?? '—'}</td>
        <td>${row.avg_weather_risk ?? '—'}</td>
        <td>${row.avg_night_safety ?? '—'}</td>
        <td>${row.avg_crowd_density ?? '—'}%</td>
      </tr>`;
    });

    tableHost.innerHTML = `
      <div class="olap-table-wrap">
        <table class="olap-table">
          <thead>${thead}</thead>
          <tbody>${tbody}</tbody>
        </table>
      </div>
    `;
  }

  function renderPivotTable(data, host) {
    const rows = data.rows || [];
    const cols = data.columns || [];
    const matrix = data.matrix || {};
    const measureName = formatMeasureName(data.measure);

    let thead = `<tr><th>${formatDimName(data.row_dimension)} \\ ${formatDimName(data.col_dimension)}</th>`;
    cols.forEach(c => {
      thead += `<th>${c}</th>`;
    });
    thead += '</tr>';

    let tbody = '';
    rows.forEach(r => {
      tbody += `<tr><td><strong>${r}</strong></td>`;
      cols.forEach(c => {
        const val = matrix[r] ? matrix[r][c] : null;
        if (val !== null && val !== undefined) {
          let badgeClass = 'mid';
          if (data.measure === 'avg_safety_score') {
            badgeClass = val >= 75 ? 'high' : (val >= 60 ? 'mid' : 'low');
          }
          tbody += `<td><span class="score-badge ${badgeClass}">${val}</span></td>`;
        } else {
          tbody += '<td style="color:#64748b;">—</td>';
        }
      });
      tbody += '</tr>';
    });

    host.innerHTML = `
      <div style="font-size:0.78rem;color:#38bdf8;margin-bottom:6px;">
        <i class="fa-solid fa-chart-simple"></i> Matrix Cross-Tabulation Metric: <strong>${measureName}</strong>
      </div>
      <div class="olap-table-wrap">
        <table class="olap-table">
          <thead>${thead}</thead>
          <tbody>${tbody}</tbody>
        </table>
      </div>
    `;
  }

  function formatDimName(d) {
    if (d === 'region') return 'Region';
    if (d === 'category') return 'Category';
    if (d === 'risk_tier') return 'Risk Tier';
    return d;
  }

  function formatMeasureName(m) {
    if (m === 'avg_safety_score') return 'Average Safety Score';
    if (m === 'total_capacity') return 'Total Footfall Capacity';
    if (m === 'avg_crowd_density') return 'Average Crowd Density (%)';
    if (m === 'avg_crime_index') return 'Average Crime Index';
    if (m === 'avg_scam_index') return 'Average Scam Index';
    return m;
  }

  return {
    init,
    openModal,
    closeModal,
    onSliceDimChange,
    executeOlapQuery
  };
})();

// Auto-init when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  OlapAnalytics.init();
});
