/* ============================================
    Candidate Ranking System Frontend Logic
    ============================================ */

// ==================== CONFIG ====================
const API_BASE = 'http://127.0.0.1:5000';

// ==================== STATE ====================
const state = {
    jdFile: null,
    resumeFiles: [],
    analysesCount: 0,
    currentResults: null,
    jdText: '',
    chart: null,
    chartType: 'radar',
    analyticsChartType: 'bar',
    compareQueue: [],
    scoreDistChart: null,
    skillCoverageChart: null,
    expDistChart: null,
    potentialChart: null,
    shortlisted: new Set(),
    selectedCandidates: new Set(),
    sortField: 'rank',
    sortAsc: true,
    scores: [],
    customWeights: null,
    serverWeights: null,
    weightsInitialized: false
};

// ==================== INIT ====================
document.addEventListener('DOMContentLoaded', () => {
    checkHealth();
    setupDragDrop();
    setupTextAreaSubmit();
    initParticles();
    updateCharCount();
    initKeyboardShortcuts();
    loadShortlist();
    addStylesForNewFeatures();
    renderCopilotSuggestions();
});

// ==================== ADD NEW CSS STYLES ====================
function addStylesForNewFeatures() {
    const style = document.createElement('style');
    style.textContent = `
        /* Multi-select actions bar */
        .bulk-actions-bar {
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 10px 16px;
            background: var(--glass-bg-heavy);
            border: 1px solid var(--glass-border);
            border-radius: var(--radius-sm);
            margin-bottom: 10px;
            animation: slideDown 0.3s ease;
            flex-wrap: wrap;
        }
        .bulk-actions-bar .selected-count {
            font-size: 0.85rem;
            color: var(--accent-2);
            font-weight: 600;
        }
        .bulk-actions-bar .bulk-btn {
            padding: 6px 14px;
            border-radius: var(--radius-sm);
            border: 1px solid var(--glass-border);
            background: var(--glass-bg);
            color: var(--text-primary);
            font-size: 0.8rem;
            cursor: pointer;
            transition: all 0.2s;
            font-family: var(--font);
        }
        .bulk-actions-bar .bulk-btn:hover {
            border-color: var(--accent-1);
            background: rgba(108,99,255,0.1);
        }
        .bulk-actions-bar .bulk-btn.danger {
            border-color: rgba(255,71,87,0.2);
            color: var(--danger);
        }
        .bulk-actions-bar .bulk-btn.danger:hover {
            background: rgba(255,71,87,0.1);
        }
        
        /* KPI Cards */
        .kpi-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin-bottom: 1.5rem;
        }
        .kpi-card {
            padding: 1.2rem;
            text-align: center;
            background: var(--glass-bg);
            border: 1px solid var(--glass-border);
            border-radius: var(--radius-md);
            transition: all var(--transition-normal);
            position: relative;
            overflow: hidden;
        }
        .kpi-card:hover {
            transform: translateY(-2px);
            border-color: var(--glass-border-hover);
        }
        .kpi-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: var(--accent-gradient);
            opacity: 0.7;
        }
        .kpi-icon {
            font-size: 1.5rem;
            margin-bottom: 0.5rem;
        }
        .kpi-value {
            font-size: 1.6rem;
            font-weight: 800;
            background: var(--accent-gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .kpi-label {
            font-size: 0.7rem;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-top: 4px;
        }
        
        /* Hiring score meter */
        .hiring-meter {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 1rem;
        }
        .hiring-meter-bar {
            flex: 1;
            height: 12px;
            background: var(--glass-bg);
            border-radius: 10px;
            overflow: hidden;
            position: relative;
        }
        .hiring-meter-fill {
            height: 100%;
            border-radius: 10px;
            transition: width 1.5s ease;
            background: linear-gradient(90deg, #ff4757, #ffa502, #00d4ff, #00ff88);
            background-size: 200% 100%;
        }
        .hiring-meter-label {
            font-size: 0.75rem;
            color: var(--text-muted);
            min-width: 60px;
        }
        .hiring-meter-value {
            font-size: 1.2rem;
            font-weight: 700;
            min-width: 50px;
            text-align: right;
        }
        
        /* Similarity matrix grid */
        .similarity-grid {
            display: grid;
            gap: 6px;
            padding: 0.5rem;
        }
        .similarity-cell {
            padding: 8px;
            border-radius: var(--radius-xs);
            text-align: center;
            font-size: 0.75rem;
            font-weight: 600;
            transition: all 0.2s;
        }
        .similarity-cell:hover {
            transform: scale(1.05);
        }
        .similarity-label {
            font-size: 0.7rem;
            color: var(--text-muted);
            padding: 4px;
            text-align: center;
            font-weight: 600;
        }
        
        /* Loading shimmer for tables */
        .loading-row {
            height: 48px;
        }
        .loading-row td {
            padding: 8px 12px;
        }
        .shimmer-block {
            height: 16px;
            border-radius: var(--radius-xs);
            background: linear-gradient(90deg, var(--glass-bg) 25%, var(--glass-bg-heavy) 50%, var(--glass-bg) 75%);
            background-size: 200% 100%;
            animation: shimmer 1.5s ease-in-out infinite;
        }
        .shimmer-block.w60 { width: 60px; }
        .shimmer-block.w80 { width: 80px; }
        .shimmer-block.w120 { width: 120px; }
        
        /* Batch select all checkbox */
        .select-all-cell {
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .select-all-checkbox {
            width: 16px;
            height: 16px;
            accent-color: var(--accent-1);
            cursor: pointer;
        }
        
        /* Candidate similarity matrix modal */
        .matrix-container {
            overflow-x: auto;
            padding: 1rem 0;
        }
        .matrix-table {
            border-collapse: collapse;
            font-size: 0.75rem;
            margin: 0 auto;
        }
        .matrix-table th {
            padding: 8px 6px;
            font-weight: 600;
            color: var(--text-muted);
            border-bottom: 1px solid var(--glass-border);
            text-align: center;
        }
        .matrix-table th:first-child {
            text-align: left;
            min-width: 100px;
        }
        .matrix-table td {
            padding: 6px;
            text-align: center;
            border: 1px solid var(--glass-border);
        }
        .matrix-cell {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 40px;
            height: 30px;
            border-radius: var(--radius-xs);
            font-weight: 600;
            font-size: 0.75rem;
        }

        /* Progress stages */
        .progress-stages {
            display: flex;
            justify-content: space-between;
            margin: 16px 0;
            position: relative;
        }
        .progress-stages::before {
            content: '';
            position: absolute;
            top: 50%;
            left: 0;
            right: 0;
            height: 2px;
            background: var(--glass-border);
            transform: translateY(-50%);
            z-index: 0;
        }
        .stage-item {
            display: flex;
            flex-direction: column;
            align-items: center;
            position: relative;
            z-index: 1;
            gap: 4px;
        }
        .stage-dot {
            width: 24px;
            height: 24px;
            border-radius: 50%;
            background: var(--glass-bg);
            border: 2px solid var(--glass-border);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.6rem;
            transition: all 0.3s;
            color: var(--text-muted);
        }
        .stage-dot.completed {
            background: var(--accent-gradient);
            border-color: transparent;
            color: white;
        }
        .stage-dot.active {
            border-color: var(--accent-1);
            box-shadow: 0 0 12px rgba(108,99,255,0.4);
            animation: pulseGlow 2s ease-in-out infinite;
        }
        .stage-label {
            font-size: 0.6rem;
            color: var(--text-muted);
            text-align: center;
            max-width: 70px;
        }
        .stage-label.completed {
            color: var(--accent-2);
        }
    `;
    document.head.appendChild(style);
}

// ==================== PARTICLES ====================
function initParticles() {
    const canvas = document.getElementById('particles-canvas') || document.createElement('canvas');
    if (!canvas.id) { canvas.id = 'particles-canvas'; document.body.prepend(canvas); }
    const ctx = canvas.getContext('2d');
    let particles = [];
    let animationId = null;
    
    function resize() { canvas.width = window.innerWidth; canvas.height = window.innerHeight; }
    resize();
    window.addEventListener('resize', resize);

    for (let i = 0; i < 60; i++) {
        particles.push({
            x: Math.random() * canvas.width,
            y: Math.random() * canvas.height,
            vx: (Math.random() - 0.5) * 0.5,
            vy: (Math.random() - 0.5) * 0.5,
            r: Math.random() * 2 + 0.5,
            alpha: Math.random() * 0.4 + 0.1
        });
    }

    function animate() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        particles.forEach((p, i) => {
            p.x += p.vx;
            p.y += p.vy;
            if (p.x < 0) p.x = canvas.width;
            if (p.x > canvas.width) p.x = 0;
            if (p.y < 0) p.y = canvas.height;
            if (p.y > canvas.height) p.y = 0;

            ctx.beginPath();
            ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
            ctx.fillStyle = `rgba(108, 99, 255, ${p.alpha})`;
            ctx.fill();

            particles.slice(i + 1).forEach(p2 => {
                const dx = p.x - p2.x;
                const dy = p.y - p2.y;
                const dist = Math.sqrt(dx * dx + dy * dy);
                if (dist < 150) {
                    ctx.beginPath();
                    ctx.moveTo(p.x, p.y);
                    ctx.lineTo(p2.x, p2.y);
                    ctx.strokeStyle = `rgba(108, 99, 255, ${0.08 * (1 - dist / 150)})`;
                    ctx.stroke();
                }
            });
        });
        animationId = requestAnimationFrame(animate);
    }
    animate();
}

// ==================== KEYBOARD SHORTCUTS ====================
function initKeyboardShortcuts() {
    document.addEventListener('keydown', (e) => {
        if (e.ctrlKey && e.key === 'Enter') {
            e.preventDefault();
            analyze();
        }
        if (e.ctrlKey && e.shiftKey && e.key.toLowerCase() === 't') {
            e.preventDefault();
            toggleTheme();
        }
        if (e.ctrlKey && !e.shiftKey && e.key >= '1' && e.key <= '6') {
            e.preventDefault();
            const tabs = ['upload', 'rankings', 'shortlist', 'analytics', 'copilot', 'bias'];
            const idx = parseInt(e.key) - 1;
            if (idx < tabs.length) {
                const btn = document.querySelector(`[data-tab="${tabs[idx]}"]`);
                if (btn && !btn.disabled) switchTab(tabs[idx]);
            }
        }
        if (e.key === 'Escape') {
            closeModal();
            closeCompareModal();
            closeInterviewModal();
        }
        if (e.key === '/' && !['INPUT', 'TEXTAREA'].includes(e.target.tagName)) {
            e.preventDefault();
            const search = document.getElementById('searchInput');
            if (search) search.focus();
        }
    });

    let lastScroll = 0;
    window.addEventListener('scroll', () => {
        const navbar = document.getElementById('navbar');
        if (window.scrollY > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    });
}

// ==================== TABS ====================
function switchTab(tabName) {
    document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
    document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));
    
    const tabContent = document.getElementById(`tab-${tabName}`);
    if (tabContent) tabContent.classList.add('active');
    
    const btn = document.querySelector(`[data-tab="${tabName}"]`);
    if (btn) btn.classList.add('active');
    
    if (tabName === 'analytics' && state.currentResults) {
        renderAnalytics(state.currentResults);
    }
    if (tabName === 'bias' && state.currentResults) {
        renderBiasReport(state.currentResults);
    }
    if (tabName === 'shortlist') {
        renderShortlist();
    }
    if (tabName === 'rankings') {
        renderResults(state.currentResults);
    }
}

// ==================== HEALTH CHECK ====================
async function checkHealth() {
    try {
        const res = await fetch(API_BASE + '/api/health');
        const data = await res.json();
        document.getElementById('modelStatusText').textContent = 'System Ready';
        document.getElementById('modelStatus').className = 'nav-badge ready';
        document.getElementById('navCandidates').textContent = '7';
        document.getElementById('heroProcessed').textContent = 'Sample';
        showToast('✅ System connected. Ready to analyze candidates.', 'success');
    } catch (e) {
        document.getElementById('modelStatusText').textContent = 'Server Offline';
        document.getElementById('modelStatus').className = 'nav-badge offline';
        showToast('⚠️ Server offline. Start the backend with: python app.py', 'warning');
    }
}

// ==================== THEME ====================
function toggleTheme() {
    const html = document.documentElement;
    const current = html.getAttribute('data-theme');
    const next = current === 'dark' ? 'light' : 'dark';
    html.setAttribute('data-theme', next);
    document.getElementById('themeIcon').textContent = next === 'dark' ? '🌙' : '☀️';
    localStorage.setItem('talentrank-theme', next);
}

(function loadTheme() {
    const saved = localStorage.getItem('talentrank-theme');
    if (saved) {
        document.documentElement.setAttribute('data-theme', saved);
        document.getElementById('themeIcon').textContent = saved === 'dark' ? '🌙' : '☀️';
    }
})();

// ==================== DRAG DROP ====================
function setupDragDrop() {
    ['jdDropzone', 'resumeDropzone'].forEach(id => {
        const el = document.getElementById(id);
        if (!el) return;
        el.addEventListener('dragover', (e) => { e.preventDefault(); el.classList.add('dragover'); });
        el.addEventListener('dragleave', () => el.classList.remove('dragover'));
        el.addEventListener('drop', (e) => {
            e.preventDefault();
            el.classList.remove('dragover');
            const files = e.dataTransfer.files;
            if (id === 'jdDropzone' && files.length > 0) {
                handleJDFile({ target: { files: [files[0]] } });
            } else if (id === 'resumeDropzone' && files.length > 0) {
                handleResumeFiles({ target: { files: Array.from(files) } });
            }
        });
    });
}

function setupTextAreaSubmit() {
    const textarea = document.getElementById('jdText');
    if (textarea) {
        textarea.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.key === 'Enter') { e.preventDefault(); analyze(); }
        });
    }
}

// ==================== FILE HANDLERS ====================
function handleJDFile(event) {
    const file = event && event.target && event.target.files ? event.target.files[0] : null;
    if (!file) return;
    state.jdFile = file;
    const info = document.getElementById('jdFileInfo');
    document.getElementById('jdFileName').textContent = file.name;
    document.getElementById('jdFileSize').textContent = `(${(file.size / 1024).toFixed(1)} KB)`;
    info.style.display = 'flex';
    showToast(`JD "${file.name}" loaded`, 'success');
}

function removeJDFile() {
    state.jdFile = null;
    document.getElementById('jdFileInfo').style.display = 'none';
    const input = document.getElementById('jdFile');
    if (input) input.value = '';
}

function handleResumeFiles(event) {
    const files = event && event.target && event.target.files ? Array.from(event.target.files) : [];
    if (files.length === 0) return;
    state.resumeFiles = files;
    const info = document.getElementById('resumeFileInfo');
    document.getElementById('resumeCount').textContent = `${files.length} files`;
    const totalSize = files.reduce((s, f) => s + f.size, 0);
    document.getElementById('resumeDetails').textContent = `(${(totalSize / 1024).toFixed(1)} KB total)`;
    info.style.display = 'flex';
    document.getElementById('navCandidates').textContent = files.length;
    showToast(`${files.length} resume(s) loaded`, 'success');
}

function removeResumes() {
    state.resumeFiles = [];
    document.getElementById('resumeFileInfo').style.display = 'none';
    const input = document.getElementById('resumeFiles');
    if (input) input.value = '';
    document.getElementById('navCandidates').textContent = '0';
}

