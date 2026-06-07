/**
 * Daily ritual voice agent — ElevenLabs TTS + guided conversation through ritual steps.
 */
(function (global) {
  const COACH_NAME = 'Anna';
  const COACH_TAGLINE = 'your personal hormone intelligence assistant';
  const API = global.location.origin;
  const SpeechRecognition = global.SpeechRecognition || global.webkitSpeechRecognition;

  let voiceRec = null;
  let listening = false;
  let conversationActive = false;
  let conversationPhase = 'mood';
  let voiceCfg = { elevenlabs_enabled: false, fallback: 'browser_speech' };
  let speaking = false;
  let sessionTranscript = '';
  let micStream = null;
  let stopRequested = false;
  let listenSession = 0;
  let listenStarting = false;
  let userStoppedRecording = false;
  let mediaRecorder = null;
  let audioChunks = [];
  let lastVoiceError = '';
  let sending = false;
  let currentAudio = null;
  let speechGen = 0;
  let conversationGen = 0;

  function el(id) {
    return document.getElementById(id);
  }

  function currentStep() {
    if (typeof global.STEPS !== 'undefined' && typeof global.stepIndex === 'number') {
      return global.STEPS[global.stepIndex] || 'general';
    }
    return 'general';
  }

  function buildDailyLogPayload() {
    if (typeof global.draft === 'undefined') return {};
    const d = global.draft;
    return {
      mood: d.mood,
      moodText: d.moodText,
      inflammation: d.infl || 'none',
      infl: d.infl,
      food_triggers: d.foodCats || [],
      foodCats: d.foodCats || [],
      supps: d.supps || [],
      meals: d.meals || [],
      hormoneState: d.hormoneState,
      voice_transcript: d.voice?.transcript || '',
      cognition_signals: d.voice?.cognition_signals || [],
    };
  }

  function applyLogUpdates(updates) {
    if (!updates || typeof global.draft === 'undefined') return;
    if (updates.mood != null) global.draft.mood = updates.mood;
    if (updates.moodText) global.draft.moodText = updates.moodText;
    if (updates.infl) global.draft.infl = updates.infl;
    if (Array.isArray(updates.supps)) global.draft.supps = [...updates.supps];
    if (Array.isArray(updates.foodCats)) global.draft.foodCats = [...updates.foodCats];
    if (Array.isArray(updates.meals)) global.draft.meals = [...updates.meals];
    if (updates.voice) global.draft.voice = updates.voice;
    if (typeof global.stepIndex === 'number' && typeof updates.wizard_step === 'number') {
      global.stepIndex = updates.wizard_step;
    }
    if (typeof global.renderStep === 'function') global.renderStep();
  }

  function appendMessage(role, text) {
    const box = el('agent-messages');
    if (!box) return;
    const div = document.createElement('div');
    div.className = 'agent-msg agent-msg--' + role;
    div.innerHTML = role === 'agent'
      ? `<span class="agent-msg-label">${COACH_NAME}</span>${escapeHtml(text)}`
      : escapeHtml(text);
    box.appendChild(div);
    box.scrollTop = box.scrollHeight;
  }

  function escapeHtml(s) {
    return String(s)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;');
  }

  function setStatus(text) {
    const status = el('agent-status-line');
    if (status) status.textContent = text;
  }

  function renderSuggestions(data) {
    const wrap = el('agent-suggestions');
    if (!wrap) return;
    wrap.innerHTML = '';
    (data.suggestions || []).forEach((s) => {
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'agent-suggest-chip';
      btn.textContent = s.label || 'Apply';
      btn.onclick = () => applySuggestion(s);
      wrap.appendChild(btn);
    });
    if (data.cognition_signals?.length) {
      const note = document.createElement('p');
      note.className = 'agent-cog-note';
      note.textContent = 'Cognition layer · ' + data.cognition_signals.join(', ');
      wrap.appendChild(note);
    }
  }

  function renderQuickReplies(replies) {
    const wrap = el('agent-quick');
    if (!wrap) return;
    wrap.innerHTML = '';
    (replies || []).forEach((q) => {
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'agent-quick-chip';
      btn.textContent = q;
      btn.onclick = () => sendConversationTurn(q);
      wrap.appendChild(btn);
    });
  }

  function applySuggestion(s) {
    if (typeof global.draft === 'undefined') return;
    if (s.field === 'mood' && s.value) global.draft.mood = s.value;
    if (s.field === 'infl' && s.value) global.draft.infl = s.value;
    if (s.field === 'supp' && s.value && !global.draft.supps.includes(s.value)) {
      global.draft.supps.push(s.value);
    }
    if (s.field === 'meal' && s.value && !global.draft.meals.includes(s.value)) {
      global.draft.meals.push(s.value);
    }
    if (typeof global.renderStep === 'function') global.renderStep();
    appendMessage('agent', 'Updated your log draft — check the step above.');
  }

  function pickFemaleVoice() {
    const synth = global.speechSynthesis;
    if (!synth) return null;
    const voices = synth.getVoices() || [];
    const prefer = [
      /kate/i, /serena/i, /victoria/i, /fiona/i, /samantha/i, /karen/i,
      /moira/i, /tessa/i, /veena/i, /zira/i, /female/i, /woman/i,
    ];
    const en = voices.filter((v) => /^en(-|_)/i.test(v.lang));
    for (const pattern of prefer) {
      const match = en.find((v) => pattern.test(v.name));
      if (match) return match;
    }
    return en.find((v) => /google uk english female/i.test(v.name))
      || en.find((v) => /english.*female/i.test(v.name))
      || en[0]
      || voices[0]
      || null;
  }

  function speakBrowser(text) {
    return new Promise((resolve) => {
      if (!global.speechSynthesis) {
        resolve();
        return;
      }
      global.speechSynthesis.cancel();
      const u = new SpeechSynthesisUtterance(text);
      const female = pickFemaleVoice();
      if (female) {
        u.voice = female;
        u.lang = female.lang;
      } else {
        u.lang = 'en-GB';
      }
      u.pitch = 1.05;
      u.rate = 0.93;
      u.onend = () => resolve();
      u.onerror = () => resolve();
      global.speechSynthesis.speak(u);
    });
  }

  function cancelSpeech() {
    speechGen += 1;
    if (currentAudio) {
      currentAudio.pause();
      currentAudio.currentTime = 0;
      currentAudio.onended = null;
      currentAudio.onerror = null;
      currentAudio = null;
    }
    global.speechSynthesis?.cancel();
    speaking = false;
    setOrbSpeaking(false);
  }

  function stopConversation() {
    conversationGen += 1;
    listenSession += 1;
    conversationActive = false;
    cancelSpeech();
    stopListening();
    closeMicStream();
    sending = false;
    listenStarting = false;
    setAskButtonBusy(false);
    userStoppedRecording = false;
    el('agent-voice-btn')?.classList.remove('your-turn');
    el('agent-voice-steps')?.classList.remove('active');
    updateTalkButton(false);
    setStatus(`Stopped — type below or tap ${COACH_NAME} to speak again`);
  }

  function setAskButtonBusy(busy) {
    const btn = el('agent-send-btn');
    if (!btn) return;
    btn.disabled = busy;
    btn.textContent = busy ? '…' : 'ask';
    btn.style.opacity = busy ? '0.6' : '';
    btn.style.pointerEvents = busy ? 'none' : '';
  }

  async function speakText(text, audioBase64) {
    if (!text) return;
    const mySpeech = speechGen;
    speaking = true;
    setOrbSpeaking(true);
    setStatus('Speaking…');
    try {
      if (audioBase64) {
        await new Promise((resolve) => {
          if (mySpeech !== speechGen) {
            resolve();
            return;
          }
          const audio = new Audio('data:audio/mpeg;base64,' + audioBase64);
          currentAudio = audio;
          const done = () => {
            if (currentAudio === audio) currentAudio = null;
            resolve();
          };
          audio.onended = done;
          audio.onerror = () => {
            if (mySpeech !== speechGen) { done(); return; }
            speakBrowser(text).then(done);
          };
          audio.play().catch(() => {
            if (mySpeech !== speechGen) { done(); return; }
            speakBrowser(text).then(done);
          });
        });
      } else if (mySpeech === speechGen) {
        await speakBrowser(text);
      }
    } finally {
      if (mySpeech === speechGen) {
        speaking = false;
        setOrbSpeaking(false);
      }
    }
  }

  async function postConversation(payload) {
    const res = await fetch(API + '/agent/daily/conversation', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        ...payload,
        daily_log: buildDailyLogPayload(),
        phase: conversationPhase,
      }),
    });
    if (!res.ok) throw new Error('Agent unavailable');
    return res.json();
  }

  async function handleConversationResult(data, userText, gen) {
    if (gen !== conversationGen || !conversationActive) return;
    if (userText) appendMessage('user', userText);
    appendMessage('agent', data.answer || data.speak_text);
    renderSuggestions(data);
    renderQuickReplies(data.quick_replies);
    if (data.next_phase) conversationPhase = data.next_phase;
    if (data.wizard_step != null && typeof global.stepIndex === 'number') {
      global.stepIndex = data.wizard_step;
    }
    applyLogUpdates(data.log_updates);
    if (data.lab_context) setStatus('Lab context · ' + data.lab_context);
    if (gen !== conversationGen || !conversationActive) return;
    await speakText(data.speak_text || data.answer, data.audio_base64);
    if (gen !== conversationGen || !conversationActive) return;
    if (data.listening !== false && conversationPhase !== 'done') {
      promptUserTurn();
    } else if (conversationPhase === 'done') {
      stopConversation();
      setStatus('Ritual complete · you can still type questions');
    }
  }

  async function startConversation() {
    if (!canRecordVoice()) {
      appendMessage('agent', 'Voice not available — type your answers in the box below.');
      setStatus('Type your answers below');
      return;
    }
    const micOk = await openMicStream();
    if (!micOk) {
      appendMessage('agent', 'Microphone blocked. Allow mic access for this site in browser settings, then try again.');
      setStatus('Microphone blocked — check browser permissions');
      return;
    }
    const gen = conversationGen;
    conversationActive = true;
    conversationPhase = 'mood';
    if (typeof global.stepIndex === 'number') global.stepIndex = 0;
    if (typeof global.renderStep === 'function') global.renderStep();
    updateTalkButton(true);
    setStatus(`Starting ${COACH_NAME}…`);
    try {
      const data = await postConversation({ message: '', action: 'start' });
      if (gen !== conversationGen) return;
      voiceCfg = data.voice || voiceCfg;
      await handleConversationResult(data, null, gen);
    } catch (_) {
      appendMessage('agent', `Run bash scripts/start.sh — then tap ${COACH_NAME} again.`);
      setStatus('Offline — run bash scripts/start.sh');
      stopConversation();
    }
  }

  async function sendConversationTurn(message) {
    const text = (message || el('agent-input')?.value || '').trim();
    if (!text) {
      setStatus('Type your answer first, then press ask');
      el('agent-input')?.focus();
      return;
    }
    if (sending) return;
    sending = true;
    setAskButtonBusy(true);
    cancelSpeech();
    if (el('agent-input')) el('agent-input').value = '';
    stopListening();
    setStatus('Agent reading your labs…');
    const gen = conversationGen;
    try {
      const data = await postConversation({ message: text, action: 'turn' });
      if (gen !== conversationGen) return;
      await handleConversationResult(data, text, gen);
    } catch (_) {
      appendMessage('agent', 'Connection lost — is the server running?');
      setStatus('Offline — run bash scripts/start.sh');
    } finally {
      sending = false;
      setAskButtonBusy(false);
    }
  }

  async function sendMessage(message) {
    const text = (message || el('agent-input')?.value || '').trim();
    if (!text) {
      setStatus('Type a message first, then press ask');
      el('agent-input')?.focus();
      return;
    }
    if (sending) return;
    if (conversationActive) {
      await sendConversationTurn(text);
      return;
    }
    sending = true;
    setAskButtonBusy(true);
    cancelSpeech();
    appendMessage('user', text);
    if (el('agent-input')) el('agent-input').value = '';
    setStatus('Agent reading your labs…');
    try {
      const res = await fetch(API + '/agent/daily/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: text,
          step: currentStep(),
          daily_log: buildDailyLogPayload(),
        }),
      });
      if (!res.ok) throw new Error('Agent unavailable');
      const data = await res.json();
      appendMessage('agent', data.answer);
      renderSuggestions(data);
      renderQuickReplies(data.quick_replies);
      if (data.voice) voiceCfg = data.voice;
      if (data.lab_context) setStatus('Lab context · ' + data.lab_context);
      await speakText(data.answer, data.audio_base64);
    } catch (_) {
      appendMessage('agent', 'Start the server with bash scripts/start.sh — then I can read your labs.');
      setStatus('Offline — run bash scripts/start.sh');
    } finally {
      sending = false;
      setAskButtonBusy(false);
    }
  }

  function speechSupported() {
    return Boolean(SpeechRecognition);
  }

  function useServerStt() {
    return voiceCfg.stt_mode === 'elevenlabs' || voiceCfg.elevenlabs_enabled;
  }

  function canRecordVoice() {
    return Boolean(global.MediaRecorder && navigator.mediaDevices?.getUserMedia)
      && (useServerStt() || speechSupported());
  }

  function showVoiceError(msg) {
    setStatus(msg);
    if (msg && msg !== lastVoiceError) {
      lastVoiceError = msg;
      appendMessage('agent', msg);
    }
  }

  function pickRecorderMime() {
    if (typeof MediaRecorder === 'undefined') return '';
    for (const t of ['audio/webm;codecs=opus', 'audio/webm', 'audio/mp4']) {
      if (MediaRecorder.isTypeSupported(t)) return t;
    }
    return '';
  }

  async function openMicStream() {
    if (micStream) return true;
    if (!navigator.mediaDevices?.getUserMedia) return true;
    try {
      micStream = await navigator.mediaDevices.getUserMedia({ audio: true });
      return true;
    } catch (_) {
      return false;
    }
  }

  function closeMicStream() {
    if (!micStream) return;
    micStream.getTracks().forEach((t) => t.stop());
    micStream = null;
  }

  function releaseMicIfIdle() {
    if (!conversationActive && !listening) closeMicStream();
  }

  function setRecordingUi(active) {
    el('agent-voice-btn')?.classList.toggle('recording', active);
    const vb = el('agent-voice-btn');
    if (vb) vb.textContent = active ? '■ 2 · send' : '🎙 1 · record';
    const talk = el('agent-talk-btn');
    if (talk && conversationActive) {
      talk.classList.toggle('recording', active);
    }
  }

  function promptUserTurn() {
    setStatus('Step 1: tap 🎙 1 · record — then speak — then tap ■ 2 · send');
    const vb = el('agent-voice-btn');
    const steps = el('agent-voice-steps');
    if (steps) steps.classList.add('active');
    if (vb) {
      vb.classList.add('your-turn');
      setTimeout(() => {
        vb.classList.remove('your-turn');
        steps?.classList.remove('active');
      }, 8000);
    }
  }

  function voiceErrorMessage(err) {
    const messages = {
      'not-allowed': 'Microphone blocked — allow access in browser settings, then tap 🎙 1 · record.',
      'no-speech': 'No speech heard — tap 🎙 1 · record, speak, then ■ 2 · send.',
      network: useServerStt()
        ? 'Connection issue — check Wi‑Fi or type your answer below.'
        : 'Chrome voice needs Google internet. Add ELEVENLABS_API_KEY to .env — or type below.',
      'audio-capture': 'No microphone found — plug in a mic or type your answer below.',
      'service-not-allowed': 'Voice only works on http://127.0.0.1:8080 — run bash scripts/start.sh',
      'language-not-supported': 'Language not supported — tap 🎙 1 · record to try again.',
      aborted: 'Listening stopped',
    };
    return messages[err] || `Voice error (${err}) — type your answer below`;
  }

  async function finishMediaRecording() {
    if (!mediaRecorder || mediaRecorder.state === 'inactive') return;
    const input = el('agent-input');
    const mime = mediaRecorder.mimeType || 'audio/webm';
    await new Promise((resolve) => {
      mediaRecorder.onstop = async () => {
        setRecordingUi(false);
        listening = false;
        mediaRecorder = null;
        const blob = new Blob(audioChunks, { type: mime });
        audioChunks = [];
        releaseMicIfIdle();
        if (blob.size < 500) {
          setStatus('Too short — speak longer, then tap ■ 2 · send');
          resolve();
          return;
        }
        setStatus('Transcribing…');
        try {
          const fd = new FormData();
          fd.append('file', blob, 'recording.webm');
          const res = await fetch(API + '/agent/daily/transcribe', { method: 'POST', body: fd });
          if (!res.ok) {
            const err = await res.json().catch(() => ({}));
            throw new Error(err.detail || 'transcribe failed');
          }
          const data = await res.json();
          const transcript = (data.transcript || '').trim();
          if (input) input.value = transcript;
          if (!transcript) {
            setStatus('No speech heard — try again or type below');
            if (conversationActive && conversationPhase !== 'done') promptUserTurn();
            resolve();
            return;
          }
          if (conversationActive) await sendConversationTurn(transcript);
          else await sendMessage(transcript);
        } catch (e) {
          const msg = String(e.message || '');
          showVoiceError(
            msg.includes('permission') || msg.includes('speech_to_text')
              ? msg
              : msg.includes('ELEVENLABS') || msg.includes('not set')
                ? 'Add ELEVENLABS_API_KEY to .env and restart — or type below.'
                : msg && msg !== 'transcribe failed'
                  ? msg
                  : 'Could not transcribe — type your answer below.',
          );
        }
        resolve();
      };
      try {
        if (mediaRecorder.state === 'recording') mediaRecorder.requestData();
        mediaRecorder.stop();
      } catch (_) { resolve(); }
    });
  }

  async function startMediaRecording() {
    if (!micStream) return false;
    const mime = pickRecorderMime();
    audioChunks = [];
    try {
      mediaRecorder = mime
        ? new MediaRecorder(micStream, { mimeType: mime })
        : new MediaRecorder(micStream);
    } catch (_) {
      showVoiceError('Recording not supported — type your answer below.');
      return false;
    }
    mediaRecorder.ondataavailable = (e) => {
      if (e.data && e.data.size > 0) audioChunks.push(e.data);
    };
    mediaRecorder.start(300);
    listening = true;
    el('agent-voice-btn')?.classList.remove('your-turn');
    setRecordingUi(true);
    setStatus('Step 2: speak now — then tap ■ 2 · send');
    return true;
  }

  function finishListening() {
    userStoppedRecording = true;
    stopRequested = true;
    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
      finishMediaRecording();
      return;
    }
    if (voiceRec) {
      try { voiceRec.stop(); } catch (_) { /* ignore */ }
    }
  }

  function stopListening() {
    stopRequested = true;
    listening = false;
    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
      mediaRecorder.onstop = null;
      try {
        mediaRecorder.requestData();
        mediaRecorder.stop();
      } catch (_) { /* ignore */ }
      mediaRecorder = null;
      audioChunks = [];
    }
    if (voiceRec) {
      try { voiceRec.stop(); } catch (_) { /* ignore */ }
      voiceRec.onresult = null;
      voiceRec.onend = null;
      voiceRec.onerror = null;
      voiceRec.onstart = null;
      voiceRec = null;
    }
    closeMicStream();
    setRecordingUi(false);
  }

  function updateTalkButton(active) {
    const btn = el('agent-talk-btn');
    const label = el('agent-talk-label');
    if (!btn) return;
    btn.classList.toggle('active', active);
    btn.setAttribute('aria-label', active ? `Stop ${COACH_NAME}` : `Talk to ${COACH_NAME}`);
    if (label) label.textContent = active ? 'tap to stop' : `tap ${COACH_NAME} to speak`;
  }

  function setOrbSpeaking(on) {
    el('agent-talk-btn')?.classList.toggle('speaking', on);
  }

  async function startListening() {
    if (!canRecordVoice()) {
      setStatus('Voice not available — type your answer below');
      return false;
    }
    if (listenStarting) return false;
    if (speaking) {
      setStatus('Wait until I finish speaking, then tap 🎙 1 · record');
      return false;
    }

    listenStarting = true;
    setStatus('Opening microphone…');
    el('agent-voice-btn')?.classList.remove('your-turn');
    try {
      const micOk = await openMicStream();
      if (!micOk) {
        showVoiceError('Mic blocked — allow access in browser settings, or type below.');
        return false;
      }

      global.speechSynthesis?.cancel();

      if (useServerStt()) {
        return await startMediaRecording();
      }

      if (!speechSupported()) {
        setStatus('Add ELEVENLABS_API_KEY for voice — or type below');
        return false;
      }

      const input = el('agent-input');
      sessionTranscript = '';
      userStoppedRecording = false;
      stopRequested = false;
      listenSession += 1;
      const session = listenSession;

      voiceRec = new SpeechRecognition();
      voiceRec.continuous = true;
      voiceRec.interimResults = true;
      voiceRec.lang = navigator.language || 'en-US';
      voiceRec.maxAlternatives = 1;

      voiceRec.onstart = () => {
        if (session !== listenSession) return;
        listening = true;
        el('agent-voice-btn')?.classList.remove('your-turn');
        setRecordingUi(true);
        setStatus('Step 2: speak now — then tap ■ 2 · send');
      };

      voiceRec.onresult = (event) => {
        if (session !== listenSession) return;
        let full = '';
        for (let i = 0; i < event.results.length; i++) {
          full += event.results[i][0].transcript;
        }
        sessionTranscript = full.trim();
        if (input) input.value = sessionTranscript;
        if (sessionTranscript) {
          setStatus('Recording… ' + sessionTranscript.slice(0, 48) + (sessionTranscript.length > 48 ? '…' : ''));
        }
      };

      voiceRec.onend = async () => {
        if (session !== listenSession) return;
        setRecordingUi(false);
        listening = false;
        voiceRec = null;
        releaseMicIfIdle();
        const transcript = (sessionTranscript || input?.value || '').trim();
        sessionTranscript = '';
        const stopped = userStoppedRecording;
        userStoppedRecording = false;
        stopRequested = false;

        if (!transcript) {
          setStatus(stopped
            ? 'No speech heard — tap 🎙 1 · record, speak, then ■ 2 · send (or type below)'
            : 'Didn\'t catch that — tap 🎙 1 · record and try again');
          if (conversationActive && conversationPhase !== 'done') promptUserTurn();
          return;
        }
        if (conversationActive) {
          await sendConversationTurn(transcript);
        } else {
          await sendMessage(transcript);
        }
      };

      voiceRec.onerror = (event) => {
        if (session !== listenSession) return;
        if (stopRequested) return;
        setRecordingUi(false);
        listening = false;
        voiceRec = null;
        releaseMicIfIdle();
        const err = event.error || 'unknown';
        if (err === 'aborted') return;
        if (err !== 'no-speech') showVoiceError(voiceErrorMessage(err));
        else setStatus(voiceErrorMessage(err));
      };

      voiceRec.start();
      return true;
    } catch (_) {
      listening = false;
      voiceRec = null;
      releaseMicIfIdle();
      setRecordingUi(false);
      setStatus('Could not start mic — tap 🎙 1 · record or type below');
      return false;
    } finally {
      listenStarting = false;
    }
  }

  function toggleConversation() {
    if (conversationActive || speaking || listening) {
      stopConversation();
      return;
    }
    startConversation();
  }

  function isLocalApp() {
    return global.location.protocol === 'http:' || global.location.protocol === 'https:';
  }

  function submitAsk(e) {
    if (e) e.preventDefault();
    sendMessage();
  }

  async function initDailyAgent() {
    const form = el('agent-form');
    const askBtn = el('agent-send-btn');
    const input = el('agent-input');
    form?.addEventListener('submit', submitAsk);
    askBtn?.addEventListener('click', submitAsk);
    input?.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        submitAsk();
      }
    });
    el('agent-voice-btn')?.addEventListener('click', () => {
      if (listening) {
        finishListening();
        return;
      }
      startListening();
    });
    el('agent-talk-btn')?.addEventListener('click', toggleConversation);

    try {
      const cfgRes = await fetch(API + '/agent/voice/config');
      if (cfgRes.ok) voiceCfg = await cfgRes.json();
    } catch (_) { /* offline */ }

    if (global.speechSynthesis) {
      global.speechSynthesis.onvoiceschanged = () => pickFemaleVoice();
      pickFemaleVoice();
    }
    const voiceHint = useServerStt()
      ? "Women's voice · Matilda · ElevenLabs voice in + out (no Chrome Google speech)"
      : canRecordVoice()
        ? 'Browser voice — add ELEVENLABS_API_KEY to .env'
        : 'Type your answers below';
    const ttsNote = voiceCfg.elevenlabs_enabled
      ? `${COACH_NAME} · ${voiceHint}`
      : `${COACH_NAME} · ${COACH_TAGLINE}${voiceHint ? ' · ' + voiceHint : ''}`;
    setStatus(ttsNote);

    if (!voiceCfg.elevenlabs_enabled && isLocalApp()) {
      appendMessage('agent', voiceCfg.setup_hint || 'Add ELEVENLABS_API_KEY to .env — then run bash scripts/start.sh');
    } else if (!isLocalApp()) {
      appendMessage('agent', 'Open http://127.0.0.1:8080/daily.html after running bash scripts/start.sh — voice needs the server.');
    } else if (useServerStt()) {
      appendMessage(
        'agent',
        `Hi — I'm ${COACH_NAME}, ${COACH_TAGLINE}. I'll use your labs and check how your mental health connects to them. Tap the orb — when I finish: ① 🎙 record ② speak ③ ■ send.`,
      );
    } else {
      appendMessage(
        'agent',
        'Voice may fail without ElevenLabs. Add ELEVENLABS_API_KEY to .env — or type answers below.',
      );
    }
  }

  global.HsenceDailyAgent = {
    init: initDailyAgent,
    send: sendMessage,
    startConversation,
    stopConversation,
    refreshQuickReplies(step) {
      if (conversationActive) return;
      fetch(API + '/agent/daily/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: '', step: step || currentStep(), daily_log: buildDailyLogPayload() }),
      })
        .then((r) => r.json())
        .then((d) => renderQuickReplies(d.quick_replies))
        .catch(() => {});
    },
  };

  global.addEventListener('DOMContentLoaded', initDailyAgent);
})(window);
