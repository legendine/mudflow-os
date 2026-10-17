/**
 * MudFlow OS - Retort & Solids Control Analysis
 */

let solidsChart = null;
let solidsDebounceTimer = null;

function initSolidsModule() {
    initSolidsChart();
    attachSolidsInputListeners();
    analyzeSolids();
}

function initSolidsChart() {
    const ctx = document.getElementById('solidsChartCanvas');
    if (!ctx) return;

    solidsChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Base Oil', 'Water Phase', 'High Gravity Solids (HGS)', 'Low Gravity Solids (LGS)'],
            datasets: [{
                data: [65, 15, 15, 5],
                backgroundColor: [
                    '#38BDF8', // Oil (cyan)
                    '#3B82F6', // Water (blue)
                    '#F59E0B', // HGS (amber)
                    '#F43F5E'  // LGS (rose/red)
                ],
                borderWidth: 1,
                borderColor: '#111827'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '68%',
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: '#CBD5E1',
                        font: { family: 'Plus Jakarta Sans', size: 10, weight: '600' },
                        boxWidth: 10
                    }
                },
                tooltip: {
                    backgroundColor: '#0F172A',
                    titleColor: '#38BDF8',
                    bodyColor: '#F8FAFC',
                    borderColor: '#334155',
                    borderWidth: 1,
                    padding: 8,
                    callbacks: {
                        label: (ctx) => `${ctx.label}: ${ctx.raw.toFixed(1)} % vol`
                    }
                }
            }
        }
    });

    window.solidsChart = solidsChart;
}

function attachSolidsInputListeners() {
    const inputs = ['retWater', 'retOil', 'retSolids', 'retMw', 'retMbt', 'retChlorides', 'retOilSg'];
    inputs.forEach(id => {
        const el = document.getElementById(id);
        if (el) {
            el.addEventListener('input', () => {
                clearTimeout(solidsDebounceTimer);
                solidsDebounceTimer = setTimeout(analyzeSolids, 200);
            });
        }
    });

    // Auto balance solids when water or oil changes
    const wEl = document.getElementById('retWater');
    const oEl = document.getElementById('retOil');
    const sEl = document.getElementById('retSolids');

    const autoBalance = () => {
        const w = parseFloat(wEl.value) || 0;
        const o = parseFloat(oEl.value) || 0;
        const s = Math.max(0, 100 - (w + o));
        sEl.value = s.toFixed(1);
    };

    if (wEl) wEl.addEventListener('change', autoBalance);
    if (oEl) oEl.addEventListener('change', autoBalance);
}

async function analyzeSolids() {
    const payload = {
        water_pct: parseFloat(document.getElementById('retWater').value) || 14.0,
        oil_pct: parseFloat(document.getElementById('retOil').value) || 66.0,
        solids_pct: parseFloat(document.getElementById('retSolids').value) || 20.0,
        mud_weight: parseFloat(document.getElementById('retMw').value) || 12.6,
        mbt_ppb: parseFloat(document.getElementById('retMbt').value) || 12.0,
        chlorides_mg_l: parseFloat(document.getElementById('retChlorides').value) || 18000.0,
        oil_sg: parseFloat(document.getElementById('retOilSg').value) || 0.84
    };

    try {
        const res = await fetch('/api/solids/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        if (!res.ok) throw new Error('Solids analysis failed');
        const data = await res.json();

        // Save live state
        AppState.liveEngineData.solids = { input: payload, output: data };

        updateSolidsUI(data);
        updateSolidsChart(data);

    } catch (err) {
        console.error('Solids analysis error:', err);
    }
}

function updateSolidsUI(data) {
    const set = (id, val) => {
        const el = document.getElementById(id);
        if (el) el.textContent = val;
    };

    set('resRetAsg', data.asg.toFixed(2));
    set('resRetHgsPct', `${data.hgs_pct.toFixed(2)} %`);
    set('resRetLgsPct', `${data.lgs_pct.toFixed(2)} %`);
    set('resRetHgsPpb', `${data.hgs_ppb.toFixed(1)} ppb`);
    set('resRetLgsPpb', `${data.lgs_ppb.toFixed(1)} ppb`);
    set('resRetActiveClay', `${data.active_clay_pct.toFixed(2)} % (${data.active_clay_ppb.toFixed(1)} ppb)`);
    set('resRetInactiveSolids', `${data.inactive_drill_solids_pct.toFixed(2)} %`);
    set('resRetClayRatio', `${(data.active_clay_ratio * 100).toFixed(1)}%`);
    set('resRetOwr', data.oil_water_ratio);
    set('resRetEfficiency', data.solids_control_efficiency);
    set('resRetRecommendation', data.lgs_recommendation);

    // LGS Badge styling
    const lgsBadge = document.getElementById('resRetLgsBadge');
    if (lgsBadge) {
        if (data.excess_lgs) {
            lgsBadge.className = 'telemetry-badge badge-turbulent';
            lgsBadge.textContent = 'EXCESS LGS (>5.5%)';
        } else {
            lgsBadge.className = 'telemetry-badge badge-laminar';
            lgsBadge.textContent = 'OPTIMAL LGS (<5.5%)';
        }
    }
}

function updateSolidsChart(data) {
    if (!solidsChart) return;

    solidsChart.data.datasets[0].data = [
        data.oil_pct,
        data.water_pct,
        data.hgs_pct,
        data.lgs_pct
    ];

    solidsChart.update('none');
}

window.initSolidsModule = initSolidsModule;
window.analyzeSolids = analyzeSolids;