function updateCharCount() {
    const text = document.getElementById('jdText').value;
    document.getElementById('charCount').textContent = `${text.length} characters`;
    state.jdText = text;
}

// ==================== TOASTS ====================
function showToast(message, type) {
    if (!type) type = 'info';
    const container = document.getElementById('toastContainer');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    const icons = { success: '✅', error: '❌', info: 'ℹ️', warning: '⚠️' };
    const icon = icons[type] || 'ℹ️';
    toast.innerHTML = `
        <span class="toast-icon">${icon}</span>
        <span class="toast-message">${message}</span>
        <button class="toast-close" onclick="this.parentElement.remove()">✕</button>
    `;
    container.appendChild(toast);
    setTimeout(() => toast.classList.add('show'), 10);
    setTimeout(() => { toast.classList.remove('show'); setTimeout(() => toast.remove(), 300); }, 4000);
}

// ==================== PROGRESS BAR ====================
function showProgress(label, percent, sublabel) {
    const container = document.getElementById('progressContainer');
    const fill = document.getElementById('progressFill');
    const labelEl = document.getElementById('progressLabel');
    const percentEl = document.getElementById('progressPercent');
    
    container.classList.add('active');
    fill.style.width = `${Math.min(percent, 100)}%`;
    labelEl.textContent = sublabel ? `${label} — ${sublabel}` : label;
    percentEl.textContent = `${Math.round(percent)}%`;
}

function hideProgress() {
    const container = document.getElementById('progressContainer');
    container.classList.remove('active');
}

// ==================== MAIN ANALYZE ====================
async function analyze() {
    const btn = document.getElementById('analyzeBtn');
    const jdText = document.getElementById('jdText').value.trim();
    const reason = document.getElementById('analyzeHint');

    if (!state.jdFile && !jdText) {
        showToast('Please upload a job description or paste the JD text', 'error');
        if (reason) { reason.textContent = '⚠️ A job description is required (upload a file or paste the text).'; reason.style.display = ''; }
        return;
    }
    if (state.resumeFiles.length === 0) {
        showToast('Please upload at least one candidate resume', 'error');
        if (reason) { reason.textContent = '⚠️ Add at least one resume (PDF, DOCX or TXT).'; reason.style.display = ''; }
        return;
    }
    if (reason) { reason.textContent = ''; reason.style.display = 'none'; }

    btn.classList.add('loading');
    const content = btn.querySelector('.btn-content');
    const loader = btn.querySelector('.btn-loader');
    content.style.display = 'none';
    loader.style.display = 'flex';
    
    showProgress('Starting analysis...', 5);
    
    try {
        const progressSteps = [
            [10, 'Parsing job description...', 'Analyzing role requirements'],
            [20, 'Extracting skills & requirements...', 'NLP processing'],
            [30, 'Parsing candidate resumes...', 'Processing resumes'],
            [40, 'Computing skill match scores...', 'Keyword + semantic matching'],
            [50, 'Calculating semantic similarity...', 'Sentence-BERT embeddings'],
            [60, 'Evaluating experience & projects...', 'Depth analysis'],
            [70, 'Analyzing skill gaps & potential...', 'Growth prediction'],
            [80, 'Generating interview questions...', 'AI question generation'],
            [90, 'Running bias-free evaluation...', 'Anonymizing'],
            [95, 'Generating candidate summaries...', 'Finalizing']
        ];
        
        let stepIdx = 0;
        const progressInterval = setInterval(() => {
            if (stepIdx < progressSteps.length) {
                const [pct, label, sublabel] = progressSteps[stepIdx];
                showProgress(label, pct, sublabel);
                stepIdx++;
            }
        }, 800);

        const formData = new FormData();
        if (state.jdFile) formData.append('job_file', state.jdFile);
        else formData.append('job_description', jdText);
        state.resumeFiles.forEach(f => formData.append('resumes', f));
        const w = normalizedWeights();
        if (w) formData.append('weights', JSON.stringify(w));

        const response = await fetch(API_BASE + '/api/analyze', { method: 'POST', body: formData });
        clearInterval(progressInterval);
        showProgress('Processing complete!', 100);
        
        if (!response.ok) {
            let errMsg = 'Analysis failed';
            try { const err = await response.json(); errMsg = err.error || errMsg; } catch (_) {}
            throw new Error(errMsg);
        }

        const text = await response.text();
        if (!text) throw new Error('Empty response from server');
        const data = JSON.parse(text);
        state.currentResults = data;
        state.analysesCount++;
        state.scores = data.ranked_candidates || [];

        document.getElementById('navAnalyzed').textContent = state.analysesCount;
        document.getElementById('heroProcessed').textContent = state.analysesCount;
        state.serverWeights = data.weights_used || null;
        
        // Enable all tabs
        ['tabRankings', 'tabShortlist', 'tabAnalytics', 'tabCopilot', 'tabBias'].forEach(id => {
            const el = document.getElementById(id);
            if (el) { el.style.display = 'inline-flex'; el.disabled = false; }
        });
        enableFeatureTabs();
        syncRerankButton();
        
        // Clear any existing shortlist that doesn't match current candidates
        const currentIds = new Set(data.ranked_candidates.map(c => c.candidate_id));
        state.shortlisted.forEach(id => { if (!currentIds.has(id)) state.shortlisted.delete(id); });
        saveShortlist();
        
        renderResults(data);
        renderAnalytics(data);
        renderShortlist();
        renderBiasReport();
        applyFilters();
        setTimeout(() => {
            hideProgress();
            switchTab('rankings');
            showToast(`✅ Analysis complete! ${data.ranked_candidates.length} candidates ranked across 11 AI modules.`, 'success');
        }, 600);
    } catch (e) {
        hideProgress();
        showToast(`❌ ${e.message}`, 'error');
    } finally {
        btn.classList.remove('loading');
        content.style.display = 'flex';
        loader.style.display = 'none';
    }
}

// ==================== SAMPLE DATA ====================
async function runSample() {
    const btn = document.getElementById('sampleBtn');
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner"></span> Loading sample...';
    showToast('📦 Loading sample dataset...', 'info');
    
    showProgress('Loading sample job description...', 10);

    try {
        const progressSteps = [
            [20, 'Loading candidate resumes...', '5 sample resumes'],
            [35, 'Running AI analysis...', '11 AI modules'],
            [50, 'Computing scores...', '7 dimensions'],
            [65, 'Analyzing skill gaps...', 'Recommendations'],
            [80, 'Generating insights...', 'Potential & bias'],
            [95, 'Finalizing results...', 'Export ready']
        ];
        let stepIdx = 0;
        const progressInterval = setInterval(() => {
            if (stepIdx < progressSteps.length) {
                const [pct, label, sublabel] = progressSteps[stepIdx];
                showProgress(label, pct, sublabel);
                stepIdx++;
            }
        }, 600);

        const response = await fetch(API_BASE + '/api/analyze-sample', { method: 'POST' });
        clearInterval(progressInterval);
        showProgress('Complete!', 100);
        
        if (!response.ok) {
            let errMsg = 'Sample analysis failed';
            try { const err = await response.json(); errMsg = err.error || errMsg; } catch (_) {}
            throw new Error(errMsg);
        }
        const text = await response.text();
        if (!text) throw new Error('Empty response from server');
        const data = JSON.parse(text);
        state.currentResults = data;
        state.analysesCount++;
        state.scores = data.ranked_candidates || [];
        
        document.getElementById('navAnalyzed').textContent = state.analysesCount;
        document.getElementById('heroProcessed').textContent = state.analysesCount;
        state.serverWeights = data.weights_used || null;
        
        ['tabRankings', 'tabShortlist', 'tabAnalytics', 'tabCopilot', 'tabBias'].forEach(id => {
            const el = document.getElementById(id);
            if (el) { el.style.display = 'inline-flex'; el.disabled = false; }
        });
        enableFeatureTabs();
        syncRerankButton();
        
        renderResults(data);
        renderAnalytics(data);
        renderShortlist();
        renderBiasReport();
        applyFilters();
        setTimeout(() => {
            hideProgress();
            switchTab('rankings');
            showToast(`✅ ${data.ranked_candidates.length} candidates ranked! Try the Copilot tab to ask questions.`, 'success');
        }, 600);
    } catch (e) {
        hideProgress();
        showToast(`❌ ${e.message}`, 'error');
    } finally {
        btn.disabled = false;
        btn.innerHTML = '<span class="btn-icon">🎯</span> Try with Sample Data';
    }
}

// ==================== SHORTLIST (localStorage) ====================
function loadShortlist() {
    try {
        const saved = localStorage.getItem('talentrank-shortlist');
        if (saved) {
            state.shortlisted = new Set(JSON.parse(saved));
            document.getElementById('navShortlisted').textContent = state.shortlisted.size;
        }
    } catch (e) {
        state.shortlisted = new Set();
    }
}

function saveShortlist() {
    try {
        localStorage.setItem('talentrank-shortlist', JSON.stringify([...state.shortlisted]));
        document.getElementById('navShortlisted').textContent = state.shortlisted.size;
    } catch (e) {
        // localStorage full or unavailable
    }
}

function toggleShortlist(candidateId) {
    if (state.shortlisted.has(candidateId)) {
        state.shortlisted.delete(candidateId);
        showToast('Removed from shortlist', 'info');
    } else {
        state.shortlisted.add(candidateId);
        showToast('⭐ Added to shortlist', 'success');
    }
    saveShortlist();
    if (state.currentResults) {
        renderResults(state.currentResults);
    }
}

function batchAddToShortlist() {
    const selected = state.selectedCandidates;
    if (selected.size === 0) { showToast('No candidates selected', 'warning'); return; }
    let added = 0;
    selected.forEach(id => {
        if (!state.shortlisted.has(id)) {
            state.shortlisted.add(id);
            added++;
        }
    });
    saveShortlist();
    showToast(`⭐ ${added} candidate(s) shortlisted`, 'success');
    if (state.currentResults) renderResults(state.currentResults);
}

function batchRemoveFromShortlist() {
    const selected = state.selectedCandidates;
    if (selected.size === 0) { showToast('No candidates selected', 'warning'); return; }
    let removed = 0;
    selected.forEach(id => {
        if (state.shortlisted.has(id)) {
            state.shortlisted.delete(id);
            removed++;
        }
    });
    saveShortlist();
    showToast(`🗑️ ${removed} candidate(s) removed from shortlist`, 'info');
    if (state.currentResults) renderResults(state.currentResults);
}

function selectAllCandidates(checkbox) {
    const checked = checkbox.checked;
    document.querySelectorAll('.candidate-checkbox').forEach(cb => {
        cb.checked = checked;
        const id = cb.getAttribute('data-id');
        if (checked) state.selectedCandidates.add(id);
        else state.selectedCandidates.delete(id);
    });
    updateBulkActionsBar();
}

function isShortlisted(candidateId) {
    return state.shortlisted.has(candidateId);
}

function renderShortlist() {
    const tbody = document.getElementById('shortlistBody');
    const meta = document.getElementById('shortlistMeta');
    
    if (!state.currentResults || !state.currentResults.ranked_candidates) {
        tbody.innerHTML = `<tr class="empty-row"><td colspan="9"><div class="empty-state">
            <div class="empty-icon">⭐</div><h3>No shortlisted candidates</h3>
            <p>Star candidates from the Rankings tab to add them here</p></div></td></tr>`;
        return;
    }
    
    const shortlistedCandidates = state.currentResults.ranked_candidates.filter(
        c => state.shortlisted.has(c.candidate_id)
    );
    
    if (shortlistedCandidates.length === 0) {
        tbody.innerHTML = `<tr class="empty-row"><td colspan="9"><div class="empty-state">
            <div class="empty-icon">⭐</div><h3>No shortlisted candidates</h3>
            <p>Star candidates from the Rankings tab to add them here</p></div></td></tr>`;
        meta.textContent = 'Star candidates to add them here';
        return;
    }
    
    meta.textContent = `${shortlistedCandidates.length} candidate(s) shortlisted`;
    
    tbody.innerHTML = shortlistedCandidates.map((c, i) => {
        const rankClass = c.rank === 1 ? 'rank-1' : c.rank === 2 ? 'rank-2' : c.rank === 3 ? 'rank-3' : 'rank-other';
        const scorePct = (c.final_score * 100).toFixed(1);
        const color = c.final_score >= 0.7 ? '#00ff88' : c.final_score >= 0.4 ? '#ffa502' : '#ff4757';
        const potential = c.potential || {};
        const potentialScore = potential.potential_score || 0;

        return `<tr>
            <td><span class="rank-badge ${rankClass}">${c.rank}</span></td>
            <td>
                <div class="candidate-cell">
                    <div class="candidate-avatar-sm" style="background:linear-gradient(135deg,${c.rank===1?'#ffd700':c.rank===2?'#c0c0c0':c.rank===3?'#cd7f32':'#6c63ff'},#00d4ff)">
                        ${c.candidate_name.charAt(0)}
                    </div>
                    <div>
                        <strong>${c.candidate_name}</strong>
                        <small>${c.candidate_id}</small>
                    </div>
                </div>
            </td>
            <td><span style="color:${color};font-weight:700;font-size:1.1rem">${scorePct}%</span></td>
            <td><div class="score-bar-bg"><div class="score-bar-fill" style="width:${c.scores.skill_match*100}%;background:linear-gradient(90deg,#6c63ff,#00d4ff)"></div></div></td>
            <td><div class="score-bar-bg"><div class="score-bar-fill" style="width:${c.scores.experience_match*100}%;background:linear-gradient(90deg,#00d4ff,#00ff88)"></div></div></td>
            <td><div class="score-bar-bg"><div class="score-bar-fill" style="width:${c.scores.semantic_similarity*100}%;background:linear-gradient(90deg,#a855f7,#ec4899)"></div></div></td>
            <td><span class="reason-text" title="${c.reason||''}">${(c.reason||'').substring(0,35)}${(c.reason||'').length>35?'...':''}</span></td>
            <td><span class="potential-badge ${potentialScore>=70?'high':potentialScore>=40?'medium':'low'}">${potentialScore.toFixed(0)}%</span></td>
            <td>
                <div class="action-btns">
                    <button class="btn-sm" onclick="showCandidateDetail(${state.currentResults.ranked_candidates.indexOf(c)})" title="View Profile">👤</button>
                    <button class="btn-sm active" onclick="toggleShortlist('${c.candidate_id}')" title="Remove from shortlist">⭐</button>
                </div>
            </td>
        </tr>`;
    }).join('');
}

function clearShortlist() {
    if (state.shortlisted.size === 0) return;
    if (!confirm('Clear all shortlisted candidates?')) return;
    state.shortlisted = new Set();
    saveShortlist();
    renderShortlist();
    if (state.currentResults) renderResults(state.currentResults);
    showToast('🗑️ Shortlist cleared', 'info');
}

function exportShortlist() {
    if (!state.currentResults || !state.currentResults.ranked_candidates) {
        showToast('No data to export', 'warning');
        return;
    }
    const shortlisted = state.currentResults.ranked_candidates.filter(
        c => state.shortlisted.has(c.candidate_id)
    );
    if (shortlisted.length === 0) {
        showToast('No shortlisted candidates to export', 'warning');
        return;
    }
    
    const data = {
        exported_at: new Date().toISOString(),
        total: shortlisted.length,
        title: 'Shortlist Export',
        candidates: shortlisted.map(c => ({
            rank: c.rank,
            name: c.candidate_name,
            score: c.final_score,
            scores: c.scores,
            summary: c.candidate_summary,
            potential: c.potential,
            skill_gaps: c.skill_gaps
        }))
    };
    
    downloadJSON(data, `shortlist_${Date.now()}.json`);
    showToast('📤 Shortlist exported!', 'success');
}

