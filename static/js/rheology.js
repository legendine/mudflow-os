/**
 * MudFlow OS - Viscometer & Rheology Engine
 */

let rheoChart = null;
let rheoDebounceTimer = null;

function initRheologyModule() {
    initRheologyChart();
    attachRheologyInputListeners();
    // Run initial calculation
    calculateRheology();
}

function initRheologyChart() {
    const ctx = document.getElementById('rheologyChartCanvas');
    if (!ctx) return;

    rheoChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [
                {
                    label: 'Measured Points (Fann 35)',
                    data: [],
                    borderColor: '#F59E0B',
                    backgroundColor: '#F59E0B',
                    pointRadius: 6,
                    pointHoverRadius: 8,
                    showLine: false,
                    order: 1
                },
                {
                    label: 'Herschel-Bulkley (API 13D YPL)',
                    data: [],
                    borderColor: '#06B6D4',
                    backgroundColor: 'rgba(6, 182, 212, 0.1)',
                    borderWidth: 2.5,
                    tension: 0.3,
                    pointRadius: 0,
                    order: 2
                },
                {
                    label: 'Bingham Plastic Model',
                    data: [],
                    borderColor: '#10B981',
                    borderWidth: 2,
                    borderDash: [5, 5],
                    pointRadius: 0,
                    order: 3
                },
                {
                    label: 'Power Law Model',
                    data: [],
                    borderColor: '#A855F7',
                    borderWidth: 1.8,
                    borderDash: [2, 3],
                    pointRadius: 0,
                    order: 4
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false,
            },
            plugins: {
                legend: {
                    position: 'top',
                    labels: {
                        color: '#CBD5E1',
                        font: { family: 'Plus Jakarta Sans', size: 11, weight: '600' },
                        usePointStyle: true,
                        boxWidth: 8
                    }
                },
                tooltip: {
                    backgroundColor: '#0F172A',
                    titleColor: '#38BDF8',
                    bodyColor: '#F8FAFC',
                    borderColor: '#334155',
                    borderWidth: 1,
                    padding: 10,
                    callbacks: {
                        title: (items) => `Shear Rate: ${items[0].label} sec⁻¹`,
                        label: (ctx) => `${ctx.dataset.label}: ${ctx.raw ? ctx.raw.toFixed(1) : '-'} lb/100ft²`
                    }
                }
            },
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Shear Rate γ (sec⁻¹)',
                        color: '#94A3B8',
                        font: { family: 'Plus Jakarta Sans', size: 12, weight: 'bold' }
                    },
                    grid: { color: '#1E293B' },
                    ticks: { color: '#94A3B8', font: { family: 'JetBrains Mono', size: 10 } }
                },
                y: {
                    title: {
                        display: true,
                        text: 'Shear Stress τ (lb / 100 ft²)',
                        color: '#94A3B8',
                        font: { family: 'Plus Jakarta Sans', size: 12, weight: 'bold' }
                    },
                    grid: { color: '#1E293B' },
                    ticks: { color: '#94A3B8', font: { family: 'JetBrains Mono', size: 10 } },
                    min: 0
                }
            }
        }
    });

    window.rheoChart = rheoChart;
}

function attachRheologyInputListeners() {
    const inputs = [
        'rheoR600', 'rheoR300', 'rheoR200', 'rheoR100', 'rheoR6', 'rheoR3',
        'rheoGel10s', 'rheoGel10m', 'rheoGel30m', 'rheoMudWeight'
    ];

    inputs.forEach(id => {
        const el = document.getElementById(id);
        if (el) {
            el.addEventListener('input', () => {
                clearTimeout(rheoDebounceTimer);
                rheoDebounceTimer = setTimeout(calculateRheology, 200);
            });
        }
    });

    // Preset buttons
    const btnObm = document.getElementById('btnPresetObm');
    const btnWbm = document.getElementById('btnPresetWbm');
    const btnHpht = document.getElementById('btnPresetHpht');

    if (btnObm) {
        btnObm.addEventListener('click', () => loadRheologyPreset({
            r600: 68, r300: 42, r200: 32, r100: 20, r6: 7, r3: 5,
            g10s: 7, g10m: 12, g30m: 15, mw: 12.8
        }));
    }
    if (btnWbm) {
        btnWbm.addEventListener('click', () => loadRheologyPreset({
            r600: 55, r300: 35, r200: 26, r100: 17, r6: 5, r3: 4,
            g10s: 5, g10m: 9, g30m: 11, mw: 10.5
        }));
    }
    if (btnHpht) {
        btnHpht.addEventListener('click', () => loadRheologyPreset({
            r600: 82, r300: 51, r200: 39, r100: 25, r6: 9, r3: 7,
            g10s: 9, g10m: 16, g30m: 22, mw: 15.2
        }));
    }
}

