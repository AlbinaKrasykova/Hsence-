const AGENT_API = window.location.origin;

const LAYER_META = {
  hormones: { icon: '◐', color: 'var(--lavender)' },
  metabolic: { icon: '◆', color: 'var(--amber)' },
  cognition: { icon: '○', color: 'var(--blue-mid)' },
  inflammation: { icon: '◇', color: 'var(--green)' },
};

let lastResult = null;

function buildPayload() {
  return {
    profile: {
      name: document.getElementById('p-name').value,
      sex: document.getElementById('p-sex').value,
      age: parseInt(document.getElementById('p-age').value, 10) || 34,
    },
    chat_message: document.getElementById('chat-message')?.value?.trim() || '',
    wearable: {
      sleep_hours: parseFloat(document.getElementById('w-sleep').value) || 5.7,
      hrv_delta: parseFloat(document.getElementById('w-hrv').value) || 0.08,
      readiness: parseInt(document.getElementById('w-ready').value, 10) || 74,
    },
    daily_log: {
      mood: parseInt(document.querySelector('input[name=mood]:checked')?.value || '3', 10),
      inflammation: document.getElementById('d-infl').value,
      food_triggers: getSelectedTriggers(),
    },
  };
}

async function runAgent(eventType = 'full_cycle') {
  const status = document.getElementById('agent-status');
  const btn = document.getElementById('btn-run-agent');
  status.textContent = 'agent planning tools…';
  btn.disabled = true;

  try {
    const res = await fetch(`${AGENT_API}/agent/run`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ event_type: eventType, payload: buildPayload() }),
    });
    if (!res.ok) throw new Error('Agent API error');
    lastResult = await res.json();
    renderResult(lastResult);
    const plan = lastResult.plan || lastResult.cycle?.plan;
    status.textContent = `cycle complete · ${lastResult.cycle?.duration_ms || '?'}ms · ${plan?.tools?.length || lastResult.cycle?.tools_run?.length || 0} tools planned`;
  } catch (e) {
    status.textContent = 'start agent: .venv/bin/python scripts/run_agent.py';
    document.getElementById('api-hint').classList.add('show');
  } finally {
    btn.disabled = false;
  }
}

function getSelectedTriggers() {
  return [...document.querySelectorAll('.trigger-chip.on')].map((el) => el.dataset.id);
}