// ==================== FILTERS & SORTING ====================
function candidateById(id) {
    const list = (state.currentResults && state.currentResults.ranked_candidates) || [];
    return list.find(c => c.candidate_id === id) || null;
}

function applyFilters() {
    if (!state.currentResults) return;
    
    const nameFilter = (document.getElementById('filterName').value || '').toLowerCase();
    const scoreFilter = document.getElementById('filterScoreRange').value;
    const expFilter = document.getElementById('filterExperience').value;
    const shortlistFilter = document.getElementById('filterShortlist').value;
    const candidatesData = state.currentResults.ranked_candidates || [];
    
    // Rows are looked up by their data-candidate-id, NOT by DOM position, so
    // filtering still targets the right candidate after a column sort.
    const rows = document.querySelectorAll('#rankingBody tr:not(.empty-row)');
    let visibleCount = 0;
    
    rows.forEach(row => {
        const candidate = candidateById(row.dataset.candidateId);
        if (!candidate) { row.style.display = 'none'; return; }
        
        let show = true;
        const name = (candidate.candidate_name || '').toLowerCase();
        const score = (candidate.final_score || 0) * 100;
        const expYears = (candidate.profile && candidate.profile.experience_years) || 0;
        const isStarred = state.shortlisted.has(candidate.candidate_id);
        
        if (nameFilter && !name.includes(nameFilter)) show = false;
        if (scoreFilter === 'excellent' && score < 80) show = false;
        if (scoreFilter === 'good' && (score < 60 || score >= 80)) show = false;
        if (scoreFilter === 'moderate' && (score < 40 || score >= 60)) show = false;
        if (scoreFilter === 'low' && score >= 40) show = false;
        
        if (expFilter === 'senior' && expYears < 7) show = false;
        if (expFilter === 'mid' && (expYears < 3 || expYears > 6)) show = false;
        if (expFilter === 'junior' && (expYears < 1 || expYears > 2)) show = false;
        if (expFilter === 'entry' && expYears >= 1) show = false;
        
        if (shortlistFilter === 'shortlisted' && !isStarred) show = false;
        if (shortlistFilter === 'not' && isStarred) show = false;
        
        row.style.display = show ? '' : 'none';
        if (show) visibleCount++;
    });
    
    const meta = document.getElementById('resultsMeta');
    if (meta) {
        const total = candidatesData.length;
        meta.textContent = visibleCount === total
            ? `Found ${total} candidates`
            : `Showing ${visibleCount} of ${total} candidates`;
    }
    updateFilterBadge(visibleCount, candidatesData.length);
}

function updateFilterBadge(visible, total) {
    const badge = document.getElementById('filterBadge');
    if (!badge) return;
    if (visible < total) {
        badge.textContent = `${visible}/${total}`;
        badge.style.display = '';
    } else {
        badge.style.display = 'none';
    }
}

function clearFilters() {
    document.getElementById('filterName').value = '';
    document.getElementById('filterScoreRange').value = 'all';
    document.getElementById('filterExperience').value = 'all';
    document.getElementById('filterShortlist').value = 'all';
    applyFilters();
}

let sortState = { field: 'rank', asc: true };

function sortBy(field) {
    if (sortState.field === field) {
        sortState.asc = !sortState.asc;
    } else {
        sortState.field = field;
        sortState.asc = true;
    }
    
    document.querySelectorAll('.ranking-table th').forEach(th => {
        const icon = th.querySelector('.sort-icon');
        if (!icon) return;
        icon.textContent = '↕';
        icon.style.opacity = '0.3';
        th.removeAttribute('aria-sort');
    });
    const colIndex = field === 'rank' ? 2 : field === 'name' ? 3 : field === 'score' ? 4 : 3;
    const activeHeader = document.querySelector(`.ranking-table th:nth-child(${colIndex})`);
    if (activeHeader) {
        const icon = activeHeader.querySelector('.sort-icon');
        if (icon) {
            icon.textContent = sortState.asc ? '↑' : '↓';
            icon.style.opacity = '1';
        }
        activeHeader.setAttribute('aria-sort', sortState.asc ? 'ascending' : 'descending');
    }

    const indicator = document.getElementById('sortIndicator');
    if (indicator) {
        const label = { rank: 'Rank', name: 'Name', score: 'AI Match' }[field] || 'Rank';
        indicator.textContent = `Sort: ${label} ${sortState.asc ? '↑' : '↓'}`;
    }
    
    const tbody = document.getElementById('rankingBody');
    const rows = Array.from(tbody.querySelectorAll('tr:not(.empty-row)'));
    if (rows.length === 0) return;
    
    rows.sort((a, b) => {
        let aVal, bVal;
        switch(field) {
            case 'rank':
                aVal = parseInt(a.querySelector('td:nth-child(2) .rank-badge')?.textContent || '0');
                bVal = parseInt(b.querySelector('td:nth-child(2) .rank-badge')?.textContent || '0');
                break;
            case 'name':
                aVal = (a.querySelector('td:nth-child(3) .candidate-cell strong')?.textContent || '').toLowerCase();
                bVal = (b.querySelector('td:nth-child(3) .candidate-cell strong')?.textContent || '').toLowerCase();
                return sortState.asc ? aVal.localeCompare(bVal) : bVal.localeCompare(aVal);
            case 'score':
                aVal = parseFloat(a.querySelector('td:nth-child(4) span')?.textContent || '0');
                bVal = parseFloat(b.querySelector('td:nth-child(4) span')?.textContent || '0');
                break;
            default:
                aVal = 0; bVal = 0;
        }
        return sortState.asc ? aVal - bVal : bVal - aVal;
    });
    
    rows.forEach(row => tbody.appendChild(row));
    
    // Sorting re-orders the DOM, so re-apply active filters to the new order.
    applyFilters();
}

// ==================== RENDER RESULTS ====================
function renderResults(data) {
    if (!data) return;
    const candidates = data.ranked_candidates;
    if (!candidates || candidates.length === 0) return;
    
    const top = candidates[0];
    const total = candidates.length;
    const avgScore = candidates.reduce((s, c) => s + c.final_score, 0) / total;
    const topScorePct = (top.final_score * 100).toFixed(1);
    const avgScorePct = (avgScore * 100).toFixed(1);

    document.getElementById('resultsMeta').textContent = 
        `Found ${total} candidates • Top: ${topScorePct}% • ${top.candidate_name}`;
    document.getElementById('totalCandidates').textContent = total;
    document.getElementById('topScore').textContent = `${topScorePct}%`;
    document.getElementById('avgScore').textContent = `${avgScorePct}%`;
    document.getElementById('topCandidate').textContent = top.candidate_name;
    document.getElementById('analysisTime').textContent = `Processed ${new Date().toLocaleTimeString()}`;

    // Table
    const tbody = document.getElementById('rankingBody');
    tbody.innerHTML = candidates.map((c, i) => {
        const rankClass = i === 0 ? 'rank-1' : i === 1 ? 'rank-2' : i === 2 ? 'rank-3' : 'rank-other';
        const scorePct = (c.final_score * 100).toFixed(1);
        const color = c.final_score >= 0.7 ? '#00ff88' : c.final_score >= 0.4 ? '#ffa502' : '#ff4757';
        const potential = c.potential || {};
        const potentialScore = potential.potential_score || 0;
        const shortlisted = state.shortlisted.has(c.candidate_id);
        const reason = c.reason || '';
        const reasonShort = reason.length > 35 ? reason.substring(0, 35) + '...' : reason;

        return `<tr class="${shortlisted ? 'shortlisted' : ''}" data-candidate-id="${c.candidate_id}" data-candidate-index="${i}">
            <td class="checkbox-cell"><input type="checkbox" class="candidate-checkbox" data-id="${c.candidate_id}" onchange="toggleSelect(this)"></td>
            <td><span class="rank-badge ${rankClass}">${c.rank}</span></td>
            <td>
                <div class="candidate-cell">
                    <div class="candidate-avatar-sm" style="background:linear-gradient(135deg,${c.rank===1?'#ffd700':c.rank===2?'#c0c0c0':c.rank===3?'#cd7f32':'#6c63ff'},#00d4ff)">
                        ${(c.candidate_name || '?').charAt(0)}
                    </div>
                    <div>
                        <strong>${c.candidate_name}</strong>
                        <small>${c.candidate_id}</small>
                    </div>
                </div>
            </td>
            <td><span style="color:${color};font-weight:700;font-size:1.1rem">${scorePct}%</span></td>
            <td><div class="score-bar-bg"><div class="score-bar-fill" style="width:${(c.scores.skill_match||0)*100}%;background:linear-gradient(90deg,#6c63ff,#00d4ff)"></div></div></td>
            <td><div class="score-bar-bg"><div class="score-bar-fill" style="width:${(c.scores.experience_match||0)*100}%;background:linear-gradient(90deg,#00d4ff,#00ff88)"></div></div></td>
            <td><div class="score-bar-bg"><div class="score-bar-fill" style="width:${(c.scores.semantic_similarity||0)*100}%;background:linear-gradient(90deg,#a855f7,#ec4899)"></div></div></td>
            <td><span class="reason-text" title="${reason.replace(/"/g, '"')}">${reasonShort}</span></td>
            <td><span class="potential-badge ${potentialScore>=70?'high':potentialScore>=40?'medium':'low'}">${potentialScore.toFixed(0)}%</span></td>
            <td><span class="shortlist-star ${shortlisted ? 'active' : ''}" onclick="toggleShortlist('${c.candidate_id}')" title="${shortlisted ? 'Remove from shortlist' : 'Add to shortlist'}">${shortlisted ? '⭐' : '☆'}</span></td>
            <td>
                <div class="action-btns">
                    <button class="btn-sm" onclick="showCandidateDetail(${i})" title="View Profile">👤</button>
                    <button class="btn-sm" onclick="showInterviewQuestions(${i})" title="Interview Questions">🎯</button>
                    <button class="btn-sm" onclick="compareWith(${i})" title="Compare">⚖️</button>
                </div>
            </td>
        </tr>`;
    }).join('');

    updateScoreChart(candidates);
    renderWordCloud(candidates);
}

// ==================== SELECTION ====================
function toggleSelect(checkbox) {
    const id = checkbox.getAttribute('data-id');
    if (checkbox.checked) {
        state.selectedCandidates.add(id);
    } else {
        state.selectedCandidates.delete(id);
    }
    updateBulkActionsBar();
}

function updateBulkActionsBar() {
    let bar = document.getElementById('bulkActionsBar');
    const count = state.selectedCandidates.size;
    
    if (count === 0) {
        if (bar) bar.remove();
        return;
    }
    
    if (!bar) {
        bar = document.createElement('div');
        bar.id = 'bulkActionsBar';
        bar.className = 'bulk-actions-bar';
        const filterBar = document.querySelector('.filters-bar');
        if (filterBar) filterBar.after(bar);
        else {
            const tableSection = document.querySelector('.table-section');
            if (tableSection) tableSection.before(bar);
        }
    }
    
    bar.innerHTML = `
        <span class="selected-count">✅ ${count} selected</span>
        <button class="bulk-btn" onclick="batchAddToShortlist()">⭐ Add to Shortlist</button>
        <button class="bulk-btn" onclick="batchRemoveFromShortlist()">🗑️ Remove from Shortlist</button>
        <button class="bulk-btn" onclick="batchExportSelected()">📤 Export Selected</button>
        <button class="bulk-btn danger" onclick="deselectAll()">✕ Deselect All</button>
    `;
}

function deselectAll() {
    state.selectedCandidates.clear();
    document.querySelectorAll('.candidate-checkbox').forEach(cb => cb.checked = false);
    document.querySelectorAll('.select-all-checkbox').forEach(cb => cb.checked = false);
    updateBulkActionsBar();
}

function batchExportSelected() {
    if (!state.currentResults || !state.currentResults.ranked_candidates) return;
    const selected = state.currentResults.ranked_candidates.filter(
        c => state.selectedCandidates.has(c.candidate_id)
    );
    if (selected.length === 0) { showToast('No candidates selected', 'warning'); return; }
    
    const data = {
        exported_at: new Date().toISOString(),
        total: selected.length,
        title: 'Selected Candidates Export',
        candidates: selected.map(c => ({
            rank: c.rank,
            name: c.candidate_name,
            score: c.final_score,
            scores: c.scores,
            summary: c.candidate_summary,
            potential: c.potential,
            skill_gaps: c.skill_gaps
        }))
    };
    
    downloadJSON(data, `selected_candidates_${Date.now()}.json`);
    showToast(`📤 ${selected.length} candidate(s) exported`, 'success');
}

// ==================== SCORE CHART ====================
function updateScoreChart(candidates) {
    if (!chartAvailable()) { showChartUnavailable(document.querySelector('canvas')); return; }
    // FIXED: Check multiple possible canvas IDs
    let canvas = document.getElementById('scoreChart');
    
    // If scoreChart canvas doesn't exist, create one in rankings tab
    if (!canvas) {
        const tableSection = document.querySelector('.table-section');
        if (tableSection && candidates && candidates.length > 0) {
            const chartContainer = document.createElement('div');
            chartContainer.className = 'chart-section glass';
            chartContainer.id = 'scoreChartContainer';
            chartContainer.style.marginBottom = '1.5rem';
            chartContainer.innerHTML = `
                <div class="chart-header">
                    <h3>📊 Candidate Score Breakdown</h3>
                    <div class="chart-toggles">
                        <button class="chart-toggle active" onclick="switchChart('radar', this)">Radar</button>
                        <button class="chart-toggle" onclick="switchChart('bar', this)">Bar</button>
                    </div>
                </div>
                <div class="chart-container" style="height:300px">
                    <canvas id="scoreChart"></canvas>
                </div>
            `;
            tableSection.parentElement.insertBefore(chartContainer, tableSection);
            canvas = document.getElementById('scoreChart');
        }
    }
    
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (state.chart) state.chart.destroy();

    const labels = candidates.slice(0, 10).map(c => {
        const name = c.candidate_name || '';
        return name.split(' ')[0] || 'Candidate';
    });
    
    const datasets = state.chartType === 'radar' ? [
        { label: 'Skill', data: candidates.slice(0, 10).map(c => (c.scores.skill_match||0) * 100), borderColor: '#6c63ff', backgroundColor: 'rgba(108,99,255,0.1)' },
        { label: 'Experience', data: candidates.slice(0, 10).map(c => (c.scores.experience_match||0) * 100), borderColor: '#00d4ff', backgroundColor: 'rgba(0,212,255,0.1)' },
        { label: 'Semantic', data: candidates.slice(0, 10).map(c => (c.scores.semantic_similarity||0) * 100), borderColor: '#a855f7', backgroundColor: 'rgba(168,85,247,0.1)' },
        { label: 'Projects', data: candidates.slice(0, 10).map(c => (c.scores.project_relevance||0) * 100), borderColor: '#00ff88', backgroundColor: 'rgba(0,255,136,0.1)' }
    ] : [
        { label: 'Scores', data: candidates.slice(0, 10).map(c => c.final_score * 100), backgroundColor: 'rgba(108,99,255,0.7)', borderColor: '#6c63ff', borderWidth: 1 }
    ];

    state.chart = new Chart(ctx, {
        type: state.chartType,
        data: { labels, datasets },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { labels: { color: '#aaa', font: { size: 11 } } },
                tooltip: { backgroundColor: 'rgba(0,0,0,0.8)', titleColor: '#fff', bodyColor: '#ddd' }
            },
            scales: state.chartType === 'radar' ? {
                r: { angleLines: { color: 'rgba(255,255,255,0.1)' }, grid: { color: 'rgba(255,255,255,0.1)' }, pointLabels: { color: '#aaa', font: { size: 10 } }, ticks: { display: false } }
            } : {
                y: { beginAtZero: true, max: 100, grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#888' } },
                x: { grid: { display: false }, ticks: { color: '#aaa', font: { size: 10 } } }
            }
        }
    });
}

