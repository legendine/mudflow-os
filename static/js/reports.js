/**
 * MudFlow OS - Daily Mud Reports Manager & PDF Export
 */

function initReportsModule() {
    loadReportsForActiveWell();
    attachReportModalListeners();
}

async function loadReportsForActiveWell() {
    const tableBody = document.getElementById('reportsTableBody');
    if (!tableBody) return;

    tableBody.innerHTML = `<tr><td colspan="9" class="text-center py-6 text-slate-500">Loading historical reports...</td></tr>`;

    try {
        const res = await fetch(`/api/reports?well_id=${AppState.activeWellId}`);
        if (!res.ok) throw new Error('Failed to load reports');
        const reports = await res.json();
        AppState.reports = reports;

        if (reports.length === 0) {
            tableBody.innerHTML = `<tr><td colspan="9" class="text-center py-6 text-slate-500">No daily reports recorded yet for this well.</td></tr>`;
            return;
        }

        tableBody.innerHTML = reports.map(r => `
            <tr class="border-b border-slate-800 hover:bg-slate-800/40 transition">
                <td class="py-3 px-4 font-mono font-bold text-sky-400">#${r.report_no}</td>
                <td class="py-3 px-4 text-slate-300 font-mono text-xs">${r.report_date}</td>
                <td class="py-3 px-4 text-slate-200 font-mono text-xs">${r.depth_md.toLocaleString()} / ${r.depth_tvd.toLocaleString()} ft</td>
                <td class="py-3 px-4 font-mono font-semibold text-amber-300">${r.mud_weight.toFixed(2)} ppg</td>
                <td class="py-3 px-4 font-mono text-xs text-slate-300">${r.pv.toFixed(0)} / ${r.yp.toFixed(0)}</td>
                <td class="py-3 px-4 font-mono font-bold text-emerald-400">${r.ecd.toFixed(2)} ppg</td>
                <td class="py-3 px-4 font-mono text-xs ${r.lgs_pct > 5.5 ? 'text-rose-400 font-bold' : 'text-slate-300'}">${r.lgs_pct.toFixed(1)}%</td>
                <td class="py-3 px-4 text-xs text-slate-400 truncate max-w-xs">${r.current_operation}</td>
                <td class="py-3 px-4 text-right">
                    <div class="inline-flex items-center gap-2">
                        <button onclick="viewReportDetails(${r.id})" class="text-xs bg-slate-800 hover:bg-slate-700 text-sky-400 px-2.5 py-1 rounded border border-slate-700 transition">
                            View
                        </button>
                        <a href="/api/reports/${r.id}/pdf" target="_blank" class="text-xs bg-sky-600 hover:bg-sky-500 text-white font-semibold px-2.5 py-1 rounded flex items-center gap-1 transition shadow-sm">
                            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>
                            PDF
                        </a>
                    </div>
                </td>
            </tr>
        `).join('');

    } catch (err) {
        console.error('Failed to load reports:', err);
        tableBody.innerHTML = `<tr><td colspan="9" class="text-center py-6 text-rose-400">Failed to load reports database.</td></tr>`;
    }
}

