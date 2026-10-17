/**
 * MudFlow OS - Pit Volume & Weight Up / Dilution Manager
 */

function initVolumetricsModule() {
    attachVolumetricListeners();
    attachWeightUpListeners();
    attachDilutionListeners();
    calculateHoleVolumes();
    calculateWeightUp();
    calculateDilution();
}

function attachVolumetricListeners() {
    const inputs = [
        'volHoleId', 'volHoleLength', 'volDpOd', 'volDpId', 'volDpLength',
        'volDcOd', 'volDcId', 'volDcLength', 'volActivePits', 'volReservePits', 'volTripTank'
    ];
    inputs.forEach(id => {
        const el = document.getElementById(id);
        if (el) el.addEventListener('input', calculateHoleVolumes);
    });
}

function attachWeightUpListeners() {
    const inputs = ['wuInitialMw', 'wuTargetMw', 'wuVolume'];
    inputs.forEach(id => {
        const el = document.getElementById(id);
        if (el) el.addEventListener('input', calculateWeightUp);
    });

    const radios = document.querySelectorAll('input[name="wuAgent"]');
    radios.forEach(r => r.addEventListener('change', calculateWeightUp));
}

function attachDilutionListeners() {
    const inputs = ['dilInitialMw', 'dilTargetMw', 'dilVolume', 'dilCurrentLgs', 'dilTargetLgs'];
    inputs.forEach(id => {
        const el = document.getElementById(id);
        if (el) el.addEventListener('input', calculateDilution);
    });

    const baseFluid = document.getElementById('dilBaseFluid');
    if (baseFluid) baseFluid.addEventListener('change', calculateDilution);
}