function switchChart(type, btn) {
    state.chartType = type;
    const toggles = document.querySelectorAll('#scoreChartContainer .chart-toggle');
    toggles.forEach(b => b.classList.remove('active'));
    if (btn) btn.classList.add('active');
    if (state.currentResults && state.currentResults.ranked_candidates) {
        updateScoreChart(state.currentResults.ranked_candidates);
    }
}

// ==================== FILTER TABLE (delegates to unified filter bar) ====================
// The header previously had a second search box that reset row visibility and
// clobbered the filter bar. It now simply re-applies the active filters.
function filterTable() {
    applyFilters();
}

// ==================== CANDIDATE DETAIL MODAL ====================
function showCandidateDetail(index) {
    const data = state.currentResults;
    if (!data || !data.ranked_candidates || !data.ranked_candidates[index]) return;

    const c = data.ranked_candidates[index];
    const modal = document.getElementById('candidateModal');
    const body = document.getElementById('modalBody');

    // Weights shown are the ones actually in effect for the current results
    // (server-normalised from the last run), falling back to the defaults.
    const W = (c.scores && c.scores.weights) || activeWeights();
    const wpct = k => `${Math.round((W[k] || 0) * 100)}%`;

    const scores = [
        { label: 'Skill Match', value: c.scores.skill_match || 0, weight: wpct('skill_match') },
        { label: 'Experience Match', value: c.scores.experience_match || 0, weight: wpct('experience_match') },
        { label: 'Project Relevance', value: c.scores.project_relevance || 0, weight: wpct('project_relevance') },
        { label: 'Semantic Similarity', value: c.scores.semantic_similarity || 0, weight: wpct('semantic_similarity') },
        { label: 'Education', value: c.scores.education || 0, weight: wpct('education') },
        { label: 'Certifications', value: c.scores.certifications || 0, weight: wpct('certifications') },
        { label: 'Soft Skills', value: c.scores.behavioral_score || 0, weight: wpct('behavioral_score') }
    ];

    const skills = (c.profile && c.profile.technical_skills || []).map(s => `<span class="skill-tag">${s}</span>`).join('');
    const softSkills = (c.profile && c.profile.soft_skills || []).map(s => `<span class="skill-tag soft">${s}</span>`).join('');
    
    const potential = c.potential || {};
    const skillGaps = c.skill_gaps || {};
    const predictedSkills = potential.predicted_future_skills || [];

    body.innerHTML = `
        <div class="detail-header">
            <div class="detail-avatar">${(c.candidate_name || '?').charAt(0)}</div>
            <div class="detail-info">
                <h2>${c.candidate_name}</h2>
                <span class="rank-tag">🏆 Rank #${c.rank} — ${(c.final_score * 100).toFixed(1)}% Match</span>
                <p class="detail-id">${c.candidate_id} • ${(c.profile && c.profile.experience_years) || 0} years experience • ${(c.profile && c.profile.completeness_score * 100).toFixed(0)}% profile completeness</p>
            </div>
        </div>

        <div class="detail-section">
            <h4>📊 Score Breakdown</h4>
            <div class="score-list">
                ${scores.map(s => `
                    <div class="score-row-modern">
                        <div class="score-row-header">
                            <span>${s.label}</span>
                            <small>(${s.weight})</small>
                            <span class="score-val">${(s.value * 100).toFixed(0)}%</span>
                        </div>
                        <div class="score-bar-track">
                            <div class="score-bar-progress ${s.value >= 0.7 ? 'high' : s.value >= 0.4 ? 'medium' : 'low'}" style="width:${s.value * 100}%"></div>
                        </div>
                    </div>
                `).join('')}
            </div>
        </div>

        <div class="detail-section reason-section">
            <h4>💡 Why This Candidate?</h4>
            <p>${c.reason || 'No detailed reasoning available.'}</p>
        </div>

        <div class="detail-section">
            <h4>🤖 AI Candidate Summary</h4>
            <p style="background:var(--glass-bg);padding:1rem;border-radius:8px;border:1px solid var(--glass-border)">
                ${c.candidate_summary || 'No summary generated.'}
            </p>
        </div>

        ${skills ? `<div class="detail-section"><h4>🔧 Technical Skills (${(c.profile && c.profile.technical_skills && c.profile.technical_skills.length) || 0})</h4><div class="skills-grid">${skills}</div></div>` : ''}
        ${softSkills ? `<div class="detail-section"><h4>🤝 Soft Skills</h4><div class="skills-grid">${softSkills}</div></div>` : ''}

        ${c.profile && c.profile.certifications && c.profile.certifications.length > 0 ? `
            <div class="detail-section"><h4>📜 Certifications</h4><p>${c.profile.certifications.join(', ')}</p></div>
        ` : ''}

        <!-- Hiring Prediction Meter -->
        <div class="detail-section">
            <h4>🎯 Hiring Success Prediction</h4>
            <div class="hiring-meter">
                <span class="hiring-meter-label">Hire Confidence</span>
                <div class="hiring-meter-bar">
                    <div class="hiring-meter-fill" style="width:${Math.min(c.final_score * 100, 100)}%"></div>
                </div>
                <span class="hiring-meter-value" style="color:${c.final_score >= 0.7 ? '#00ff88' : c.final_score >= 0.4 ? '#ffa502' : '#ff4757'}">${(c.final_score * 100).toFixed(0)}%</span>
            </div>
        </div>

        <div class="detail-section">
            <h4>🚀 Potential Score: ${(potential.potential_score || 0).toFixed(0)}%</h4>
            <p>${potential.explanation || ''}</p>
            ${predictedSkills.length > 0 ? `
                <div style="margin-top:8px">
                    <small style="color:var(--text-muted)">Predicted future skills:</small>
                    <div class="skills-grid" style="margin-top:4px">
                        ${predictedSkills.map(s => `<span class="skill-tag" style="background:rgba(0,212,255,0.1);border-color:rgba(0,212,255,0.2);color:var(--accent-2)">${s}</span>`).join('')}
                    </div>
                </div>
            ` : ''}
        </div>

        ${skillGaps.strengths && skillGaps.strengths.length > 0 ? `
            <div class="detail-section">
                <h4>✅ Strengths (${skillGaps.strengths.length} matched)</h4>
                <div class="skills-grid">${skillGaps.strengths.map(s => `<span class="skill-tag" style="background:rgba(0,255,136,0.1);border-color:rgba(0,255,136,0.2);color:var(--success)">${s}</span>`).join('')}</div>
            </div>
        ` : ''}
        ${skillGaps.missing_required_skills && skillGaps.missing_required_skills.length > 0 ? `
            <div class="detail-section">
                <h4>⚠️ Missing Required Skills (${skillGaps.missing_required_skills.length})</h4>
                <div class="skills-grid">${skillGaps.missing_required_skills.map(s => `<span class="skill-tag" style="background:rgba(255,71,87,0.1);border-color:rgba(255,71,87,0.2);color:var(--danger)">${s}</span>`).join('')}</div>
            </div>
        ` : ''}
        ${skillGaps.learning_recommendations && skillGaps.learning_recommendations.length > 0 ? `
            <div class="detail-section">
                <h4>📚 Learning Recommendations</h4>
                <ul style="color:var(--text-secondary);font-size:0.85rem;line-height:1.8">
                    ${skillGaps.learning_recommendations.slice(0, 3).map(r => `<li>${r.recommendation || `Learn ${r.skill}`}</li>`).join('')}
                </ul>
            </div>
        ` : ''}

        <div class="detail-section">
            <h4>⚖️ Bias-Free Evaluation</h4>
            <p>✅ Anonymized evaluation performed — ${((c.bias_free && c.bias_free.fairness_score) || 0).toFixed(0)}% fairness score</p>
        </div>
        
        <div class="detail-section" style="display:flex;gap:8px;flex-wrap:wrap">
            <button class="btn-outline" onclick="toggleShortlist('${c.candidate_id}'); closeModal(); showToast('${state.shortlisted.has(c.candidate_id) ? 'Removed from' : 'Added to'} shortlist', '${state.shortlisted.has(c.candidate_id) ? 'info' : 'success'}')">
                ${state.shortlisted.has(c.candidate_id) ? '⭐ Remove from Shortlist' : '☆ Add to Shortlist'}
            </button>
            <button class="btn-outline" onclick="showInterviewQuestions(${index})">🎯 View Interview Questions</button>
        </div>
    `;

    modal.classList.add('active');
    // Animate the hiring meter
    setTimeout(() => {
        const fill = body.querySelector('.hiring-meter-fill');
        if (fill) fill.style.width = '0%';
        setTimeout(() => {
            if (fill) fill.style.width = `${Math.min(c.final_score * 100, 100)}%`;
        }, 50);
    }, 100);
}

function closeModal() {
    document.getElementById('candidateModal').classList.remove('active');
}

document.getElementById('candidateModal').addEventListener('click', (e) => {
    if (e.target === e.currentTarget) closeModal();
});
document.getElementById('compareModal').addEventListener('click', (e) => {
    if (e.target === e.currentTarget) closeCompareModal();
});
document.getElementById('interviewModal').addEventListener('click', (e) => {
    if (e.target === e.currentTarget) closeInterviewModal();
});

