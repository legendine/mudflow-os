/**
 * MudFlow OS - Global App Controller
 */

const AppState = {
    activeTab: 'dashboard',
    activeWellId: 1,
    wells: [],
    reports: [],
    liveEngineData: {
        rheology: null,
        hydraulics: null,
        volumetrics: null,
        solids: null
    }
};

document.addEventListener('DOMContentLoaded', async () => {
    initNavigation();
    await loadWells();
    
    // Initialize child modules
    if (window.initRheologyModule) window.initRheologyModule();
    if (window.initHydraulicsModule) window.initHydraulicsModule();
    if (window.initVolumetricsModule) window.initVolumetricsModule();
    if (window.initSolidsModule) window.initSolidsModule();
    if (window.initReportsModule) window.initReportsModule();

    // Initial Dashboard refresh
    refreshDashboardTelemetry();
});

function initNavigation() {
    const navButtons = document.querySelectorAll('.nav-tab-btn');
    navButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const tabId = btn.getAttribute('data-tab');
            switchTab(tabId);
        });
    });
}

function switchTab(tabId) {
    AppState.activeTab = tabId;

    // Update buttons
    document.querySelectorAll('.nav-tab-btn').forEach(btn => {
        if (btn.getAttribute('data-tab') === tabId) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });

    // Update tab sections
    document.querySelectorAll('.tab-content-panel').forEach(panel => {
        if (panel.id === `tab-${tabId}`) {
            panel.classList.remove('hidden');
        } else {
            panel.classList.add('hidden');
        }
    });

    // Trigger chart resizes if switching to Rheology or Hydraulics
    if (tabId === 'rheology' && window.rheoChart) {
        setTimeout(() => window.rheoChart.resize(), 100);
    }
    if (tabId === 'hydraulics' && window.pressureChart) {
        setTimeout(() => window.pressureChart.resize(), 100);
    }
    if (tabId === 'solids' && window.solidsChart) {
        setTimeout(() => window.solidsChart.resize(), 100);
    }
    if (tabId === 'dashboard') {
        refreshDashboardTelemetry();
    }
}

async function loadWells() {
    try {
        const res = await fetch('/api/wells');
        if (!res.ok) throw new Error('Failed to fetch wells');
        const wells = await res.json();
        AppState.wells = wells;

        const wellSelect = document.getElementById('globalWellSelect');
        const reportWellSelect = document.getElementById('reportWellSelect');
        const modalWellSelect = document.getElementById('modalWellSelect');

        if (wellSelect) {
            wellSelect.innerHTML = wells.map(w => `<option value="${w.id}">${w.well_name} (${w.rig_name})</option>`).join('');
            wellSelect.value = AppState.activeWellId;
            wellSelect.addEventListener('change', (e) => {
                AppState.activeWellId = parseInt(e.target.value);
                onWellChanged();
            });
        }
        if (reportWellSelect) {
            reportWellSelect.innerHTML = wells.map(w => `<option value="${w.id}">${w.well_name}</option>`).join('');
            reportWellSelect.value = AppState.activeWellId;
            reportWellSelect.addEventListener('change', (e) => {
                AppState.activeWellId = parseInt(e.target.value);
                if (wellSelect) wellSelect.value = AppState.activeWellId;
                onWellChanged();
            });
        }
        if (modalWellSelect) {
            modalWellSelect.innerHTML = wells.map(w => `<option value="${w.id}">${w.well_name} - ${w.rig_name}</option>`).join('');
        }

        updateWellHeaderUI();
    } catch (err) {
        console.error('Error loading wells:', err);
        showToast('Error connecting to backend database', 'error');
    }
}

function onWellChanged() {
    updateWellHeaderUI();
    if (window.loadReportsForActiveWell) {
        window.loadReportsForActiveWell();
    }
    refreshDashboardTelemetry();
    showToast(`Switched active well context to ID #${AppState.activeWellId}`, 'info');
}