function attachReportModalListeners() {
    const btnNew = document.getElementById('btnOpenNewReportModal');
    const modal = document.getElementById('newReportModal');
    const btnClose = document.getElementById('btnCloseNewReportModal');
    const btnCancel = document.getElementById('btnCancelNewReportModal');
    const form = document.getElementById('newReportForm');
    const btnAutofill = document.getElementById('btnAutofillEngines');

    if (btnNew && modal) {
        btnNew.addEventListener('click', () => {
            // Set default date to today
            const today = new Date().toISOString().split('T')[0];
            document.getElementById('repDate').value = today;
            
            // Suggest next report number
            const nextNo = (AppState.reports.length > 0) ? Math.max(...AppState.reports.map(r => r.report_no)) + 1 : 1;
            document.getElementById('repNo').value = nextNo;
            
            modal.classList.remove('hidden');
        });
    }

    const closeModal = () => {
        if (modal) modal.classList.add('hidden');
    };

    if (btnClose) btnClose.addEventListener('click', closeModal);
    if (btnCancel) btnCancel.addEventListener('click', closeModal);

    // Autofill button: transfers current engine states into the form!
    if (btnAutofill) {
        btnAutofill.addEventListener('click', () => {
            const rheo = AppState.liveEngineData.rheology;
            const hyd = AppState.liveEngineData.hydraulics;
            const vol = AppState.liveEngineData.volumetrics;
            const sol = AppState.liveEngineData.solids;

            if (rheo) {
                document.getElementById('repMw').value = rheo.input.mud_weight;
                document.getElementById('repPv').value = rheo.output.pv;
                document.getElementById('repYp').value = rheo.output.yp;
                document.getElementById('repGel10s').value = rheo.output.gel_10s;
                document.getElementById('repGel10m').value = rheo.output.gel_10m;
                document.getElementById('repGel30m').value = rheo.output.gel_30m;
                document.getElementById('repR600').value = rheo.input.rpm_600;
                document.getElementById('repR300').value = rheo.input.rpm_300;
                document.getElementById('repR200').value = rheo.input.rpm_200;
                document.getElementById('repR100').value = rheo.input.rpm_100;
                document.getElementById('repR6').value = rheo.input.rpm_6;
                document.getElementById('repR3').value = rheo.input.rpm_3;
            }

            if (hyd) {
                document.getElementById('repDepthMd').value = hyd.input.md;
                document.getElementById('repDepthTvd').value = hyd.input.tvd;
                document.getElementById('repFlowRate').value = hyd.input.flow_rate;
                document.getElementById('repPumpPress').value = hyd.input.pump_pressure;
                document.getElementById('repEcd').value = hyd.output.ecd;
                document.getElementById('repHoleId').value = hyd.input.hole_id;
                document.getElementById('repDpOd').value = hyd.input.drill_pipe_od;
            }

            if (vol) {
                document.getElementById('repActiveVol').value = vol.output.active_surface_volume;
                document.getElementById('repReserveVol').value = vol.output.reserve_surface_volume;
                document.getElementById('repTotalVol').value = vol.output.total_system_volume;
                document.getElementById('repHoleVol').value = vol.output.total_hole_volume;
            }

            if (sol) {
                document.getElementById('repRetWater').value = sol.output.water_pct;
                document.getElementById('repRetOil').value = sol.output.oil_pct;
                document.getElementById('repRetSolids').value = sol.output.total_solids_pct;
                document.getElementById('repRetAsg').value = sol.output.asg;
                document.getElementById('repRetHgs').value = sol.output.hgs_pct;
                document.getElementById('repRetLgs').value = sol.output.lgs_pct;
                document.getElementById('repRetMbt').value = sol.output.active_clay_ppb;
            }

            window.showToast('Autofilled report fields from active calculation engines!', 'success');
        });
    }

    if (form) {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            await submitNewReport();
        });
    }
}