// ==================== INTERVIEW QUESTIONS ====================
function showInterviewQuestions(index) {
    const data = state.currentResults;
    if (!data || !data.ranked_candidates || !data.ranked_candidates[index]) return;

    const c = data.ranked_candidates[index];
    const modal = document.getElementById('interviewModal');
    const body = document.getElementById('interviewBody');
    const questions = c.interview_questions || { all_questions: [] };

    body.innerHTML = `
        <div class="interview-header">
            <h3>${c.candidate_name} — ${questions.total_count || 0} Questions</h3>
            <p style="color:var(--text-muted);font-size:0.8rem">Tailored based on job requirements, candidate profile, and skill gaps</p>
        </div>
        <div class="interview-categories">
            ${Object.entries(questions.categorized || {}).map(([cat, qs]) => {
                if (!qs || qs.length === 0) return '';
                return `
                    <div class="interview-category">
                        <h4>${cat.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())} (${qs.length})</h4>
                        <div class="interview-questions">
                            ${qs.map(q => `
                                <div class="interview-question">
                                    <div class="question-text">${q.question || ''}</div>
                                    <div class="question-meta">
                                        <span class="question-focus">${q.focus || 'General'}</span>
                                        <span class="question-difficulty ${q.difficulty || 'intermediate'}">${q.difficulty || 'intermediate'}</span>
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                `;
            }).join('')}
        </div>
        ${(!questions.all_questions || questions.all_questions.length === 0) ? '<p class="empty-hint">No interview questions generated for this candidate.</p>' : ''}
    `;

    modal.classList.add('active');
}

function closeInterviewModal() {
    document.getElementById('interviewModal').classList.remove('active');
}

// ==================== COMPARE ====================
function compareWith(index) {
    const data = state.currentResults;
    if (!data || !data.ranked_candidates || !data.ranked_candidates[index]) return;

    state.compareQueue.push(index);
    
    if (state.compareQueue.length === 2) {
        const [i1, i2] = state.compareQueue;
        state.compareQueue = [];
        showComparison(i1, i2);
    } else {
        const c = data.ranked_candidates[index];
        showToast(`Click ⚖️ on another candidate to compare with ${c.candidate_name}`, 'info');
    }
}

async function showComparison(index1, index2) {
    const modal = document.getElementById('compareModal');
    const grid = document.getElementById('compareGrid');
    
    // Show loading
    grid.innerHTML = '<p class="empty-hint" style="text-align:center">Loading comparison... <span class="spinner" style="margin-left:8px"></span></p>';
    modal.classList.add('active');
    
    try {
        const res = await fetch(API_BASE + '/api/compare', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ index1, index2 })
        });
        const data = await res.json();
        
        grid.innerHTML = `
            <div class="compare-header-row">
                <div class="compare-card ${data.candidate_1.score > data.candidate_2.score ? 'winner' : ''}">
                    <div class="compare-avatar">${(data.candidate_1.name || '?').charAt(0)}</div>
                    <h4>${data.candidate_1.name}</h4>
                    <div class="compare-score">Rank #${data.candidate_1.rank}</div>
                    <div class="compare-score-value">${(data.candidate_1.score * 100).toFixed(1)}%</div>
                    ${data.candidate_1.score > data.candidate_2.score ? '<div class="compare-badge">🏆 Leader</div>' : ''}
                </div>
                <div class="compare-vs">VS</div>
                <div class="compare-card ${data.candidate_2.score > data.candidate_1.score ? 'winner' : ''}">
                    <div class="compare-avatar">${(data.candidate_2.name || '?').charAt(0)}</div>
                    <h4>${data.candidate_2.name}</h4>
                    <div class="compare-score">Rank #${data.candidate_2.rank}</div>
                    <div class="compare-score-value">${(data.candidate_2.score * 100).toFixed(1)}%</div>
                    ${data.candidate_2.score > data.candidate_1.score ? '<div class="compare-badge">🏆 Leader</div>' : ''}
                </div>
            </div>
            <div class="compare-details">
                <h4>Score Differences</h4>
                <div class="compare-diff-grid">
                    ${renderDiffRow('Overall', data.differences.score_diff)}
                    ${renderDiffRow('Skills', data.differences.skill_diff)}
                    ${renderDiffRow('Experience', data.differences.experience_diff)}
                    ${renderDiffRow('Semantic', data.differences.semantic_diff)}
                </div>
                <div class="compare-summaries">
                    <div class="compare-summary">
                        <h5>${data.candidate_1.name}</h5>
                        <p>${data.candidate_1.summary || 'No summary available'}</p>
                    </div>
                    <div class="compare-summary">
                        <h5>${data.candidate_2.name}</h5>
                        <p>${data.candidate_2.summary || 'No summary available'}</p>
                    </div>
                </div>
            </div>
        `;
    } catch (e) {
        grid.innerHTML = `<p class="empty-hint" style="text-align:center">Error loading comparison: ${e.message}</p>`;
    }
}

function renderDiffRow(label, diff) {
    if (diff === undefined || diff === null) return '';
    const pct = Math.min(Math.abs(diff), 100);
    return `
        <div class="diff-row">
            <span>${label}</span>
            <div class="diff-bar-container">
                <div class="diff-bar ${diff >= 0 ? 'positive' : 'negative'}" style="width:${pct}%">
                    ${diff >= 0 ? '+' : ''}${diff.toFixed(1)}%
                </div>
            </div>
        </div>
    `;
}

function closeCompareModal() {
    document.getElementById('compareModal').classList.remove('active');
    state.compareQueue = [];
}

// ==================== WORD CLOUD ====================
function renderWordCloud(candidates) {
    const container = document.getElementById('wordCloudContainer');
    if (!container) return;
    
    if (!candidates || candidates.length === 0) {
        container.innerHTML = '<p class="empty-hint">No candidate data available</p>';
        return;
    }
    
    const skillCounts = {};
    candidates.forEach(c => {
        const skills = (c.profile && c.profile.technical_skills) || [];
        skills.forEach(s => {
            const key = s.toLowerCase().trim();
            if (key) skillCounts[key] = (skillCounts[key] || 0) + 1;
        });
    });
    
    const entries = Object.entries(skillCounts).sort((a, b) => b[1] - a[1]);
    
    if (entries.length === 0) {
        container.innerHTML = '<p class="empty-hint">No skills extracted from candidates</p>';
        return;
    }
    
    const maxCount = entries[0][1];
    const minCount = entries[entries.length - 1][1];
    
    const colors = ['#6c63ff', '#00d4ff', '#00ff88', '#a855f7', '#ec4899', '#ffa502', '#ff4757', '#4ade80', '#38bdf8', '#f472b6'];
    
    container.innerHTML = entries.map(([skill, count], i) => {
        const size = 0.7 + ((count - minCount) / (maxCount - minCount || 1)) * 1.3;
        const fontSize = `${0.7 + size * 0.5}rem`;
        const opacity = 0.5 + (count / maxCount) * 0.5;
        const color = colors[i % colors.length];
        
        return `<span class="word-cloud-item" style="font-size:${fontSize};color:${color};opacity:${opacity}" title="${skill}: ${count} candidate(s)">${skill}</span>`;
    }).join('');
}

// ==================== SCORING WEIGHTS CONFIGURATOR ====================
const DEFAULT_WEIGHTS = {
    skill_match: { label: 'Skill Match', weight: 0.35, default: 0.35 },
    experience_match: { label: 'Experience', weight: 0.20, default: 0.20 },
    project_relevance: { label: 'Projects', weight: 0.15, default: 0.15 },
    semantic_similarity: { label: 'Semantic Fit', weight: 0.15, default: 0.15 },
    education: { label: 'Education', weight: 0.05, default: 0.05 },
    certifications: { label: 'Certifications', weight: 0.05, default: 0.05 },
    behavioral_score: { label: 'Soft Skills', weight: 0.05, default: 0.05 }
};

function initWeightsConfig() {
    const container = document.getElementById('weightsConfig');
    if (!container) return;
    
    // FIXED: Don't duplicate - only initialize once
    if (state.weightsInitialized) return;
    
    // Remove default Reset button and add sliders
    const defaultReset = container.querySelector('.btn-outline');
    if (defaultReset) defaultReset.remove();
    
    const weights = state.customWeights || { ...DEFAULT_WEIGHTS };
    let html = '';
    
    Object.entries(weights).forEach(([key, config]) => {
        html += `
            <div class="weight-row">
                <span class="weight-label">${config.label}</span>
                <input type="range" class="weight-slider" min="0" max="0.50" step="0.01" value="${config.weight}" 
                    oninput="updateWeight('${key}', this.value)" id="weight-${key}">
                <span class="weight-value" id="weightVal-${key}">${(config.weight * 100).toFixed(0)}%</span>
            </div>
        `;
    });
    
    html += `
        <div style="margin-top:1rem;padding:0.5rem;background:var(--bg-secondary);border-radius:var(--radius-sm);text-align:center">
            <span style="font-size:0.85rem;color:var(--text-muted)">Total: </span>
            <span style="font-size:1rem;font-weight:700;color:var(--accent-2)" id="weightTotal">
                ${Object.values(weights).reduce((s, w) => s + w.weight, 0) * 100}%
            </span>
            <span style="font-size:0.75rem;color:var(--text-muted);margin-left:8px">(must equal 100%)</span>
        </div>
    `;
    
    container.innerHTML += html;
    state.weightsInitialized = true;
}

function updateWeight(key, value) {
    const val = parseFloat(value);
    if (!state.customWeights) {
        state.customWeights = JSON.parse(JSON.stringify(DEFAULT_WEIGHTS));
    }
    state.customWeights[key].weight = val;
    const valEl = document.getElementById(`weightVal-${key}`);
    if (valEl) valEl.textContent = `${(val * 100).toFixed(0)}%`;
    
    const total = Object.values(state.customWeights).reduce((s, w) => s + w.weight, 0);
    const totalEl = document.getElementById('weightTotal');
    if (totalEl) {
        totalEl.textContent = `${(total * 100).toFixed(0)}%`;
        totalEl.style.color = Math.abs(total - 1.0) < 0.01 ? 'var(--success)' : 'var(--danger)';
    }
}

function resetWeights() {
    state.customWeights = null;
    state.weightsInitialized = false;
    Object.entries(DEFAULT_WEIGHTS).forEach(([key, config]) => {
        const slider = document.getElementById(`weight-${key}`);
        if (slider) {
            slider.value = config.default;
            const valEl = document.getElementById(`weightVal-${key}`);
            if (valEl) valEl.textContent = `${(config.default * 100).toFixed(0)}%`;
        }
    });
    const totalEl = document.getElementById('weightTotal');
    if (totalEl) {
        totalEl.textContent = '100%';
        totalEl.style.color = 'var(--success)';
    }
    syncRerankButton();
    showToast('🔄 Weights reset to default', 'info');
}

// Return the weights currently in effect: the server-normalised set from the
// last run if available, else the user's sliders, else the defaults.
function activeWeights() {
    const source = state.customWeights
        || state.serverWeights
        || DEFAULT_WEIGHTS;
    const out = {};
    Object.keys(DEFAULT_WEIGHTS).forEach(key => {
        const entry = source[key];
        let v;
        if (entry == null) v = DEFAULT_WEIGHTS[key].default;
        else if (typeof entry === 'object') v = entry.weight;
        else v = entry;
        v = Number(v);
        out[key] = Number.isFinite(v) ? v : DEFAULT_WEIGHTS[key].default;
    });
    return out;
}

// Clamp to [0,1] and rescale so the values sum to 1.0. Mirrors
// CandidateScorer.resolve_weights() on the server.
function normalizedWeights() {
    const raw = activeWeights();
    const clamped = {};
    Object.keys(raw).forEach(k => { clamped[k] = Math.min(Math.max(raw[k] || 0, 0), 1); });
    const total = Object.values(clamped).reduce((s, v) => s + v, 0);
    if (total <= 0) return { ...DEFAULT_WEIGHTS };
    const out = {};
    Object.keys(clamped).forEach(k => { out[k] = +(clamped[k] / total).toFixed(4); });
    return out;
}

// Re-run the last analysis with the current slider values.
async function rerankWithWeights() {
    if (!state.currentResults) {
        showToast('Run an analysis first before re-ranking', 'warning');
        return;
    }

    const btn = document.getElementById('rerankBtn');
    const wasSample = !state.jdFile && state.resumeFiles.length === 0;
    const weights = normalizedWeights();

    if (btn) { btn.disabled = true; btn.innerHTML = '<span class="spinner"></span> Re-ranking...'; }
    showProgress('Re-ranking with custom weights...', 40);

    try {
        let response;
        if (wasSample) {
            // No local JD/resumes on hand — re-score the bundled sample set.
            const fd = new FormData();
            fd.append('weights', JSON.stringify(weights));
            response = await fetch(API_BASE + '/api/analyze-sample', { method: 'POST', body: fd });
        } else {
            const fd = new FormData();
            if (state.jdFile) fd.append('job_file', state.jdFile);
            else fd.append('job_description', document.getElementById('jdText').value.trim());
            state.resumeFiles.forEach(f => fd.append('resumes', f));
            fd.append('weights', JSON.stringify(weights));
            response = await fetch(API_BASE + '/api/analyze', { method: 'POST', body: fd });
        }

        if (!response.ok) {
            let msg = 'Re-rank failed';
            try { const e = await response.json(); msg = e.error || msg; } catch (_) {}
            throw new Error(msg);
        }

        const data = await response.json();
        state.currentResults = data;
        state.scores = data.ranked_candidates || [];
        state.serverWeights = data.weights_used || null;

        renderResults(data);
        renderAnalytics(data);
        showProgress('Re-rank complete!', 100);
        setTimeout(hideProgress, 500);
        showToast('⚡ Re-ranked with your custom weights', 'success');
    } catch (e) {
        hideProgress();
        showToast(`❌ ${e.message}`, 'error');
    } finally {
        if (btn) { btn.disabled = false; btn.innerHTML = '⚡ Re-rank with these weights'; }
    }
}

function syncRerankButton() {
    const btn = document.getElementById('rerankBtn');
    if (btn) btn.disabled = !state.currentResults;
}

// ==================== ANALYTICS ====================
// Chart.js is loaded from a CDN. If it is unavailable (offline / blocked),
// every chart call becomes a no-op with a visible notice instead of a
// ReferenceError that would break the rest of the page.
function chartAvailable() {
    return typeof Chart !== 'undefined';
}

function showChartUnavailable(canvas) {
    if (!canvas) return;
    const parent = canvas.parentElement;
    if (!parent) return;
    const old = parent.querySelector('.chart-unavailable');
    if (old) return;
    const note = document.createElement('p');
    note.className = 'empty-hint chart-unavailable';
    note.textContent = '📉 Charts unavailable offline (Chart.js not loaded). All other analytics still work.';
    parent.appendChild(note);
}

// Replace a chart's parent content without destroying the <canvas> element,
// so the same canvas can be reused on the next render.
function setChartPlaceholder(canvas, message) {
    if (!canvas) return;
    const parent = canvas.parentElement;
    if (!parent) return;
    let note = parent.querySelector('.chart-unavailable');
    if (!note) {
        note = document.createElement('p');
        note.className = 'empty-hint chart-unavailable';
        parent.appendChild(note);
    }
    note.textContent = message;
    canvas.style.display = 'none';
}

function clearChartPlaceholder(canvas) {
    if (!canvas) return;
    const parent = canvas.parentElement;
    if (!parent) return;
    const note = parent.querySelector('.chart-unavailable');
    if (note) note.remove();
    canvas.style.display = '';
}

function renderAnalytics(data) {
    const candidates = data.ranked_candidates;
    const summary = data.summary || {};
    
    renderScoreDistribution(summary.score_distribution || {});
    renderSkillCoverage(summary.skill_coverage || {}, candidates);
    renderExperienceDistribution(candidates);
    renderPotentialScores(candidates);
    renderSkillGapSummary(candidates);
    renderHiringKPIs(summary, candidates);
    initWeightsConfig();
}

function renderHiringKPIs(summary, candidates) {
    // Add KPI cards above the analytics grid
    const analyticsGrid = document.getElementById('analyticsGrid');
    if (!analyticsGrid) return;
    
    // Check if already rendered
    if (document.getElementById('hiringKpiSection')) return;
    
    const total = candidates.length;
    const avgScore = summary.average_score || 0;
    const topScore = summary.top_score || 0;
    
    // Compute advanced KPIs
    const scores = candidates.map(c => c.final_score * 100);
    const median = [...scores].sort((a, b) => a - b)[Math.floor(scores.length / 2)] || 0;
    const stdDev = scores.length > 1 ? Math.sqrt(scores.reduce((sq, s) => sq + Math.pow(s - avgScore, 2), 0) / scores.length) : 0;
    
    // Hiring recommendation
    let recommendation, recColor;
    if (avgScore >= 70) { recommendation = 'Strong Pool'; recColor = '#00ff88'; }
    else if (avgScore >= 50) { recommendation = 'Moderate Pool'; recColor = '#ffa502'; }
    else { recommendation = 'Needs Review'; recColor = '#ff4757'; }
    
    const kpiSection = document.createElement('div');
    kpiSection.id = 'hiringKpiSection';
    kpiSection.innerHTML = `
        <h3 style="font-size:1.1rem;margin-bottom:1rem">📊 Hiring Dashboard KPIs</h3>
        <div class="kpi-grid">
            <div class="kpi-card">
                <div class="kpi-icon">👥</div>
                <div class="kpi-value">${total}</div>
                <div class="kpi-label">Total Candidates</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-icon">📈</div>
                <div class="kpi-value">${avgScore.toFixed(1)}%</div>
                <div class="kpi-label">Average Score</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-icon">🏆</div>
                <div class="kpi-value">${topScore.toFixed(1)}%</div>
                <div class="kpi-label">Top Score</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-icon">📊</div>
                <div class="kpi-value">${median.toFixed(1)}%</div>
                <div class="kpi-label">Median Score</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-icon">🎯</div>
                <div class="kpi-value" style="background:none;-webkit-text-fill-color:${recColor};color:${recColor};font-size:1rem">${recommendation}</div>
                <div class="kpi-label">Hiring Recommendation</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-icon">⚖️</div>
                <div class="kpi-value">${stdDev.toFixed(1)}</div>
                <div class="kpi-label">Std Deviation</div>
            </div>
        </div>
    `;
    
    analyticsGrid.parentElement.insertBefore(kpiSection, analyticsGrid);
}

function renderScoreDistribution(distribution) {
    if (!chartAvailable()) { showChartUnavailable(document.querySelector('canvas')); return; }
    let canvas = document.getElementById('scoreDistChart');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (state.scoreDistChart) state.scoreDistChart.destroy();

    const labels = ['Excellent (80%+)', 'Good (60-80%)', 'Moderate (40-60%)', 'Needs Dev (<40%)'];
    const values = [
        distribution.excellent_80_plus || 0,
        distribution.good_60_80 || 0,
        distribution.moderate_40_60 || 0,
        distribution.needs_development_below_40 || 0
    ];
    const colors = ['#00ff88', '#00d4ff', '#ffa502', '#ff4757'];

    if (values.every(v => v === 0)) {
        setChartPlaceholder(canvas, 'No score distribution data available');
        return;
    }
    clearChartPlaceholder(canvas);

    state.scoreDistChart = new Chart(ctx, {
        type: state.analyticsChartType === 'doughnut' ? 'doughnut' : 'bar',
        data: {
            labels,
            datasets: [{ label: 'Candidates', data: values, backgroundColor: colors, borderRadius: 6 }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: state.analyticsChartType === 'doughnut' ? { position: 'right', labels: { color: '#aaa', font: { size: 10 } } } : { display: false }
            },
            scales: state.analyticsChartType === 'bar' ? {
                y: { beginAtZero: true, ticks: { stepSize: 1, color: '#888' }, grid: { color: 'rgba(255,255,255,0.05)' } },
                x: { ticks: { color: '#aaa', font: { size: 10 } }, grid: { display: false } }
            } : {}
        }
    });
}

function renderSkillCoverage(skillCoverage, candidates) {
    if (!chartAvailable()) { showChartUnavailable(document.querySelector('canvas')); return; }
    let canvas = document.getElementById('skillCoverageChart');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (state.skillCoverageChart) state.skillCoverageChart.destroy();

    const skills = Object.keys(skillCoverage).slice(0, 10);
    const coverage = skills.map(s => {
        const item = skillCoverage[s];
        return item && item.coverage_pct ? item.coverage_pct : 0;
    });

    if (skills.length === 0) {
        const allSkills = {};
        if (candidates) {
            candidates.forEach(c => {
                const techSkills = (c.profile && c.profile.technical_skills) || [];
                techSkills.forEach(s => {
                    allSkills[s] = (allSkills[s] || 0) + 1;
                });
            });
        }
        const topSkills = Object.entries(allSkills).sort((a, b) => b[1] - a[1]).slice(0, 10);
        
        if (topSkills.length === 0) {
            const parent = canvas.parentElement;
            if (parent) parent.innerHTML = '<p class="empty-hint">No skill data available</p>';
            return;
        }
        
        state.skillCoverageChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: topSkills.map(([s]) => s),
                datasets: [{
                    label: 'Candidates',
                    data: topSkills.map(([, c]) => c),
                    backgroundColor: 'rgba(108,99,255,0.7)',
                    borderRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                indexAxis: 'y',
                plugins: { legend: { display: false } },
                scales: {
                    x: { beginAtZero: true, ticks: { stepSize: 1, color: '#888' }, grid: { color: 'rgba(255,255,255,0.05)' } },
                    y: { ticks: { color: '#aaa', font: { size: 10 } }, grid: { display: false } }
                }
            }
        });
        return;
    }

    state.skillCoverageChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: skills,
            datasets: [{
                label: 'Coverage %',
                data: coverage,
                backgroundColor: 'rgba(0,212,255,0.7)',
                borderRadius: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            indexAxis: 'y',
            plugins: { legend: { display: false } },
            scales: {
                x: { beginAtZero: true, max: 100, ticks: { color: '#888' }, grid: { color: 'rgba(255,255,255,0.05)' } },
                y: { ticks: { color: '#aaa', font: { size: 10 } }, grid: { display: false } }
            }
        }
    });
}

function renderExperienceDistribution(candidates) {
    if (!chartAvailable()) { showChartUnavailable(document.querySelector('canvas')); return; }
    let canvas = document.getElementById('expDistChart');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (state.expDistChart) state.expDistChart.destroy();

    const expRanges = { '0-2 yrs': 0, '3-5 yrs': 0, '6-8 yrs': 0, '9-12 yrs': 0, '12+ yrs': 0 };
    if (candidates) {
        candidates.forEach(c => {
            const exp = (c.profile && c.profile.experience_years) || 0;
            if (exp <= 2) expRanges['0-2 yrs']++;
            else if (exp <= 5) expRanges['3-5 yrs']++;
            else if (exp <= 8) expRanges['6-8 yrs']++;
            else if (exp <= 12) expRanges['9-12 yrs']++;
            else expRanges['12+ yrs']++;
        });
    }

    state.expDistChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: Object.keys(expRanges),
            datasets: [{
                data: Object.values(expRanges),
                backgroundColor: ['#6c63ff', '#00d4ff', '#00ff88', '#ffa502', '#ff4757'],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'right', labels: { color: '#aaa', font: { size: 11 }, padding: 12 } }
            }
        }
    });
}

function renderPotentialScores(candidates) {
    if (!chartAvailable()) { showChartUnavailable(document.querySelector('canvas')); return; }
    let canvas = document.getElementById('potentialChart');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (state.potentialChart) state.potentialChart.destroy();

    if (!candidates || candidates.length === 0) {
        const parent = canvas.parentElement;
        if (parent) parent.innerHTML = '<p class="empty-hint">No candidate data</p>';
        return;
    }

    const labels = candidates.slice(0, 10).map(c => {
        const name = c.candidate_name || '';
        return name.split(' ')[0] || 'Candidate';
    });
    const potentialData = candidates.slice(0, 10).map(c => (c.potential && c.potential.potential_score) || 0);
    const fitData = candidates.slice(0, 10).map(c => c.final_score * 100);

    state.potentialChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels,
            datasets: [
                { label: 'Fit Score', data: fitData, backgroundColor: 'rgba(108,99,255,0.7)', borderRadius: 4 },
                { label: 'Potential Score', data: potentialData, backgroundColor: 'rgba(0,255,136,0.7)', borderRadius: 4 }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { labels: { color: '#aaa', font: { size: 10 } } }
            },
            scales: {
                y: { beginAtZero: true, max: 100, ticks: { color: '#888' }, grid: { color: 'rgba(255,255,255,0.05)' } },
                x: { ticks: { color: '#aaa', font: { size: 9 } }, grid: { display: false } }
            }
        }
    });
}

function renderSkillGapSummary(candidates) {
    const container = document.getElementById('skillGapSummary');
    if (!container) return;
    
    const allMissing = {};
    if (candidates) {
        candidates.forEach(c => {
            const gaps = c.skill_gaps || {};
            const missing = gaps.missing_required_skills || [];
            missing.forEach(s => {
                allMissing[s] = (allMissing[s] || 0) + 1;
            });
        });
    }

    const sortedGaps = Object.entries(allMissing).sort((a, b) => b[1] - a[1]).slice(0, 10);
    
    if (sortedGaps.length === 0) {
        container.innerHTML = '<p class="empty-hint" style="padding:1.5rem">No skill gaps identified — all candidates match required skills</p>';
        return;
    }

    const total = candidates ? candidates.length : 1;
    container.innerHTML = `
        <h4 style="margin-bottom:1rem">Most Common Missing Skills (across all candidates)</h4>
        <div class="gap-chart">
            ${sortedGaps.map(([skill, count]) => `
                <div class="gap-row">
                    <span class="gap-skill">${skill}</span>
                    <div class="gap-bar-bg">
                        <div class="gap-bar-fill" style="width:${(count / total * 100).toFixed(0)}%"></div>
                    </div>
                    <span class="gap-count">${count}/${total} (${(count/total*100).toFixed(0)}%)</span>
                </div>
            `).join('')}
        </div>
    `;
}

function switchAnalyticsChart(type, btn) {
    state.analyticsChartType = type;
    const toggles = document.querySelectorAll('#analyticsGrid .chart-toggle');
    toggles.forEach(b => b.classList.remove('active'));
    if (btn) btn.classList.add('active');
    if (state.currentResults) renderAnalytics(state.currentResults);
}

// ==================== COPILOT ====================
async function sendCopilotQuery() {
    const input = document.getElementById('copilotQuery');
    const query = input.value.trim();
    if (!query) return;

    const chat = document.getElementById('copilotChat');
    
    const userMsg = document.createElement('div');
    userMsg.className = 'copilot-message user';
    userMsg.innerHTML = `
        <div class="message-avatar">👤</div>
        <div class="message-content"><p>${escapeHtml(query)}</p></div>
    `;
    chat.appendChild(userMsg);
    
    input.value = '';
    chat.scrollTop = chat.scrollHeight;

    const loadingMsg = document.createElement('div');
    loadingMsg.className = 'copilot-message assistant';
    loadingMsg.id = 'copilotLoading';
    loadingMsg.innerHTML = `
        <div class="message-avatar">🤖</div>
        <div class="message-content"><p><span class="spinner"></span> Thinking...</p></div>
    `;
    chat.appendChild(loadingMsg);
    chat.scrollTop = chat.scrollHeight;

    try {
        const res = await fetch(API_BASE + '/api/copilot', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query })
        });
        
        loadingMsg.remove();
        
        if (!res.ok) {
            let errMsg = 'Copilot query failed';
            try { const err = await res.json(); errMsg = err.error || errMsg; } catch (_) {}
            throw new Error(errMsg);
        }
        
        const data = await res.json();
        
        const assistantMsg = document.createElement('div');
        assistantMsg.className = 'copilot-message assistant';
        assistantMsg.innerHTML = `
            <div class="message-avatar">🤖</div>
            <div class="message-content">${formatCopilotResponse(data.answer || 'No response')}</div>
        `;
        chat.appendChild(assistantMsg);
        
    } catch (e) {
        if (loadingMsg.parentNode) loadingMsg.remove();
        const errorMsg = document.createElement('div');
        errorMsg.className = 'copilot-message assistant error';
        errorMsg.innerHTML = `
            <div class="message-avatar">⚠️</div>
            <div class="message-content"><p>${e.message}</p></div>
        `;
        chat.appendChild(errorMsg);
    }
    
    chat.scrollTop = chat.scrollHeight;
}

async function clearCopilot() {
    try {
        await fetch(API_BASE + '/api/copilot/clear', { method: 'POST' });
        const chat = document.getElementById('copilotChat');
        chat.innerHTML = `
            <div class="copilot-message assistant">
                <div class="message-avatar">🤖</div>
                <div class="message-content">
                    <p>Chat cleared. How can I help you with candidate analysis?</p>
                </div>
            </div>
        `;
        showToast('🗑️ Chat history cleared', 'info');
    } catch (e) {
        showToast('Failed to clear chat', 'error');
    }
}

function showCopilotHelp() {
    const chat = document.getElementById('copilotChat');
    const msg = document.createElement('div');
    msg.className = 'copilot-message assistant';
    msg.innerHTML = `
        <div class="message-avatar">🤖</div>
        <div class="message-content">
            <p><strong>Try these example queries:</strong></p>
            <ul>
                <li>"Show top 5 candidates"</li>
                <li>"Candidates with Python skills"</li>
                <li>"Who knows AWS?"</li>
                <li>"Who lacks Kubernetes?"</li>
                <li>"Compare Sneha and Karan"</li>
                <li>"Tell me about Divya"</li>
                <li>"Who should we hire?"</li>
                <li>"Average candidate score"</li>
                <li>"What skills are most common?"</li>
                <li>"Show summary of all candidates"</li>
            </ul>
        </div>
    `;
    chat.appendChild(msg);
    chat.scrollTop = chat.scrollHeight;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatCopilotResponse(text) {
    if (!text) return '<p>No response</p>';
    let html = text
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\n/g, '<br>')
        .replace(/•/g, '•');
    
    if (!html.startsWith('<')) {
        html = `<p>${html}</p>`;
    }
    
    return html;
}

// ==================== BIAS-FREE REPORT ====================
function renderBiasReport(data) {
    const body = document.getElementById('biasReportBody');
    const candidates = (data && data.ranked_candidates) || [];
    
    if (candidates.length === 0) {
        if (body) {
            body.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon">🔍</div>
                    <h3>No data available</h3>
                    <p>Analyze candidates to see bias-free evaluation results</p>
                </div>
            `;
        }
        return;
    }

    const totalAnonymized = candidates.filter(c => c.bias_free && c.bias_free.anonymized).length;
    const avgFairness = candidates.reduce((s, c) => s + ((c.bias_free && c.bias_free.fairness_score) || 0), 0) / candidates.length;

    if (body) {
        body.innerHTML = `
            <div class="bias-stats">
                <div class="bias-stat">
                    <span class="bias-stat-value">${totalAnonymized}/${candidates.length}</span>
                    <span class="bias-stat-label">Candidates Anonymized</span>
                </div>
                <div class="bias-stat">
                    <span class="bias-stat-value">${avgFairness.toFixed(1)}%</span>
                    <span class="bias-stat-label">Average Fairness Score</span>
                </div>
                <div class="bias-stat">
                    <span class="bias-stat-value">🟢</span>
                    <span class="bias-stat-label">Bias-Free Mode Active</span>
                </div>
            </div>
            <div class="bias-details">
                <h4>Per-Candidate Breakdown</h4>
                <div class="bias-candidate-list">
                    ${candidates.slice(0, 10).map(c => `
                        <div class="bias-candidate-row">
                            <span>${c.candidate_name}</span>
                            <span class="bias-fairness-badge ${((c.bias_free && c.bias_free.fairness_score) || 0) >= 80 ? 'high' : 'medium'}">
                                ${((c.bias_free && c.bias_free.fairness_score) || 0).toFixed(0)}% Fair
                            </span>
                        </div>
                    `).join('')}
                </div>
            </div>
            <div class="bias-info">
                <p>✅ <strong>What was removed:</strong> Name, Gender Pronouns, Age Indicators, Address, Email, Phone, Photo references</p>
                <p>⚖️ <strong>Evaluation:</strong> All candidates scored on skills, experience, and merit only — no demographic bias</p>
            </div>
        `;
    }
}