function updateWellHeaderUI() {
    const currentWell = AppState.wells.find(w => w.id === AppState.activeWellId) || AppState.wells[0];
    if (!currentWell) return;

    const nameEl = document.getElementById('hdrWellName');
    const rigEl = document.getElementById('hdrRigName');
    const opEl = document.getElementById('hdrOperator');
    const statusEl = document.getElementById('hdrWellStatus');

    if (nameEl) nameEl.textContent = currentWell.well_name;
    if (rigEl) rigEl.textContent = `${currentWell.rig_name} • ${currentWell.field_name}, ${currentWell.country}`;
    if (opEl) opEl.textContent = currentWell.operator;
    if (statusEl) statusEl.textContent = currentWell.status;
}

function refreshDashboardTelemetry() {
    // Populate dashboard with the latest active report for this well
    fetch(`/api/reports?well_id=${AppState.activeWellId}`)
        .then(r => r.json())
        .then(reports => {
            if (reports && reports.length > 0) {
                const latest = reports[0];
                const setVal = (id, val) => {
                    const el = document.getElementById(id);
                    if (el) el.textContent = val;
                };

                setVal('dashDepthMd', `${latest.depth_md.toLocaleString()} ft`);
                setVal('dashDepthTvd', `${latest.depth_tvd.toLocaleString()} ft`);
                setVal('dashMudWeight', `${latest.mud_weight.toFixed(2)} ppg`);
                setVal('dashEcd', `${latest.ecd.toFixed(2)} ppg`);
                setVal('dashPv', `${latest.pv.toFixed(0)} cP`);
                setVal('dashYp', `${latest.yp.toFixed(0)} lb/100ft²`);
                setVal('dashPumpPress', `${latest.pump_pressure.toFixed(0)} psi`);
                setVal('dashFlowRate', `${latest.flow_rate.toFixed(0)} GPM`);
                setVal('dashBitHhp', `${latest.hhp.toFixed(0)} HP`);
                setVal('dashHsi', `${latest.hsi.toFixed(2)} HSI`);
                setVal('dashAnnVel', `${latest.annular_velocity_dp.toFixed(0)} ft/min`);
                setVal('dashLgs', `${latest.lgs_pct.toFixed(2)}%`);
                setVal('dashHgs', `${latest.hgs_pct.toFixed(2)}%`);
                setVal('dashActiveVol', `${latest.active_volume.toLocaleString()} bbl`);
                setVal('dashTotalVol', `${latest.total_volume.toLocaleString()} bbl`);
                setVal('dashRegime', latest.flow_regime);
                setVal('dashOp', latest.current_operation);
                setVal('dashReportNo', `#${latest.report_no} (${latest.report_date})`);
            }
        })
        .catch(e => console.warn('Could not load dashboard telemetry:', e));
}

