/**
 * MudFlow OS - Hydraulics & Pressure Profile Engine
 */

let pressureChart = null;
let hydDebounceTimer = null;
let currentNozzles = [14, 14, 14];

function initHydraulicsModule() {
    initPressureChart();
    attachHydraulicsInputListeners();
    renderNozzlesList();
    calculateHydraulics();
}

function initPressureChart() {
    const ctx = document.getElementById('hydraulicsChartCanvas');
    if (!ctx) return;

    pressureChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [
                {
                    label: 'Dynamic Circulating Pressure (ECD)',
                    data: [],
                    borderColor: '#06B6D4',
                    backgroundColor: 'rgba(6, 182, 212, 0.15)',
                    borderWidth: 2.5,
                    fill: false,
                    tension: 0.1,
                    pointRadius: 3
                },
                {
                    label: 'Static Hydrostatic Pressure',
                    data: [],
                    borderColor: '#3B82F6',
                    borderWidth: 2,
                    borderDash: [5, 4],
                    fill: false,
                    pointRadius: 0
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            indexAxis: 'y', // Inverted: Depth on Y axis, Pressure on X axis!
            plugins: {
                legend: {
                    position: 'top',
                    labels: {
                        color: '#CBD5E1',
                        font: { family: 'Plus Jakarta Sans', size: 11, weight: '600' }
                    }
                },
                tooltip: {
                    backgroundColor: '#0F172A',
                    titleColor: '#38BDF8',
                    bodyColor: '#F8FAFC',
                    borderColor: '#334155',
                    borderWidth: 1,
                    padding: 10
                }
            },
            scales: {
                y: {
                    reverse: true, // 0 ft at the top, TD at bottom!
                    title: {
                        display: true,
                        text: 'True Vertical Depth (ft)',
                        color: '#94A3B8',
                        font: { family: 'Plus Jakarta Sans', size: 12, weight: 'bold' }
                    },
                    grid: { color: '#1E293B' },
                    ticks: { color: '#94A3B8', font: { family: 'JetBrains Mono', size: 10 } }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Wellbore Pressure (psi)',
                        color: '#94A3B8',
                        font: { family: 'Plus Jakarta Sans', size: 12, weight: 'bold' }
                    },
                    grid: { color: '#1E293B' },
                    ticks: { color: '#94A3B8', font: { family: 'JetBrains Mono', size: 10 } }
                }
            }
        }
    });

    window.pressureChart = pressureChart;
}

function attachHydraulicsInputListeners() {
    const inputs = [
        'hydMudWeight', 'hydTvd', 'hydMd', 'hydFlowRate',
        'hydHoleId', 'hydDpOd', 'hydDcOd', 'hydAnnularLoss', 'hydPumpPress'
    ];

    inputs.forEach(id => {
        const el = document.getElementById(id);
        if (el) {
            el.addEventListener('input', () => {
                clearTimeout(hydDebounceTimer);
                hydDebounceTimer = setTimeout(calculateHydraulics, 200);
            });
        }
    });

    // Preset Nozzle buttons
    const btn3x12 = document.getElementById('btnNozzle3x12');
    const btn3x14 = document.getElementById('btnNozzle3x14');
    const btn4x14 = document.getElementById('btnNozzle4x14');
    const btnAddNozzle = document.getElementById('btnAddNozzle');

    if (btn3x12) btn3x12.addEventListener('click', () => setNozzles([12, 12, 12]));
    if (btn3x14) btn3x14.addEventListener('click', () => setNozzles([14, 14, 14]));
    if (btn4x14) btn4x14.addEventListener('click', () => setNozzles([14, 14, 14, 14]));

    if (btnAddNozzle) {
        btnAddNozzle.addEventListener('click', () => {
            currentNozzles.push(14);
            renderNozzlesList();
            calculateHydraulics();
        });
    }
}

function setNozzles(list) {
    currentNozzles = [...list];
    renderNozzlesList();
    calculateHydraulics();
}

function renderNozzlesList() {
    const container = document.getElementById('nozzlesListContainer');
    if (!container) return;

    container.innerHTML = currentNozzles.map((nz, idx) => `
        <div class="inline-flex items-center gap-1 bg-slate-800 border border-slate-700 px-2 py-1 rounded text-xs">
            <span class="text-slate-400">#${idx + 1}:</span>
            <input type="number" min="8" max="32" value="${nz}" class="w-12 bg-slate-900 border border-slate-600 rounded px-1 py-0.5 text-center text-amber-300 font-mono text-xs focus:outline-none focus:border-sky-500"
                onchange="updateNozzle(${idx}, this.value)">
            <span class="text-slate-400 text-[10px]">/32"</span>
            ${currentNozzles.length > 1 ? `
                <button type="button" onclick="removeNozzle(${idx})" class="text-rose-400 hover:text-rose-300 px-1 font-bold">×</button>
            ` : ''}
        </div>
    `).join('');
}