// ==================== PDF REPORT ====================
function generatePdfReport() {
    if (!state.currentResults || !state.currentResults.ranked_candidates) {
        showToast('No results to generate report', 'warning');
        return;
    }
    
    const candidates = state.currentResults.ranked_candidates;
    const summary = state.currentResults.summary || {};
    const jobProfile = state.currentResults.job_profile || {};
    
    showToast('📄 Generating PDF report...', 'info');
    
    // Build complete HTML report for printing/PDF
    const reportWindow = window.open('', '_blank', 'width=1200,height=800');
    
    const themeColor = '#6c63ff';
    const reportHTML = `<!DOCTYPE html>
<html>
<head>
    <title>Recruitment Report</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Inter', sans-serif; color: #1a1a2e; background: #f4f6fb; padding: 40px; }
        .report-header { text-align: center; margin-bottom: 30px; }
        .report-header h1 { font-size: 1.8rem; background: linear-gradient(135deg, #6c63ff, #00d4ff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .report-header p { color: #666; margin-top: 8px; font-size: 0.9rem; }
        .report-meta { display: flex; justify-content: center; gap: 30px; margin-top: 15px; font-size: 0.85rem; color: #555; }
        
        .section { background: white; border-radius: 12px; padding: 24px; margin-bottom: 20px; box-shadow: 0 2px 12px rgba(0,0,0,0.06); }
        .section h2 { font-size: 1.2rem; margin-bottom: 16px; padding-bottom: 8px; border-bottom: 2px solid #6c63ff; display: flex; align-items: center; gap: 8px; }
        
        .kpi-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 16px; }
        .kpi-item { text-align: center; padding: 16px; background: #f8f9ff; border-radius: 8px; }
        .kpi-value { font-size: 1.6rem; font-weight: 700; color: #6c63ff; }
        .kpi-label { font-size: 0.75rem; color: #888; text-transform: uppercase; letter-spacing: 0.5px; margin-top: 4px; }
        
        table { width: 100%; border-collapse: collapse; font-size: 0.85rem; }
        th { background: #6c63ff; color: white; padding: 10px 12px; text-align: left; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.5px; }
        td { padding: 10px 12px; border-bottom: 1px solid #e0e0e0; }
        tr:hover { background: #f8f9ff; }
        .rank-1 td:first-child { font-weight: 700; color: #ffd700; }
        .rank-2 td:first-child { font-weight: 700; color: #c0c0c0; }
        .rank-3 td:first-child { font-weight: 700; color: #cd7f32; }
        
        .score-bar { display: inline-block; width: 60px; height: 6px; background: #e0e0e0; border-radius: 10px; overflow: hidden; vertical-align: middle; }
        .score-bar-fill { height: 100%; border-radius: 10px; }
        
        .footnote { text-align: center; font-size: 0.75rem; color: #999; margin-top: 30px; padding-top: 16px; border-top: 1px solid #e0e0e0; }
        
        .recommendation-box { padding: 16px; border-radius: 8px; background: #f0fff4; border-left: 4px solid #00ff88; margin-top: 16px; }
        .rec-title { font-weight: 700; margin-bottom: 6px; color: #1a1a2e; }
        .rec-text { font-size: 0.85rem; color: #555; }
        
        @media print { body { padding: 20px; } .section { break-inside: avoid; } }
    </style>
</head>
<body>
    <div class="report-header">
        <h1>Recruitment Report</h1>
        <p>AI-Powered Candidate Ranking & Intelligence Report</p>
        <div class="report-meta">
            <span>📅 Generated: ${new Date().toLocaleString()}</span>
            <span>👥 Total Candidates: ${candidates.length}</span>
            <span>🎯 Role: ${jobProfile.role || 'N/A'}</span>
        </div>
    </div>
    
    <div class="section">
        <h2>📊 Key Metrics</h2>
        <div class="kpi-grid">
            <div class="kpi-item">
                <div class="kpi-value">${candidates.length}</div>
                <div class="kpi-label">Candidates</div>
            </div>
            <div class="kpi-item">
                <div class="kpi-value">${(summary.average_score || 0).toFixed(1)}%</div>
                <div class="kpi-label">Average Score</div>
            </div>
            <div class="kpi-item">
                <div class="kpi-value">${(summary.top_score || 0).toFixed(1)}%</div>
                <div class="kpi-label">Top Score</div>
            </div>
            <div class="kpi-item">
                <div class="kpi-value">${(summary.median_score || 0).toFixed(1)}%</div>
                <div class="kpi-label">Median Score</div>
            </div>
        </div>
        <div style="display:flex;gap:16px;font-size:0.85rem;color:#555;flex-wrap:wrap">
            <span>💼 Min Exp: ${(summary.experience_distribution && summary.experience_distribution.min_exp) || 0} yrs</span>
            <span>💼 Max Exp: ${(summary.experience_distribution && summary.experience_distribution.max_exp) || 0} yrs</span>
            <span>💼 Avg Exp: ${(summary.experience_distribution && summary.experience_distribution.avg_exp) || 0} yrs</span>
            <span>⚖️ Bias-Free: Active</span>
        </div>
    </div>
    
    <div class="section">
        <h2>🏆 Ranked Candidates</h2>
        <table>
            <thead>
                <tr>
                    <th>Rank</th>
                    <th>Candidate</th>
                    <th>Score</th>
                    <th>Skill</th>
                    <th>Exp</th>
                    <th>Semantic</th>
                    <th>Potential</th>
                    <th>Skills</th>
                </tr>
            </thead>
            <tbody>
                ${candidates.map((c, i) => `
                    <tr class="rank-${c.rank <= 3 ? c.rank : ''}">
                        <td>${c.rank}${c.rank === 1 ? ' 🥇' : c.rank === 2 ? ' 🥈' : c.rank === 3 ? ' 🥉' : ''}</td>
                        <td><strong>${c.candidate_name}</strong></td>
                        <td><strong>${(c.final_score * 100).toFixed(1)}%</strong></td>
                        <td><div class="score-bar"><div class="score-bar-fill" style="width:${(c.scores.skill_match||0)*100}%;background:#6c63ff"></div></div></td>
                        <td><div class="score-bar"><div class="score-bar-fill" style="width:${(c.scores.experience_match||0)*100}%;background:#00d4ff"></div></div></td>
                        <td><div class="score-bar"><div class="score-bar-fill" style="width:${(c.scores.semantic_similarity||0)*100}%;background:#a855f7"></div></div></td>
                        <td>${(c.potential && c.potential.potential_score || 0).toFixed(0)}%</td>
                        <td style="font-size:0.75rem">${(c.profile && c.profile.technical_skills || []).slice(0, 5).join(', ')}</td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
        
        <div class="recommendation-box">
            <div class="rec-title">🎯 Hiring Recommendation</div>
            <div class="rec-text">
                <strong>Top Pick:</strong> ${candidates[0].candidate_name} — ${(candidates[0].final_score * 100).toFixed(1)}% fit.
                ${candidates[0].reason || ''}
                ${candidates.length > 1 && candidates[1].final_score >= candidates[0].final_score * 0.9 ? 
                    `<br><strong>Also Consider:</strong> ${candidates[1].candidate_name}` : ''}
            </div>
        </div>
    </div>
    
    <div class="section">
        <h2>📈 Score Distribution</h2>
        <p>Excellent (80%+): ${summary.score_distribution ? summary.score_distribution.excellent_80_plus : 0} | 
           Good (60-80%): ${summary.score_distribution ? summary.score_distribution.good_60_80 : 0} | 
           Moderate (40-60%): ${summary.score_distribution ? summary.score_distribution.moderate_40_60 : 0} | 
           Needs Dev (<40%): ${summary.score_distribution ? summary.score_distribution.needs_development_below_40 : 0}</p>
    </div>
    
    ${jobProfile && jobProfile.required_skills && jobProfile.required_skills.length > 0 ? `
    <div class="section">
        <h2>📋 Job Requirements</h2>
        <p><strong>Role:</strong> ${jobProfile.role || 'N/A'}</p>
        <p><strong>Required Skills:</strong> ${jobProfile.required_skills.join(', ')}</p>
        <p><strong>Preferred Skills:</strong> ${(jobProfile.preferred_skills || []).join(', ') || 'None specified'}</p>
        <p><strong>Experience Required:</strong> ${jobProfile.experience_required || 0}+ years</p>
        <p><strong>Domain:</strong> ${jobProfile.domain || 'General'}</p>
    </div>` : ''}
    
    <div class="footnote">
        Generated by <strong>Candidate Ranking System</strong><br>
        11 AI Modules • 7 Scoring Dimensions • Bias-Free Evaluation • Explainable AI
    </div>
    
    <script>
        window.onload = function() { window.print(); }
    <\/script>
</body>
</html>`;
    
    reportWindow.document.write(reportHTML);
    reportWindow.document.close();
    
    showToast('📄 Report generated in new window. Press Ctrl+S to save as PDF.', 'success');
}

// ==================== SIMILARITY MATRIX ====================
function showSimilarityMatrix() {
    if (!state.currentResults || !state.currentResults.ranked_candidates || state.currentResults.ranked_candidates.length < 2) {
        showToast('Need at least 2 candidates for similarity matrix', 'warning');
        return;
    }
    
    const candidates = state.currentResults.ranked_candidates;
    const names = candidates.map(c => c.candidate_name.split(' ')[0] || c.candidate_name);
    const n = candidates.length;
    
    // Compute similarity scores based on skill overlap
    const matrix = [];
    for (let i = 0; i < n; i++) {
        matrix[i] = [];
        const skillsI = new Set((candidates[i].profile && candidates[i].profile.technical_skills || []).map(s => s.toLowerCase()));
        for (let j = 0; j < n; j++) {
            if (i === j) {
                matrix[i][j] = 100;
            } else {
                const skillsJ = new Set((candidates[j].profile && candidates[j].profile.technical_skills || []).map(s => s.toLowerCase()));
                const intersection = new Set([...skillsI].filter(s => skillsJ.has(s)));
                const union = new Set([...skillsI, ...skillsJ]);
                matrix[i][j] = union.size > 0 ? Math.round((intersection.size / union.size) * 100) : 0;
            }
        }
    }
    
    const modal = document.getElementById('compareModal');
    const grid = document.getElementById('compareGrid');
    
    const getColor = (val) => {
        if (val >= 70) return 'rgba(0,255,136,0.3)';
        if (val >= 40) return 'rgba(0,212,255,0.3)';
        if (val >= 20) return 'rgba(255,165,2,0.3)';
        return 'rgba(255,71,87,0.3)';
    };
    
    grid.innerHTML = `
        <div class="modal-header" style="position:static;padding-bottom:1rem;margin-bottom:0">
            <h2>📊 Candidate Similarity Matrix</h2>
            <span style="font-size:0.75rem;color:var(--text-muted)">Skill overlap percentage between candidates</span>
        </div>
        <div class="matrix-container">
            <table class="matrix-table">
                <thead>
                    <tr>
                        <th></th>
                        ${names.map(n => `<th>${n}</th>`).join('')}
                    </tr>
                </thead>
                <tbody>
                    ${matrix.map((row, i) => `
                        <tr>
                            <td><strong>${names[i]}</strong></td>
                            ${row.map((val, j) => `
                                <td>
                                    <span class="matrix-cell" style="background:${getColor(val)};color:${val >= 50 ? '#1a1a2e' : '#aaa'}">
                                        ${val}%
                                    </span>
                                </td>
                            `).join('')}
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        </div>
        <p style="text-align:center;font-size:0.75rem;color:var(--text-muted);margin-top:1rem">
            Higher percentage = more skill overlap. Use to identify similar/duplicate profiles.
        </p>
    `;
    
    modal.classList.add('active');
    
    // Update the modal header to have the proper close button
    const modalContent = modal.querySelector('.modal-content');
    const existingClose = modalContent.querySelector('.modal-close');
    if (!existingClose) {
        const closeBtn = document.createElement('button');
        closeBtn.className = 'modal-close';
        closeBtn.onclick = () => closeCompareModal();
        closeBtn.textContent = '✕';
        modalContent.querySelector('.modal-header')?.appendChild(closeBtn);
    }
}

// ==================== DOWNLOAD HELPER ====================
// ==================== PRO FEATURES TAB ====================

function populateFeatureSelects() {
    const candidates = state.currentResults?.ranked_candidates || [];
    const selects = ['atsCandidateSelect', 'salaryCandidateSelect', 'careerCandidateSelect', 
                     'emailCandidateSelect', 'teamFitCandidateSelect'];
    
    selects.forEach(id => {
        const sel = document.getElementById(id);
        if (!sel) return;
        sel.innerHTML = '<option value="">Select candidate...</option>';
        candidates.forEach((c, i) => {
            sel.innerHTML += `<option value="${i}">${c.candidate_name}</option>`;
        });
    });
}

async function getATSScore() {
    const idx = document.getElementById('atsCandidateSelect').value;
    if (!idx) { showToast('Please select a candidate', 'warning'); return; }
    const res = document.getElementById('atsResult');
    res.innerHTML = '<p class="empty-hint">Loading ATS score...</p>';
    res.classList.add('active');
    
    try {
        const r = await fetch(API_BASE + `/api/ats-score/${idx}`);
        const data = await r.json();
        const ats = data.ats_score;
        res.innerHTML = `
            <h4>📄 ATS Resume Score</h4>
            <div class="metric-grid">
                <div class="metric-item"><div class="metric-value">${ats.ats_score}/100</div><div class="metric-label">ATS Score</div></div>
                <div class="metric-item"><div class="metric-value">${ats.ats_level}</div><div class="metric-label">Level</div></div>
            </div>
            <p style="margin:8px 0">${ats.description}</p>
            ${ats.findings?.length ? `<h4>✅ Findings</h4>${ats.findings.map(f => `<div class="highlight-item">${f}</div>`).join('')}` : ''}
            ${ats.optimization_tips?.length ? `<h4>💡 Optimization Tips</h4>${ats.optimization_tips.map(t => `<div class="tip-item">${t}</div>`).join('')}` : ''}
            <div style="margin-top:8px;font-size:0.75rem;color:var(--text-muted)">
                Score breakdown: Sections ${ats.section_completeness}/25 • Keywords ${ats.keyword_optimization}/20 • Actions ${ats.action_verbs_usage}/15 • Quant ${ats.quantifiable_impact}/15 • Format ${ats.formatting_quality}/10 • Contact ${ats.contact_info}/10
            </div>
        `;
        showToast(`ATS score: ${ats.ats_score}/100 - ${ats.ats_level}`, 'info');
    } catch (e) {
        res.innerHTML = `<p class="empty-hint">Error: ${e.message}</p>`;
    }
}

async function getSalaryPrediction() {
    const idx = document.getElementById('salaryCandidateSelect').value;
    if (!idx) { showToast('Please select a candidate', 'warning'); return; }
    const res = document.getElementById('salaryResult');
    res.innerHTML = '<p class="empty-hint">Calculating salary prediction...</p>';
    res.classList.add('active');
    
    try {
        const r = await fetch(API_BASE + `/api/salary-predict/${idx}`);
        const data = await r.json();
        const p = data.prediction;
        res.innerHTML = `
            <h4>💰 Salary Prediction for ${data.candidate_name}</h4>
            <div class="metric-grid">
                <div class="metric-item"><div class="metric-value">₹${p.predicted_range.min_lpa}L</div><div class="metric-label">Min (P10)</div></div>
                <div class="metric-item"><div class="metric-value">₹${p.predicted_range.midpoint_lpa}L</div><div class="metric-label">Mid (P50)</div></div>
                <div class="metric-item"><div class="metric-value">₹${p.predicted_range.max_lpa}L</div><div class="metric-label">Max (P90)</div></div>
                <div class="metric-item"><div class="metric-value">${p.level}</div><div class="metric-label">Level</div></div>
            </div>
            <p style="margin:8px 0">${p.explanation}</p>
            <p style="font-size:0.75rem;color:var(--text-muted)">Confidence: ${p.confidence.level} (${p.confidence.score}%) • ${p.market_context}</p>
            <p style="font-size:0.75rem;color:var(--text-muted);margin-top:4px">Skill premium: +${p.skill_premium_applied}% • Education: +${p.education_adjustment}%</p>
        `;
    } catch (e) {
        res.innerHTML = `<p class="empty-hint">Error: ${e.message}</p>`;
    }
}

async function getCareerPath() {
    const idx = document.getElementById('careerCandidateSelect').value;
    if (!idx) { showToast('Please select a candidate', 'warning'); return; }
    const res = document.getElementById('careerResult');
    res.innerHTML = '<p class="empty-hint">Predicting career path...</p>';
    res.classList.add('active');
    
    try {
        const r = await fetch(API_BASE + `/api/career-path/${idx}`);
        const data = await r.json();
        const path = data.career_path;
        
        let timelineHtml = '';
        path.next_stages?.forEach(s => {
            timelineHtml += `<div class="timeline-item">
                <div class="timeline-title">${s.title}</div>
                <div class="timeline-date">Est. ${s.estimated_date} (${s.years_from_now} yrs) • Readiness: ${s.readiness_level}</div>
                ${s.missing_skills?.length ? `<div style="font-size:0.75rem;color:var(--text-muted)">Missing: ${s.missing_skills.join(', ')}</div>` : ''}
            </div>`;
        });
        
        res.innerHTML = `
            <h4>🧭 Career Path for ${data.candidate_name}</h4>
            <p><strong>Current Role:</strong> ${path.current_role} (${path.current_experience} yrs)</p>
            <p><strong>Career Velocity:</strong> ${path.career_velocity.level} (${path.career_velocity.score}/100) - ${path.career_velocity.description}</p>
            <h4 style="margin-top:8px">📈 Career Progression</h4>
            ${timelineHtml || '<p class="empty-hint">Reached career peak in current path</p>'}
            ${path.alternative_paths?.length ? `<h4>🔄 Alternative Paths</h4>${path.alternative_paths.map(a => `<div class="highlight-item">${a.role} - ${a.feasibility} feasibility (${a.skill_match}% match)</div>`).join('')}` : ''}
        `;
    } catch (e) {
        res.innerHTML = `<p class="empty-hint">Error: ${e.message}</p>`;
    }
}

async function generateEmail() {
    const idx = document.getElementById('emailCandidateSelect').value;
    const type = document.getElementById('emailTypeSelect').value;
    if (!idx) { showToast('Please select a candidate', 'warning'); return; }
    const res = document.getElementById('emailResult');
    res.innerHTML = '<p class="empty-hint">Generating email...</p>';
    res.classList.add('active');
    
    try {
        const r = await fetch(API_BASE + '/api/email-draft', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ candidate_index: parseInt(idx), email_type: type })
        });
        const data = await r.json();
        res.innerHTML = `
            <h4>✉️ ${data.email.type.replace('_', ' ').toUpperCase()}</h4>
            <p style="font-size:0.8rem;font-weight:600;margin:4px 0">Subject: ${data.email.subject}</p>
            <div class="email-preview">${data.email.body}</div>
            <button class="btn-sm" style="margin-top:8px" onclick="copyToClipboard(this,'email-preview')">📋 Copy to Clipboard</button>
        `;
    } catch (e) {
        res.innerHTML = `<p class="empty-hint">Error: ${e.message}</p>`;
    }
}