function showToast(message, type = 'info') {
    const toastContainer = document.getElementById('toastContainer');
    if (!toastContainer) return;

    const toast = document.createElement('div');
    const colorClass = type === 'error' ? 'border-rose-500 text-rose-300 bg-rose-950/80' :
                       type === 'success' ? 'border-emerald-500 text-emerald-300 bg-emerald-950/80' :
                       'border-sky-500 text-sky-300 bg-sky-950/80';

    toast.className = `border px-4 py-3 rounded-lg shadow-xl text-sm flex items-center gap-3 transition-all duration-300 transform translate-y-2 opacity-0 ${colorClass}`;
    toast.innerHTML = `
        <span class="font-bold">${type.toUpperCase()}:</span>
        <span>${message}</span>
    `;

    toastContainer.appendChild(toast);

    setTimeout(() => {
        toast.classList.remove('translate-y-2', 'opacity-0');
    }, 10);

    setTimeout(() => {
        toast.classList.add('opacity-0', 'translate-y-2');
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

// ==========================================
// AI MUD DOCTOR CONTROLLER
// ==========================================

async function askAiMudDoctor() {
    // Collect live values for PV, YP, MW, LGS%
    let pv = 0, yp = 0, mw = 0, lgs_pct = 0;

    // 1. Mud Weight
    const mwEl = document.getElementById('rheoMudWeight') || document.getElementById('retMw') || document.getElementById('hydMudWeight');
    if (mwEl && mwEl.value) {
        mw = parseFloat(mwEl.value);
    }
    if (!mw && AppState.liveEngineData.rheology?.input?.mud_weight) {
        mw = AppState.liveEngineData.rheology.input.mud_weight;
    }
    if (!mw) mw = 12.8;

    // 2. PV and YP
    if (AppState.liveEngineData.rheology?.output) {
        pv = AppState.liveEngineData.rheology.output.pv;
        yp = AppState.liveEngineData.rheology.output.yp;
    } else {
        const r600 = parseFloat(document.getElementById('rheoR600')?.value) || 68;
        const r300 = parseFloat(document.getElementById('rheoR300')?.value) || 42;
        pv = r600 - r300;
        yp = r300 - pv;
    }

    // 3. LGS%
    if (AppState.liveEngineData.solids?.output) {
        lgs_pct = AppState.liveEngineData.solids.output.lgs_pct;
    } else {
        const lgsEl = document.getElementById('resRetLgsPct');
        if (lgsEl && lgsEl.textContent) {
            lgs_pct = parseFloat(lgsEl.textContent) || 4.2;
        } else {
            lgs_pct = 4.2;
        }
    }

    // Open drawer in analyzing state
    openAiMudDoctorDrawer();
    const statusBadge = document.getElementById('aiDoctorUrgencyBadge');
    const summaryNote = document.getElementById('aiDoctorSummaryNote');
    const recsList = document.getElementById('aiDoctorRecsList');
    const recsCount = document.getElementById('aiDoctorRecsCount');

    if (statusBadge) {
        statusBadge.textContent = 'ANALYZING...';
        statusBadge.className = 'px-2.5 py-0.5 rounded-full text-xs font-bold tracking-wider font-mono bg-purple-500/20 text-purple-300 border border-purple-500/40 animate-pulse';
    }
    if (summaryNote) summaryNote.textContent = 'Contacting AI Mud Doctor Diagnostic Engine...';
    if (recsList) recsList.innerHTML = '<div class="text-xs text-slate-400 p-4 text-center">Consulting API RP 13D / 13C expert guidelines...</div>';

    // Populate Snapshot Chips
    const setChip = (id, val) => {
        const el = document.getElementById(id);
        if (el) el.textContent = val;
    };
    setChip('aiDoctorMw', `${mw.toFixed(2)} ppg`);
    setChip('aiDoctorPv', `${pv.toFixed(1)} cP`);
    setChip('aiDoctorYp', `${yp.toFixed(1)} lb/100ft²`);
    setChip('aiDoctorYpPv', (pv > 0 ? (yp / pv).toFixed(2) : '0.00'));
    setChip('aiDoctorLgs', `${lgs_pct.toFixed(2)} % vol`);

    try {
        const res = await fetch('/api/ai-mud-doctor', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ pv, yp, mw, lgs_pct })
        });
        if (!res.ok) throw new Error('AI Mud Doctor API returned status ' + res.status);
        const data = await res.json();

        // Update Urgency Badge
        const u = data.urgency ? data.urgency.toUpperCase() : 'OPTIMAL';
        if (statusBadge) {
            statusBadge.classList.remove('animate-pulse');
            if (u === 'CRITICAL') {
                statusBadge.className = 'px-2.5 py-0.5 rounded-full text-xs font-bold tracking-wider font-mono bg-rose-500/20 text-rose-300 border border-rose-500/40';
                statusBadge.textContent = 'CRITICAL ATTENTION';
            } else if (u === 'WARNING') {
                statusBadge.className = 'px-2.5 py-0.5 rounded-full text-xs font-bold tracking-wider font-mono bg-amber-500/20 text-amber-300 border border-amber-500/40';
                statusBadge.textContent = 'WARNING';
            } else {
                statusBadge.className = 'px-2.5 py-0.5 rounded-full text-xs font-bold tracking-wider font-mono bg-emerald-500/20 text-emerald-300 border border-emerald-500/40';
                statusBadge.textContent = 'OPTIMAL ENVELOPE';
            }
        }

        // Summary Note
        if (summaryNote) {
            summaryNote.textContent = data.summary_note;
        }

        // Recommendations List
        if (recsList) {
            if (data.recommendations && data.recommendations.length > 0) {
                if (recsCount) recsCount.textContent = `${data.recommendations.length} action items`;
                recsList.innerHTML = data.recommendations.map((rec, idx) => {
                    let borderClass = 'border-slate-800 bg-rig-950/70 text-slate-200';
                    if (rec.includes('CRITICAL') || rec.includes('SEVERE')) {
                        borderClass = 'border-rose-500/40 bg-rose-950/20 text-rose-100';
                    } else if (rec.includes('ELEVATED') || rec.includes('HIGH') || rec.includes('ALERT') || rec.includes('POOR') || rec.includes('PROGRESSIVE')) {
                        borderClass = 'border-amber-500/40 bg-amber-950/20 text-amber-100';
                    } else if (rec.includes('NORMAL') || rec.includes('OPTIMAL')) {
                        borderClass = 'border-emerald-500/40 bg-emerald-950/20 text-emerald-100';
                    }

                    return `
                        <div class="p-3 rounded-lg border ${borderClass} text-xs font-sans space-y-1">
                            <div class="flex items-start gap-2">
                                <span class="font-mono text-[10px] font-bold text-slate-400 mt-0.5">#${idx + 1}</span>
                                <p class="leading-relaxed">${rec}</p>
                            </div>
                        </div>
                    `;
                }).join('');
            } else {
                recsList.innerHTML = '<div class="text-xs text-slate-400">No specific warnings. System operating within normal window.</div>';
            }
        }

        showToast(`AI Mud Doctor: Diagnostic Complete (${u})`, u === 'CRITICAL' ? 'error' : (u === 'WARNING' ? 'info' : 'success'));

    } catch (err) {
        console.error('AI Mud Doctor failed:', err);
        if (summaryNote) summaryNote.textContent = 'Failed to analyze mud properties: ' + err.message;
        showToast('AI Mud Doctor connection error', 'error');
    }
}