window.updateNozzle = function(index, value) {
    currentNozzles[index] = Math.max(6, Math.min(32, parseFloat(value) || 14));
    calculateHydraulics();
};

window.removeNozzle = function(index) {
    if (currentNozzles.length > 1) {
        currentNozzles.splice(index, 1);
        renderNozzlesList();
        calculateHydraulics();
    }
};

async function calculateHydraulics() {
    const lossInput = document.getElementById('hydAnnularLoss').value;
    const payload = {
        mud_weight: parseFloat(document.getElementById('hydMudWeight').value) || 12.5,
        tvd: parseFloat(document.getElementById('hydTvd').value) || 10000,
        md: parseFloat(document.getElementById('hydMd').value) || 11500,
        flow_rate: parseFloat(document.getElementById('hydFlowRate').value) || 500,
        hole_id: parseFloat(document.getElementById('hydHoleId').value) || 8.5,
        drill_pipe_od: parseFloat(document.getElementById('hydDpOd').value) || 5.0,
        drill_collar_od: parseFloat(document.getElementById('hydDcOd').value) || 6.5,
        nozzles: currentNozzles,
        annular_pressure_loss: lossInput ? parseFloat(lossInput) : null,
        pump_pressure: parseFloat(document.getElementById('hydPumpPress').value) || 3200
    };

    try {
        const res = await fetch('/api/hydraulics/pressure-profile', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (!res.ok) throw new Error('Hydraulics calculation failed');
        const data = await res.json();
        const summary = data.summary;

        // Save live engine data
        AppState.liveEngineData.hydraulics = { input: payload, output: summary };

        // Update UI Outputs
        updateHydraulicsUI(summary);

        // Update Chart
        updatePressureChart(data.profile);

    } catch (err) {
        console.error('Hydraulics solver failed:', err);
    }
}

function updateHydraulicsUI(data) {
    const set = (id, val) => {
        const el = document.getElementById(id);
        if (el) el.textContent = val;
    };

    set('resHydrostatic', `${data.hydrostatic_pressure.toLocaleString()} psi`);
    set('resAnnularLoss', `${data.annular_pressure_loss.toFixed(1)} psi`);
    set('resEcd', `${data.ecd.toFixed(2)} ppg`);
    set('resAnnVelDp', `${data.annular_velocity_dp.toFixed(1)} ft/min`);
    set('resAnnVelDc', `${data.annular_velocity_dc.toFixed(1)} ft/min`);
    set('resTfa', `${data.tfa.toFixed(3)} in²`);
    set('resBitVelocity', `${data.bit_velocity.toFixed(1)} ft/sec`);
    set('resBitDrop', `${data.bit_pressure_drop.toFixed(1)} psi`);
    set('resHhp', `${data.hhp.toFixed(1)} HP`);
    set('resHsi', `${data.hsi.toFixed(2)} hp/in²`);
    set('resImpactForce', `${data.impact_force.toFixed(1)} lbf`);
    set('resReynolds', `${data.reynolds_number.toLocaleString()}`);
    set('resBitPercent', `${data.percent_pressure_at_bit.toFixed(1)}% of Pump`);
    set('resHoleCleaning', data.hole_cleaning_status);

    // Flow regime badge
    const regimeBadge = document.getElementById('resFlowRegimeBadge');
    if (regimeBadge) {
        if (data.flow_regime.includes('Laminar')) {
            regimeBadge.className = 'telemetry-badge badge-laminar';
        } else if (data.flow_regime.includes('Transitional')) {
            regimeBadge.className = 'telemetry-badge badge-warning';
        } else {
            regimeBadge.className = 'telemetry-badge badge-turbulent';
        }
        regimeBadge.textContent = data.flow_regime;
    }
}

function updatePressureChart(profile) {
    if (!pressureChart || !profile) return;

    const labels = profile.map(p => `${p.depth_tvd} ft`);
    const ecdCircPressure = profile.map(p => p.total_circulating_pressure);
    const hydroPressure = profile.map(p => p.hydrostatic_pressure);

    pressureChart.data.labels = labels;
    pressureChart.data.datasets[0].data = ecdCircPressure;
    pressureChart.data.datasets[1].data = hydroPressure;

    pressureChart.update('none');
}

window.initHydraulicsModule = initHydraulicsModule;
window.calculateHydraulics = calculateHydraulics;