function copyToClipboard(btn, cls) {
    const text = btn.parentElement.querySelector(`.${cls}`)?.textContent;
    if (text) { navigator.clipboard.writeText(text); showToast('Copied to clipboard!', 'success'); }
}

async function getDiversityAnalysis() {
    const res = document.getElementById('diversityResult');
    res.innerHTML = '<p class="empty-hint">Analyzing diversity metrics...</p>';
    res.classList.add('active');
    
    try {
        const r = await fetch(API_BASE + '/api/diversity-analysis');
        const data = await r.json();
        res.innerHTML = `
            <h4>🌈 Diversity Analytics</h4>
            <div class="metric-grid">
                <div class="metric-item"><div class="metric-value">${data.overall_diversity_score}/100</div><div class="metric-label">Overall Score</div></div>
                <div class="metric-item"><div class="metric-value">${data.diversity_level}</div><div class="metric-label">Level</div></div>
                <div class="metric-item"><div class="metric-value">${data.total_candidates}</div><div class="metric-label">Candidates</div></div>
            </div>
            <div style="margin:8px 0">
                <div class="progress-sm"><div class="progress-fill" style="width:${data.components?.educational_diversity || 0}%;background:linear-gradient(90deg,#6c63ff,#00d4ff)"></div></div>
                <small>Educational: ${data.components?.educational_diversity || 0}/100</small>
                <div class="progress-sm"><div class="progress-fill" style="width:${data.components?.skill_diversity || 0}%;background:linear-gradient(90deg,#00d4ff,#00ff88)"></div></div>
                <small>Skill: ${data.components?.skill_diversity || 0}/100</small>
                <div class="progress-sm"><div class="progress-fill" style="width:${data.components?.experience_diversity || 0}%;background:linear-gradient(90deg,#a855f7,#ec4899)"></div></div>
                <small>Experience: ${data.components?.experience_diversity || 0}/100</small>
            </div>
            ${data.diversity_insights?.length ? `<h4>💡 Insights</h4>${data.diversity_insights.map(i => `<div class="tip-item">${i}</div>`).join('')}` : ''}
            ${data.recommendations?.length ? `<h4>📋 Recommendations</h4>${data.recommendations.map(r => `<div class="tip-item" style="border-left-color:var(--accent-2)">${r}</div>`).join('')}` : ''}
        `;
    } catch (e) {
        res.innerHTML = `<p class="empty-hint">Error: ${e.message}</p>`;
    }
}