function openAiMudDoctorDrawer() {
    const drawer = document.getElementById('aiMudDoctorDrawer');
    if (drawer) drawer.classList.remove('hidden');
}

function closeAiMudDoctor() {
    const drawer = document.getElementById('aiMudDoctorDrawer');
    if (drawer) drawer.classList.add('hidden');
}

// ==========================================
// WELL CONTROL / KILL SHEET CONTROLLER
// ==========================================

function openKillSheetModal() {
    prefillKillSheetFromWell();
    const modal = document.getElementById('killSheetModal');
    if (modal) modal.classList.remove('hidden');
}

function closeKillSheetModal() {
    const modal = document.getElementById('killSheetModal');
    if (modal) modal.classList.add('hidden');
}

function prefillKillSheetFromWell() {
    // Current MW
    const mwEl = document.getElementById('rheoMudWeight') || document.getElementById('hydMudWeight');
    if (mwEl && mwEl.value) {
        const ksMw = document.getElementById('ksCurrentMw');
        if (ksMw) ksMw.value = mwEl.value;
    }
    // TVD
    const tvdEl = document.getElementById('hydTvd');
    if (tvdEl && tvdEl.value) {
        const ksTvd = document.getElementById('ksTvd');
        if (ksTvd) ksTvd.value = tvdEl.value;
    }
}