function loadRheologyPreset(data) {
    document.getElementById('rheoR600').value = data.r600;
    document.getElementById('rheoR300').value = data.r300;
    document.getElementById('rheoR200').value = data.r200;
    document.getElementById('rheoR100').value = data.r100;
    document.getElementById('rheoR6').value = data.r6;
    document.getElementById('rheoR3').value = data.r3;
    document.getElementById('rheoGel10s').value = data.g10s;
    document.getElementById('rheoGel10m').value = data.g10m;
    document.getElementById('rheoGel30m').value = data.g30m;
    document.getElementById('rheoMudWeight').value = data.mw;

    calculateRheology();
    window.showToast('Loaded standard rheology baseline preset', 'info');
}

async function calculateRheology() {
    const payload = {
        rpm_600: parseFloat(document.getElementById('rheoR600').value) || 0,
        rpm_300: parseFloat(document.getElementById('rheoR300').value) || 0,
        rpm_200: parseFloat(document.getElementById('rheoR200').value) || 0,
        rpm_100: parseFloat(document.getElementById('rheoR100').value) || 0,
        rpm_6: parseFloat(document.getElementById('rheoR6').value) || 0,
        rpm_3: parseFloat(document.getElementById('rheoR3').value) || 0,
        gel_10s: parseFloat(document.getElementById('rheoGel10s').value) || 0,
        gel_10m: parseFloat(document.getElementById('rheoGel10m').value) || 0,
        gel_30m: parseFloat(document.getElementById('rheoGel30m').value) || 0,
        mud_weight: parseFloat(document.getElementById('rheoMudWeight').value) || 12.0
    };

    try {
        const res = await fetch('/api/rheology/calculate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (!res.ok) throw new Error('Rheology calculation error');
        const data = await res.json();

        // Save live state
        AppState.liveEngineData.rheology = { input: payload, output: data };

        // Update UI Outputs
        updateRheologyUI(data);

        // Update Chart
        updateRheologyChart(data.curve_data);

    } catch (err) {
        console.error('Rheology solver failed:', err);
    }
}

function updateRheologyUI(data) {
    const set = (id, val) => {
        const el = document.getElementById(id);
        if (el) el.textContent = val;
    };

    set('resPv', `${data.pv.toFixed(1)} cP`);
    set('resYp', `${data.yp.toFixed(1)} lb/100ft²`);
    set('resAv', `${data.av.toFixed(1)} cP`);
    set('resYpPv', data.yp_pv_ratio.toFixed(2));
    set('resNIndex', data.n_index.toFixed(4));
    set('resKIndex', data.k_index.toFixed(4));
    set('resTau0', `${data.tau_0_hb.toFixed(2)} lb/100ft²`);
    set('resNHb', data.n_hb.toFixed(4));
    set('resKHb', data.k_hb.toFixed(4));

    // Gel strengths
    set('resGel10s', `${data.gel_10s.toFixed(1)}`);
    set('resGel10m', `${data.gel_10m.toFixed(1)}`);
    set('resGel30m', `${data.gel_30m.toFixed(1)}`);
    set('resGelType', data.gel_structure_type);

    // R2 Indicators
    set('resR2Hb', `R² = ${data.r2_hb.toFixed(3)}`);
    set('resR2Bp', `R² = ${data.r2_bingham.toFixed(3)}`);
    set('resR2Pl', `R² = ${data.r2_powerlaw.toFixed(3)}`);

    // Gel profile styling badge
    const gelBadge = document.getElementById('resGelTypeBadge');
    if (gelBadge) {
        if (data.gel_structure_type.includes('Progressive')) {
            gelBadge.className = 'telemetry-badge badge-warning';
        } else if (data.gel_structure_type.includes('Flat')) {
            gelBadge.className = 'telemetry-badge badge-laminar';
        } else {
            gelBadge.className = 'telemetry-badge badge-cyan';
        }
        gelBadge.textContent = data.gel_structure_type;
    }
}

function updateRheologyChart(curveData) {
    if (!rheoChart || !curveData) return;

    const labels = curveData.map(pt => pt.shear_rate.toString());
    const measuredData = curveData.map(pt => pt.measured_stress >= 0 ? pt.measured_stress : null);
    const hbData = curveData.map(pt => pt.herschel_bulkley_stress);
    const bpData = curveData.map(pt => pt.bingham_stress);
    const plData = curveData.map(pt => pt.powerlaw_stress);

    rheoChart.data.labels = labels;
    rheoChart.data.datasets[0].data = measuredData;
    rheoChart.data.datasets[1].data = hbData;
    rheoChart.data.datasets[2].data = bpData;
    rheoChart.data.datasets[3].data = plData;

    rheoChart.update('none');
}

window.initRheologyModule = initRheologyModule;
window.calculateRheology = calculateRheology;