async function getTeamFit() {
    const idx = document.getElementById('teamFitCandidateSelect').value;
    const culture = document.getElementById('teamCultureSelect').value;
    if (!idx) { showToast('Please select a candidate', 'warning'); return; }
    const res = document.getElementById('teamFitResult');
    res.innerHTML = '<p class="empty-hint">Analyzing team fit...</p>';
    res.classList.add('active');
    
    try {
        const r = await fetch(API_BASE + '/api/team-fit', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ candidate_index: parseInt(idx), team_culture: culture })
        });
        const data = await r.json();
        const fit = data.team_fit;
        res.innerHTML = `
            <h4>🤝 Team Fit: ${data.candidate_name}</h4>
            <div class="metric-grid">
                <div class="metric-item"><div class="metric-value" style="color:${fit.overall_fit_score >= 70 ? 'var(--success)' : fit.overall_fit_score >= 50 ? 'var(--warning)' : 'var(--danger)'}">${fit.overall_fit_score}%</div><div class="metric-label">Fit Score</div></div>
                <div class="metric-item"><div class="metric-value">${fit.fit_level}</div><div class="metric-label">Level</div></div>
                <div class="metric-item"><div class="metric-value">${fit.team_culture}</div><div class="metric-label">Culture</div></div>
            </div>
            <p style="margin:8px 0">${fit.culture_description}</p>
            <p style="font-size:0.85rem;font-weight:500">${fit.recommendation}</p>
            ${fit.strengths?.length ? `<h4>✅ Strengths</h4>${fit.strengths.map(s => `<div class="highlight-item">${s}</div>`).join('')}` : ''}
            ${fit.areas_for_development?.length ? `<h4>📈 Development Areas</h4>${fit.areas_for_development.map(a => `<div class="tip-item">${a}</div>`).join('')}` : ''}
        `;
    } catch (e) {
        res.innerHTML = `<p class="empty-hint">Error: ${e.message}</p>`;
    }
}

async function loadHistory() {
    const res = document.getElementById('historyResult');
    res.innerHTML = '<p class="empty-hint">Loading history...</p>';
    res.classList.add('active');
    
    try {
        const r = await fetch(API_BASE + '/api/history');
        const data = await r.json();
        if (!data.entries?.length) {
            res.innerHTML = '<p class="empty-hint">No analysis history yet. Run some analyses first!</p>';
            return;
        }
        let html = `<h4>📚 Analysis History</h4>
            <div style="font-size:0.75rem;color:var(--text-muted);margin-bottom:8px">Total: ${data.stats.total_analyses} analyses • ${data.stats.total_candidates_analyzed} candidates analyzed</div>`;
        data.entries.forEach(e => {
            html += `<div class="timeline-item" style="cursor:pointer" onclick="restoreHistory('${e.id}')">
                <div class="timeline-title">${e.role} (${e.total_candidates} candidates)</div>
                <div class="timeline-date">${new Date(e.timestamp).toLocaleString()} • Top: ${e.top_candidate} (${(e.top_score*100).toFixed(0)}%)</div>
            </div>`;
        });
        html += '<div style="font-size:0.7rem;color:var(--text-muted);margin-top:8px">Click an entry to restore results</div>';
        res.innerHTML = html;
    } catch (e) {
        res.innerHTML = `<p class="empty-hint">Error: ${e.message}</p>`;
    }
}

async function restoreHistory(entryId) {
    try {
        const r = await fetch(API_BASE + `/api/history/${entryId}`);
        const data = await r.json();
        state.currentResults = data;
        state.serverWeights = data.weights_used || null;
        enableFeatureTabs();
        syncRerankButton();
        renderResults(data);
        renderAnalytics(data);
        renderShortlist();
        renderBiasReport();
        applyFilters();
        switchTab('rankings');
        showToast('✅ Historical results restored!', 'success');
    } catch (e) {
        showToast(`Error: ${e.message}`, 'error');
    }
}

async function clearHistory() {
    if (!confirm('Clear all analysis history?')) return;
    try {
        await fetch(API_BASE + '/api/history/clear', { method: 'POST' });
        document.getElementById('historyResult').innerHTML = '<p class="empty-hint">History cleared</p>';
        showToast('🗑️ History cleared', 'info');
    } catch (e) {
        showToast(`Error: ${e.message}`, 'error');
    }
}

// Role templates for Multi-Job Batch Analysis. Each carries a distinct skill
// set / experience bar so the backend re-scores candidates per role instead of
// replaying one generic ranking.
const MULTI_JOB_ROLES = {
    data_scientist: {
        role: 'Data Scientist',
        required_skills: ['python', 'sql', 'machine learning', 'statistics', 'pandas'],
        experience_required: 4,
        domain: 'Analytics'
    },
    ml_engineer: {
        role: 'ML Engineer',
        required_skills: ['python', 'tensorflow', 'pytorch', 'docker', 'mlops'],
        experience_required: 5,
        domain: 'Machine Learning'
    },
    full_stack: {
        role: 'Full Stack Developer',
        required_skills: ['javascript', 'react', 'nodejs', 'sql', 'rest'],
        experience_required: 3,
        domain: 'Software Engineering'
    },
    product_manager: {
        role: 'Product Manager',
        required_skills: ['product strategy', 'agile', 'stakeholder management', 'roadmapping'],
        experience_required: 5,
        domain: 'Product'
    },
    business_analyst: {
        role: 'Business Analyst',
        required_skills: ['sql', 'tableau', 'requirements gathering', 'reporting'],
        experience_required: 3,
        domain: 'Analytics'
    }
};

function selectedMultiJobRoles() {
    return Array.from(
        document.querySelectorAll('#multiJobRoles input[type=checkbox]:checked')
    ).map(el => el.value);
}

async function runMultiJobAnalysis() {
    const res = document.getElementById('multiJobResult');
    const roles = selectedMultiJobRoles();

    if (roles.length === 0) {
        res.innerHTML = '<p class="empty-hint">Select at least one role to compare.</p>';
        return;
    }

    res.innerHTML = '<p class="empty-hint">Running multi-job analysis...</p>';
    res.classList.add('active');

    const jobs = {};
    roles.forEach(key => {
        const t = MULTI_JOB_ROLES[key];
        jobs[key] = { job_profile: { ...t } };
    });

    try {
        const r = await fetch(API_BASE + '/api/multi-job-analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ jobs })
        });
        const data = await r.json();
        if (!r.ok) throw new Error(data.error || 'Multi-job analysis failed');

        const perJob = data.job_results || data.results || {};
        const entries = Array.isArray(perJob) ? perJob : Object.entries(perJob).map(([k, v]) => ({ job: v.job || k, ...v }));

        let html = `<h4>🎯 Multi-Job Analysis</h4>
            <div class="metric-grid">
                <div class="metric-item"><div class="metric-value">${data.total_jobs_analyzed ?? roles.length}</div><div class="metric-label">Roles</div></div>
                <div class="metric-item"><div class="metric-value">${Math.round((data.summary?.overall_average_score || 0) * (data.summary?.overall_average_score > 1 ? 100 : 1))}%</div><div class="metric-label">Avg Score</div></div>
                <div class="metric-item"><div class="metric-value">${data.talent_overlap?.total_overlapping ?? 0}</div><div class="metric-label">Overlapping</div></div>
            </div>`;

        if (entries.length) {
            html += `<h4>📊 Per-Role Results</h4>`;
            entries.forEach(j => {
                const avg = j.average_score != null
                    ? (j.average_score > 1 ? j.average_score * 100 : j.average_score)
                    : 0;
                const top = (j.top_candidates || j.candidates || []).slice(0, 3);
                html += `<div class="job-result-card">
                    <div class="job-result-head">
                        <strong>${escapeHtml(j.job || j.role || 'Role')}</strong>
                        <span class="dashboard-badge">${(j.total_candidates ?? 0)} candidates • avg ${avg.toFixed(1)}%</span>
                    </div>
                    ${top.length ? top.map((c, i) => {
                        const name = c.name || c.candidate_name || 'Candidate';
                        const sc = c.score != null ? c.score : c.final_score;
                        return `<div class="tip-item">#${i + 1} ${escapeHtml(name)} — ${Math.round((sc || 0) * (sc > 1 ? 100 : 1))}%</div>`;
                    }).join('') : ''}
                    ${j.recommendation ? `<div class="highlight-item">💡 ${escapeHtml(j.recommendation)}</div>` : ''}
                </div>`;
            });
        }

        if (data.hiring_priorities?.length) {
            html += `<h4>📋 Hiring Priorities</h4>` + data.hiring_priorities.map(p => {
                const avg = (p.average_score || 0) * (p.average_score > 1 ? 100 : 1);
                return `<div class="tip-item"><strong>${escapeHtml(p.job || '')}</strong>: Avg ${avg.toFixed(1)}% (${p.total_candidates || 0} candidates) — ${escapeHtml(p.recommendation || '')}</div>`;
            }).join('');
        }

        if (data.talent_overlap?.overlapping_candidates?.length) {
            html += `<h4>🔄 Overlapping Talent</h4>` + data.talent_overlap.overlapping_candidates.slice(0, 5).map(c =>
                `<div class="highlight-item">${escapeHtml(c.name)}: ${(c.matched_roles || []).map(escapeHtml).join(', ')}</div>`
            ).join('');
        }

        res.innerHTML = html;
    } catch (e) {
        res.innerHTML = `<p class="empty-hint">Error: ${e.message}</p>`;
    }
}

function enableFeatureTabs() {
    const tab = document.getElementById('tabFeatures');
    if (tab) { tab.style.display = 'inline-flex'; tab.disabled = false; }
    populateFeatureSelects();
}

function downloadJSON(data, filename) {
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
}

// Download the current rankings as CSV, built from the same API_BASE as every
// other request (the old markup hardcoded http://127.0.0.1:5000).
async function downloadCSV() {
    if (!state.currentResults) { showToast('Run an analysis first', 'warning'); return; }
    const btn = document.getElementById('downloadBtn');
    const original = btn ? btn.innerHTML : null;
    if (btn) { btn.disabled = true; btn.innerHTML = '<span>⏳</span> Preparing...'; }
    try {
        const r = await fetch(API_BASE + '/api/download');
        if (!r.ok) throw new Error(`Server returned ${r.status}`);
        const blob = await r.blob();
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `ranked_candidates_${new Date().toISOString().slice(0, 10)}.csv`;
        a.click();
        URL.revokeObjectURL(url);
        showToast('📥 CSV downloaded!', 'success');
    } catch (e) {
        // Fall back to a client-side CSV built from the results we already hold.
        try {
            const rows = state.currentResults.ranked_candidates;
            const esc = v => `"${String(v == null ? '' : v).replace(/"/g, '""')}"`;
            const csv = [
                ['Rank', 'Name', 'Score', 'Skill Match', 'Experience', 'Projects', 'Semantic', 'Reason'].join(','),
                ...rows.map(c => [
                    c.rank, esc(c.candidate_name), (c.final_score * 100).toFixed(2) + '%',
                    ((c.scores.skill_match || 0) * 100).toFixed(1) + '%',
                    ((c.scores.experience_match || 0) * 100).toFixed(1) + '%',
                    ((c.scores.project_relevance || 0) * 100).toFixed(1) + '%',
                    ((c.scores.semantic_similarity || 0) * 100).toFixed(1) + '%',
                    esc(c.reason)
                ].join(','))
            ].join('\n');
            const url = URL.createObjectURL(new Blob([csv], { type: 'text/csv' }));
            const a = document.createElement('a');
            a.href = url;
            a.download = `ranked_candidates_${new Date().toISOString().slice(0, 10)}.csv`;
            a.click();
            URL.revokeObjectURL(url);
            showToast('📥 CSV downloaded (generated locally)', 'success');
        } catch (e2) {
            showToast(`❌ Download failed: ${e2.message}`, 'error');
        }
    } finally {
        if (btn) { btn.disabled = false; btn.innerHTML = original; }
    }
}

// Suggested prompts, each mapped 1:1 to an intent the Copilot handles.
const COPILOT_SUGGESTIONS = [
    'show top 3 candidates',
    'who should we hire',
    'who has python skills',
    'which skill is missing the most',
    'tell me about candidate 1',
    'compare candidate 1 and candidate 2',
    'summarize the candidate pool'
];

function askCopilot(q) {
    const input = document.getElementById('copilotQuery');
    if (input) input.value = q;
    sendCopilotQuery();
}

function renderCopilotSuggestions() {
    const box = document.getElementById('copilotSuggestions');
    if (!box) return;
    box.innerHTML = COPILOT_SUGGESTIONS.map(q =>
        `<button class="copilot-chip" onclick="askCopilot('${q.replace(/'/g, "\\'")}')">${escapeHtml(q)}</button>`
    ).join('');
}

// ==================== EXPORT ====================
function exportJSON() {
    if (!state.currentResults) { showToast('No results to export', 'warning'); return; }
    const data = {
        generated_at: new Date().toISOString(),
        total: state.currentResults.ranked_candidates.length,
        results: state.currentResults.ranked_candidates.map(c => ({
            rank: c.rank,
            name: c.candidate_name,
            score: c.final_score,
            scores: c.scores,
            summary: c.candidate_summary,
            potential: c.potential,
            skill_gaps: c.skill_gaps
        }))
    };
    downloadJSON(data, `ranked_candidates_${Date.now()}.json`);
    showToast('📋 JSON exported!', 'success');
}