async function calculateKillSheet() {
    const current_mw = parseFloat(document.getElementById('ksCurrentMw')?.value) || 0;
    const tvd = parseFloat(document.getElementById('ksTvd')?.value) || 0;
    const sidpp = parseFloat(document.getElementById('ksSidpp')?.value) || 0;
    const sicp = parseFloat(document.getElementById('ksSicp')?.value) || 0;
    const slow_pump_press = parseFloat(document.getElementById('ksSlowPumpPress')?.value) || 0;

    if (current_mw <= 0 || tvd <= 0) {
        showToast('Please enter valid positive values for Mud Weight and TVD', 'error');
        return;
    }

    try {
        const res = await fetch('/api/well-control/kill-sheet', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ current_mw, tvd, sidpp, sicp, slow_pump_press })
        });
        if (!res.ok) {
            const errJson = await res.json().catch(() => ({}));
            throw new Error(errJson.detail || 'Kill Sheet calculation failed');
        }
        const data = await res.json();

        // Update High-Visibility Alert Cards
        const kwmEl = document.getElementById('ksResKwm');
        const icpEl = document.getElementById('ksResIcp');
        const fcpEl = document.getElementById('ksResFcp');
        const kickIntensityEl = document.getElementById('ksResKickIntensity');
        const initialBhpEl = document.getElementById('ksResInitialBhp');
        const stepDownEl = document.getElementById('ksResStepDown');

        if (kwmEl) kwmEl.innerHTML = `${data.kill_mud_weight.toFixed(2)} <span class="text-lg font-bold text-slate-300">ppg</span>`;
        if (icpEl) icpEl.innerHTML = `${Math.round(data.initial_circulating_pressure).toLocaleString()} <span class="text-lg font-bold text-slate-300">psi</span>`;
        if (fcpEl) fcpEl.innerHTML = `${Math.round(data.final_circulating_pressure).toLocaleString()} <span class="text-lg font-bold text-slate-300">psi</span>`;

        if (kickIntensityEl) kickIntensityEl.textContent = `+${data.kick_intensity_ppg.toFixed(2)} ppg`;
        if (initialBhpEl) initialBhpEl.textContent = `${Math.round(data.initial_bhp_psi).toLocaleString()} psi`;
        if (stepDownEl) stepDownEl.textContent = `Δ ${Math.round(data.initial_circulating_pressure - data.final_circulating_pressure).toLocaleString()} psi`;

        // Render Field Instructions
        const listEl = document.getElementById('ksInstructionsList');
        if (listEl && data.instructions) {
            listEl.innerHTML = data.instructions.map((inst, i) => `
                <div class="p-2.5 rounded bg-rig-900 border border-slate-800 text-slate-300 flex items-start gap-2.5">
                    <span class="w-5 h-5 rounded-full bg-amber-500/20 text-amber-400 border border-amber-500/30 flex items-center justify-center font-bold text-[10px] flex-shrink-0 mt-0.5">${i + 1}</span>
                    <span class="leading-relaxed font-sans">${inst}</span>
                </div>
            `).join('');
        }

        showToast(`Kill Sheet Calculated: KWM = ${data.kill_mud_weight.toFixed(2)} ppg`, 'success');

    } catch (err) {
        console.error('Error calculating kill sheet:', err);
        showToast(err.message, 'error');
    }
}

window.AppState = AppState;
window.switchTab = switchTab;
window.showToast = showToast;
window.askAiMudDoctor = askAiMudDoctor;
window.openAiMudDoctorDrawer = openAiMudDoctorDrawer;
window.closeAiMudDoctor = closeAiMudDoctor;
window.openKillSheetModal = openKillSheetModal;
window.closeKillSheetModal = closeKillSheetModal;
window.calculateKillSheet = calculateKillSheet;
window.prefillKillSheetFromWell = prefillKillSheetFromWell;