async function calculateHoleVolumes() {
    const payload = {
        hole_id: parseFloat(document.getElementById('volHoleId').value) || 8.5,
        hole_length: parseFloat(document.getElementById('volHoleLength').value) || 11500,
        drill_pipe_od: parseFloat(document.getElementById('volDpOd').value) || 5.0,
        drill_pipe_id: parseFloat(document.getElementById('volDpId').value) || 4.276,
        drill_pipe_length: parseFloat(document.getElementById('volDpLength').value) || 10900,
        drill_collar_od: parseFloat(document.getElementById('volDcOd').value) || 6.5,
        drill_collar_id: parseFloat(document.getElementById('volDcId').value) || 2.813,
        drill_collar_length: parseFloat(document.getElementById('volDcLength').value) || 600,
        active_pits: parseFloat(document.getElementById('volActivePits').value) || 650,
        reserve_pits: parseFloat(document.getElementById('volReservePits').value) || 400,
        trip_tank: parseFloat(document.getElementById('volTripTank').value) || 45
    };

    try {
        const res = await fetch('/api/volumetrics/hole-volumes', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        if (!res.ok) throw new Error('Hole volume calculation failed');
        const data = await res.json();

        // Save live state
        AppState.liveEngineData.volumetrics = { input: payload, output: data };

        const set = (id, val) => {
            const el = document.getElementById(id);
            if (el) el.textContent = val;
        };

        set('resDpCap', `${data.drill_pipe_capacity.toLocaleString()} bbl`);
        set('resDcCap', `${data.drill_collar_capacity.toLocaleString()} bbl`);
        set('resTotalStringCap', `${data.total_string_capacity.toLocaleString()} bbl`);
        set('resDpAnnCap', `${data.annular_capacity_dp.toLocaleString()} bbl`);
        set('resDcAnnCap', `${data.annular_capacity_dc.toLocaleString()} bbl`);
        set('resTotalAnnVol', `${data.total_annular_volume.toLocaleString()} bbl`);
        set('resTotalHoleVol', `${data.total_hole_volume.toLocaleString()} bbl`);
        set('resActiveSurfaceVol', `${data.active_surface_volume.toLocaleString()} bbl`);
        set('resCirculatingVol', `${data.total_active_circulating_volume.toLocaleString()} bbl`);
        set('resTotalSystemVol', `${data.total_system_volume.toLocaleString()} bbl`);

    } catch (err) {
        console.error('Hole volume error:', err);
    }
}

async function calculateWeightUp() {
    const selectedAgentRadio = document.querySelector('input[name="wuAgent"]:checked');
    const agent = selectedAgentRadio ? selectedAgentRadio.value : 'barite';

    const payload = {
        initial_mud_weight: parseFloat(document.getElementById('wuInitialMw').value) || 12.0,
        target_mud_weight: parseFloat(document.getElementById('wuTargetMw').value) || 12.5,
        initial_volume: parseFloat(document.getElementById('wuVolume').value) || 500,
        weighting_agent: agent
    };

    try {
        const res = await fetch('/api/volumetrics/weight-up', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        if (!res.ok) throw new Error('Weight-up calculation failed');
        const data = await res.json();

        const set = (id, val) => {
            const el = document.getElementById(id);
            if (el) el.textContent = val;
        };

        set('resWuAgent', `${data.weighting_agent} (SG ${data.weighting_agent_sg.toFixed(2)})`);
        set('resWuSacksPer100', `${data.sacks_per_100_bbl.toFixed(1)} sx/100 bbl`);
        set('resWuTotalSacks', `${data.total_sacks.toLocaleString()} sx`);
        set('resWuMetricTons', `${data.total_metric_tons.toFixed(1)} MT`);
        set('resWuVolIncrease', `+${data.volume_increase_bbl.toFixed(1)} bbl`);
        set('resWuFinalVol', `${data.final_volume_bbl.toLocaleString()} bbl`);
        set('resWuCost', `$${data.cost_estimate_usd.toLocaleString(undefined, {minimumFractionDigits: 0, maximumFractionDigits: 0})}`);

    } catch (err) {
        console.error('Weight-up error:', err);
    }
}

async function calculateDilution() {
    const curLgsInput = document.getElementById('dilCurrentLgs').value;
    const tgtLgsInput = document.getElementById('dilTargetLgs').value;

    const payload = {
        initial_mud_weight: parseFloat(document.getElementById('dilInitialMw').value) || 13.0,
        target_mud_weight: parseFloat(document.getElementById('dilTargetMw').value) || 12.4,
        initial_volume: parseFloat(document.getElementById('dilVolume').value) || 600,
        base_fluid: document.getElementById('dilBaseFluid').value || 'fresh_water',
        current_lgs_pct: curLgsInput ? parseFloat(curLgsInput) : null,
        target_lgs_pct: tgtLgsInput ? parseFloat(tgtLgsInput) : null
    };

    try {
        const res = await fetch('/api/volumetrics/dilution', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        if (!res.ok) throw new Error('Dilution calculation failed');
        const data = await res.json();

        const set = (id, val) => {
            const el = document.getElementById(id);
            if (el) el.textContent = val;
        };

        set('resDilBaseDensity', `${data.base_fluid_density_ppg.toFixed(2)} ppg`);
        set('resDilVolDensity', `${data.dilution_volume_for_density_bbl.toLocaleString()} bbl`);
        set('resDilFinalVolDensity', `${data.final_volume_after_density_dilution_bbl.toLocaleString()} bbl`);

        if (data.dilution_volume_for_lgs_bbl !== null) {
            set('resDilVolLgs', `${data.dilution_volume_for_lgs_bbl.toLocaleString()} bbl`);
            set('resDilBariteForLgs', `${data.barite_needed_to_maintain_mw_sacks.toLocaleString()} sx`);
        } else {
            set('resDilVolLgs', 'N/A');
            set('resDilBariteForLgs', 'N/A');
        }

        set('resDilNotes', data.notes);

    } catch (err) {
        console.error('Dilution error:', err);
    }
}

window.initVolumetricsModule = initVolumetricsModule;
window.calculateHoleVolumes = calculateHoleVolumes;
window.calculateWeightUp = calculateWeightUp;
window.calculateDilution = calculateDilution;