async function submitNewReport() {
    const r600 = parseFloat(document.getElementById('repR600').value) || 0;
    const r300 = parseFloat(document.getElementById('repR300').value) || 0;
    const pv = parseFloat(document.getElementById('repPv').value) || (r600 - r300);
    const yp = parseFloat(document.getElementById('repYp').value) || (r300 - pv);
    const mw = parseFloat(document.getElementById('repMw').value) || 12.5;
    const tvd = parseFloat(document.getElementById('repDepthTvd').value) || 10000;
    const md = parseFloat(document.getElementById('repDepthMd').value) || 11500;
    const ecd = parseFloat(document.getElementById('repEcd').value) || (mw + 0.3);

    const payload = {
        well_id: parseInt(document.getElementById('modalWellSelect').value) || AppState.activeWellId,
        report_no: parseInt(document.getElementById('repNo').value) || 1,
        report_date: document.getElementById('repDate').value || new Date().toISOString().split('T')[0],
        depth_md: md,
        depth_tvd: tvd,
        daily_footage: parseFloat(document.getElementById('repFootage').value) || 0,
        current_operation: document.getElementById('repOp').value || 'Drilling ahead',
        formation: document.getElementById('repFormation').value || 'Target Sandstone',
        mud_type: document.getElementById('repMudType').value || 'Synthetic OBM',
        mud_weight: mw,
        pv: pv,
        yp: yp,
        av: r600 / 2.0,
        yp_pv_ratio: pv > 0 ? (yp / pv) : 0,
        gel_10s: parseFloat(document.getElementById('repGel10s').value) || 0,
        gel_10m: parseFloat(document.getElementById('repGel10m').value) || 0,
        gel_30m: parseFloat(document.getElementById('repGel30m').value) || 0,
        rpm_600: r600,
        rpm_300: r300,
        rpm_200: parseFloat(document.getElementById('repR200').value) || 0,
        rpm_100: parseFloat(document.getElementById('repR100').value) || 0,
        rpm_6: parseFloat(document.getElementById('repR6').value) || 0,
        rpm_3: parseFloat(document.getElementById('repR3').value) || 0,
        flow_rate: parseFloat(document.getElementById('repFlowRate').value) || 500,
        pump_pressure: parseFloat(document.getElementById('repPumpPress').value) || 3200,
        annular_pressure_loss: (ecd - mw) * 0.052 * tvd,
        hydrostatic_pressure: 0.052 * mw * tvd,
        ecd: ecd,
        hole_id: parseFloat(document.getElementById('repHoleId').value) || 8.5,
        drill_pipe_od: parseFloat(document.getElementById('repDpOd').value) || 5.0,
        active_volume: parseFloat(document.getElementById('repActiveVol').value) || 650,
        reserve_volume: parseFloat(document.getElementById('repReserveVol').value) || 400,
        hole_volume: parseFloat(document.getElementById('repHoleVol').value) || 520,
        total_volume: parseFloat(document.getElementById('repTotalVol').value) || 1650,
        retort_water: parseFloat(document.getElementById('repRetWater').value) || 14.0,
        retort_oil: parseFloat(document.getElementById('repRetOil').value) || 66.0,
        retort_solids: parseFloat(document.getElementById('repRetSolids').value) || 20.0,
        asg: parseFloat(document.getElementById('repRetAsg').value) || 3.8,
        hgs_pct: parseFloat(document.getElementById('repRetHgs').value) || 15.5,
        lgs_pct: parseFloat(document.getElementById('repRetLgs').value) || 4.5,
        mbt: parseFloat(document.getElementById('repRetMbt').value) || 12.0,
        remarks: document.getElementById('repRemarks').value || 'Standard daily logging entry.',
        engineer_name: document.getElementById('repEngineer').value || 'Lead Drilling Fluids Engineer'
    };

    try {
        const res = await fetch('/api/reports', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (!res.ok) throw new Error('Failed to create report');
        const created = await res.json();

        window.showToast(`Report #${created.report_no} saved to database!`, 'success');
        document.getElementById('newReportModal').classList.add('hidden');
        await loadReportsForActiveWell();
        refreshDashboardTelemetry();

    } catch (err) {
        console.error('Failed to save report:', err);
        window.showToast('Error saving daily report to database', 'error');
    }
}

window.viewReportDetails = function(reportId) {
    const report = AppState.reports.find(r => r.id === reportId);
    if (!report) return;

    const modal = document.getElementById('viewReportModal');
    if (!modal) return;

    const set = (id, val) => {
        const el = document.getElementById(id);
        if (el) el.textContent = val;
    };

    set('vwReportTitle', `Daily Mud Report #${report.report_no} • ${report.report_date}`);
    set('vwDepth', `${report.depth_md.toLocaleString()} ft MD / ${report.depth_tvd.toLocaleString()} ft TVD`);
    set('vwMudWeight', `${report.mud_weight.toFixed(2)} ppg`);
    set('vwEcd', `${report.ecd.toFixed(2)} ppg`);
    set('vwPvYp', `PV: ${report.pv.toFixed(0)} cP | YP: ${report.yp.toFixed(0)} lb/100ft²`);
    set('vwGels', `Gels: ${report.gel_10s}/${report.gel_10m}/${report.gel_30m}`);
    set('vwFlowPump', `${report.flow_rate.toFixed(0)} GPM @ ${report.pump_pressure.toFixed(0)} psi`);
    set('vwRetort', `W: ${report.retort_water}% | O: ${report.retort_oil}% | S: ${report.retort_solids}%`);
    set('vwSolids', `HGS: ${report.hgs_pct.toFixed(1)}% | LGS: ${report.lgs_pct.toFixed(1)}% | ASG: ${report.asg.toFixed(2)}`);
    set('vwVolumes', `Active: ${report.active_volume.toLocaleString()} bbl | Total: ${report.total_volume.toLocaleString()} bbl`);
    set('vwRemarks', report.remarks || 'No specific remarks entered.');
    set('vwEngineer', report.engineer_name);

    const pdfBtn = document.getElementById('vwPdfDownloadBtn');
    if (pdfBtn) {
        pdfBtn.href = `/api/reports/${report.id}/pdf`;
    }

    modal.classList.remove('hidden');
};

window.closeViewModal = function() {
    const modal = document.getElementById('viewReportModal');
    if (modal) modal.classList.add('hidden');
};

window.initReportsModule = initReportsModule;
window.loadReportsForActiveWell = loadReportsForActiveWell;