function renderResult(data) {
  document.getElementById('api-hint').classList.remove('show');
  document.getElementById('summary-text').textContent = data.summary || '';
  document.getElementById('pattern-badge').textContent = data.pattern || 'precision read';
  document.getElementById('disclaimer').textContent = data.disclaimer || '';

  const intentEl = document.getElementById('intent-badge');
  if (data.intent?.intent) {
    intentEl.textContent = `intent · ${data.intent.intent.replace(/_/g, ' ')} · risk ${data.intent.risk_level || 'low'}`;
    intentEl.classList.remove('hidden');
  } else {
    intentEl.classList.add('hidden');
  }

  const plan = data.plan || data.cycle?.plan;
  const planBox = document.getElementById('plan-box');
  const planSteps = document.getElementById('plan-steps');
  if (plan?.tools?.length) {
    planBox.classList.remove('hidden');
    planSteps.innerHTML = plan.tools
      .map(
        (t, i) =>
          `<div class="plan-step"><span class="plan-step-num">${i + 1}.</span><span><strong>${t}</strong> — ${(plan.tool_descriptions && plan.tool_descriptions[t]) || ''}${plan.reasoning?.[i] ? `<br><span style="opacity:0.75">${plan.reasoning[i]}</span>` : ''}</span></div>`
      )
      .join('');
  }

  const layersEl = document.getElementById('layers-grid');
  layersEl.innerHTML = Object.values(data.layers || {})
    .map((layer) => {
      const meta = LAYER_META[layer.id] || { icon: '·', color: 'var(--text-mid)' };
      return `
        <div class="layer-card" data-layer="${layer.id}">
          <div class="layer-top">
            <span class="layer-icon" style="color:${meta.color}">${meta.icon}</span>
            <span class="layer-status">${layer.status || 'monitor'}</span>
          </div>
          <div class="layer-name">${layer.label}</div>
          <div class="layer-score"><span>${layer.score}</span>/100</div>
          <div class="layer-bar"><div class="layer-fill" style="width:${layer.score}%;background:${meta.color}"></div></div>
          <div class="layer-signals">${(layer.signals || []).map((s) => `<span class="signal-chip">${s}</span>`).join('') || '<span class="signal-chip">stable signals</span>'}</div>
        </div>`;
    })
    .join('');

  document.getElementById('gaps-list').innerHTML = (data.care_gaps || [])
    .map(
      (g) => `
      <div class="gap-card gap-${g.level}">
        <div class="gap-head"><span class="gap-level">${g.level}</span><span class="gap-score">${g.score}%</span></div>
        <div class="gap-name">${g.name}</div>
        <div class="gap-note">${g.note}</div>
        <div class="gap-evidence">${(g.evidence || []).map((e) => `<code>${e}</code>`).join('')}</div>
        <div class="gap-layers">${(g.layers || []).map((l) => `<span class="layer-tag">${l}</span>`).join('')}</div>
      </div>`
    )
    .join('');

  const precision = data.precision_plan || {};
  renderPlanList('meals-list', precision.meals, (m) => `<strong>${m.name}</strong><span>${m.meta}</span>`);
  renderPlanList('foods-list', precision.foods, (f) => `<strong>${f.title}</strong><span>${f.why}</span>`);
  renderPlanList(
    'supps-list',
    precision.supplements,
    (s) => `<strong>${s.name}</strong><span>${s.evidence} · ${s.note || ''}</span>`
  );
  renderPlanList('life-list', precision.lifestyle, (l) => `<strong>${l.name}</strong><span>layers: ${(l.layers || []).join(', ')}</span>`);

  const handoff = data.clinician_handoff || {};
  const doctorEl = document.getElementById('doctor-list');
  if (handoff.questions_for_doctor?.length) {
    doctorEl.innerHTML = handoff.questions_for_doctor
      .map((q) => `<div class="doctor-q"><strong>${q.q}</strong>Because: ${q.because}</div>`)
      .join('');
  } else {
    doctorEl.innerHTML = '<p class="empty-plan">run agent to generate handoff questions</p>';
  }

  const trialsEl = document.getElementById('trials-list');
  if (data.trials?.length) {
    trialsEl.innerHTML = data.trials
      .map(
        (t) => `
        <div class="trial-card">
          <div class="trial-id">${t.id} · ${t.phase}</div>
          <strong style="font-weight:400;font-size:0.85rem">${t.title}</strong>
          <p style="font-size:0.74rem;color:var(--text-mid);margin-top:0.35rem">${t.match_reason}</p>
        </div>`
      )
      .join('');
  } else {
    trialsEl.innerHTML = '<p class="empty-plan">no trial matches for current gaps</p>';
  }

  const guideEl = document.getElementById('guidelines-list');
  if (data.guidelines?.length) {
    guideEl.innerHTML = data.guidelines
      .map(
        (g) => `
        <div class="guideline-card">
          <div class="guideline-src">${g.source || 'reference'}</div>
          <strong style="font-weight:400;color:var(--text-dark)">${g.title}</strong>
          <p style="margin-top:0.35rem">${g.snippet}</p>
        </div>`
      )
      .join('');
  } else {
    guideEl.innerHTML = '<p class="empty-plan">run agent for evidence snippets</p>';
  }

  const traceEl = document.getElementById('trace-list');
  traceEl.innerHTML = (data.trace || [])
    .map((t) => {
      let detail = (t.evidence || t.flags || t.reasoning || []).slice(0, 3).join(' · ');
      if (t.tool === 'agent_planner') detail = (t.reasoning || []).join(' · ');
      if (!detail && t.passed === false) detail = 'guardrail adjusted';
      if (!detail && t.tools) detail = `Planned: ${t.tools.join(' → ')}`;
      return `
      <div class="trace-item">
        <div class="trace-tool">${t.tool || 'step'}</div>
        <div class="trace-detail">${detail || 'ok'}</div>
        ${t.duration_ms ? `<div class="trace-ms">${t.duration_ms}ms</div>` : ''}
      </div>`;
    })
    .join('');
}

function renderPlanList(id, items, fn) {
  const el = document.getElementById(id);
  if (!items?.length) {
    el.innerHTML = '<p class="empty-plan">run agent to generate personalised plan</p>';
    return;
  }
  el.innerHTML = items.map((item) => `<div class="plan-row">${fn(item)}</div>`).join('');
}

document.getElementById('btn-run-agent').addEventListener('click', () => runAgent('full_cycle'));
document.getElementById('btn-adapt').addEventListener('click', () => runAgent('daily_log'));
document.getElementById('btn-handoff').addEventListener('click', () => runAgent('clinician_handoff'));

document.querySelectorAll('.trigger-chip').forEach((el) => {
  el.addEventListener('click', () => el.classList.toggle('on'));
});

fetch(`${AGENT_API}/agent/health`)
  .then((r) => r.ok && runAgent('full_cycle'))
  .catch(() => {
    document.getElementById('agent-status').textContent = 'start agent: .venv/bin/python scripts/run_agent.py';
    document.getElementById('api-hint').classList.add('show');
  });
