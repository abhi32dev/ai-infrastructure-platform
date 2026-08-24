let currentJobs = [];
let viewMode = 'batch50';
let currentPage = 1;
const BATCH_SIZE = 50;

async function init() {
  renderRecentChips();
  await triggerHarvest();
}

function saveRecentFilter(queryStr) {
  if (!queryStr || queryStr.trim().length === 0) return;
  const q = queryStr.trim();
  let recent = JSON.parse(localStorage.getItem('oa_recent_filters') || '[]');
  recent = recent.filter(item => item.toLowerCase() !== q.toLowerCase());
  recent.unshift(q);
  recent = recent.slice(0, 2);
  localStorage.setItem('oa_recent_filters', JSON.stringify(recent));
  renderRecentChips();
}

function renderRecentChips() {
  const container = document.getElementById('recentChips');
  if (!container) return;
  const recent = JSON.parse(localStorage.getItem('oa_recent_filters') || '[]');

  if (recent.length === 0) {
    container.innerHTML = `<span class="text-slate-600 italic">No recent searches saved yet</span>`;
    return;
  }

  container.innerHTML = recent.map(q => `
    <button onclick="applyRecentSkillMemory('${escapeAttr(q)}')" 
            class="bg-emerald-950/70 hover:bg-emerald-900/80 text-emerald-300 border border-emerald-500/30 px-3 py-1 rounded-lg text-xs font-semibold flex items-center space-x-1 transition shadow-sm">
      <span>"${escapeHtml(q)}"</span>
      <span class="text-[10px] text-emerald-400">↺</span>
    </button>
  `).join('');
}

function applyRecentSkillMemory(q) {
  document.getElementById('inputQuery').value = q;
  triggerHarvest();
}

async function triggerHarvest() {
  const btn = document.getElementById('btnHarvest');
  const banner = document.getElementById('statusBanner');
  btn.disabled = true;
  btn.classList.add('opacity-50');

  const q = document.getElementById('inputQuery').value.trim();
  const loc = document.getElementById('inputLocation').value.trim();
  const minSal = parseInt(document.getElementById('salarySelect').value || "0");

  if (q) saveRecentFilter(q);

  banner.className = 'mb-6 p-4 rounded-xl text-sm border bg-emerald-950/60 border-emerald-500/40 text-emerald-300 block flex items-center space-x-3';
  banner.innerHTML = `
    <div class="w-4 h-4 rounded-full border-2 border-emerald-400 border-t-transparent animate-spin"></div>
    <span>⚡ Triggering live backend API harvest across all company endpoints...</span>
  `;

  try {
    const res = await fetch('/api/harvest', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        query: q,
        location: loc,
        min_salary: minSal
      })
    });
    const data = await res.json();
    banner.className = 'mb-6 p-4 rounded-xl text-sm border bg-emerald-950/40 border-emerald-500/30 text-emerald-300 block';
    banner.innerText = `✅ ${data.message || 'Live API Harvest Complete!'}`;
    
    currentJobs = data.jobs || [];
    currentPage = 1;
    renderJobs();
  } catch (e) {
    banner.className = 'mb-6 p-4 rounded-xl text-sm border bg-rose-950/40 border-rose-500/30 text-rose-300 block';
    banner.innerText = `[!] Error connecting to live backend: ${e.message}`;
  } finally {
    btn.disabled = false;
    btn.classList.remove('opacity-50');
  }
}

async function fetchJobs() {
  const q = document.getElementById('inputQuery').value.trim();
  const loc = document.getElementById('inputLocation').value.trim();
  const ats = document.getElementById('atsSelect').value;
  const sort = document.getElementById('sortSelect').value;
  const minSal = document.getElementById('salarySelect').value;

  const url = `/api/jobs?q=${encodeURIComponent(q)}&loc=${encodeURIComponent(loc)}&ats=${encodeURIComponent(ats)}&min_salary=${minSal}&sort_by=${sort}&limit=500`;

  try {
    const res = await fetch(url);
    const data = await res.json();
    if (data.status === 'success') {
      currentJobs = data.jobs || [];
      currentPage = 1;
      renderJobs();
    }
  } catch(e) {}
}

function setViewMode(mode) {
  viewMode = mode;
  document.getElementById('tabBatch50').className = mode === 'batch50' 
    ? 'px-4 py-1.5 rounded-lg bg-emerald-500 text-slate-950 font-bold transition'
    : 'px-4 py-1.5 rounded-lg text-slate-400 hover:text-slate-200 transition';

  document.getElementById('tabAll').className = mode === 'all'
    ? 'px-4 py-1.5 rounded-lg bg-emerald-500 text-slate-950 font-bold transition'
    : 'px-4 py-1.5 rounded-lg text-slate-400 hover:text-slate-200 transition';

  document.getElementById('paginationControls').style.display = mode === 'batch50' ? 'flex' : 'none';
  currentPage = 1;
  renderJobs();
}

function changePage(delta) {
  const totalPages = Math.ceil(currentJobs.length / BATCH_SIZE) || 1;
  currentPage += delta;
  if (currentPage < 1) currentPage = 1;
  if (currentPage > totalPages) currentPage = totalPages;
  renderJobs();
}

function renderJobs() {
  const list = document.getElementById('jobList');
  const atsFilter = document.getElementById('atsSelect').value;

  // Filter current jobs by ATS engine if selected
  let filteredJobs = currentJobs;
  if (atsFilter) {
    filteredJobs = currentJobs.filter(j => j.ats_provider === atsFilter);
  }

  const totalCount = filteredJobs.length;

  let displayJobs = filteredJobs;
  if (viewMode === 'batch50') {
    const totalPages = Math.ceil(totalCount / BATCH_SIZE) || 1;
    const start = (currentPage - 1) * BATCH_SIZE;
    displayJobs = filteredJobs.slice(start, start + BATCH_SIZE);

    document.getElementById('txtCount').innerText = `Showing ${displayJobs.length} jobs (Batch ${currentPage} of ${totalPages} | Total US: ${totalCount})`;
    document.getElementById('pageIndicator').innerText = `Page ${currentPage} of ${totalPages}`;
    document.getElementById('btnPrev').disabled = (currentPage === 1);
    document.getElementById('btnNext').disabled = (currentPage === totalPages);
  } else {
    document.getElementById('txtCount').innerText = `Showing all ${totalCount} US jobs`;
  }

  if (displayJobs.length === 0) {
    list.innerHTML = `
      <tr>
        <td colspan="7" class="px-6 py-12 text-center text-slate-500">
          No live US openings matched your search parameters. Click "Fetch All US Openings" to update target feeds!
        </td>
      </tr>`;
    return;
  }

  list.innerHTML = displayJobs.map((j, idx) => {
    const salaryStr = formatSalary(j);
    const workTypePill = formatWorkType(j.location);
    const dateStr = j.posted_date || 'Recent';
    const cleanDesc = cleanClientText(j.description);

    return `
      <tr class="hover:bg-slate-800/60 transition border-b border-slate-800/80">
        <!-- 1. Company & ATS Badge -->
        <td class="px-5 py-5 font-bold text-slate-100 text-base align-top">
          <div class="tracking-tight">${escapeHtml(j.company)}</div>
          <span class="inline-block mt-1.5 px-2.5 py-0.5 rounded text-[11px] font-bold uppercase font-mono tracking-wider ${getAtsBadgeClass(j.ats_provider)}">
            ${escapeHtml(j.ats_provider)}
          </span>
        </td>

        <!-- 2. Job Title (Allows 2-Line Wrapping, Left-Aligned) -->
        <td class="px-5 py-5 text-left align-top">
          <div class="font-bold text-slate-100 text-base leading-snug break-words whitespace-normal">
            ${escapeHtml(j.title)}
          </div>
        </td>

        <!-- 3. Date Posted -->
        <td class="px-5 py-5 text-sm text-slate-300 font-mono align-top whitespace-nowrap">
          ${escapeHtml(dateStr)}
        </td>

        <!-- 4. Salary Band -->
        <td class="px-5 py-5 text-sm font-bold text-emerald-400 align-top whitespace-nowrap">
          ${escapeHtml(salaryStr)}
        </td>

        <!-- 5. Location & Work Type -->
        <td class="px-5 py-5 text-sm align-top whitespace-normal break-words">
          <div class="text-slate-200 font-semibold leading-snug">${escapeHtml(j.location)}</div>
          <div class="mt-1.5">${workTypePill}</div>
        </td>

        <!-- 6. Clean Description Preview (Hover Tooltip + Click Popover) -->
        <td class="px-5 py-5 text-sm text-slate-300 align-top cursor-pointer hover:text-slate-100 transition whitespace-normal break-words"
            title="${escapeAttr(cleanDesc)}"
            onclick="openModal(${idx})">
          <div class="line-clamp-3 bg-slate-950/80 p-3 rounded-xl border border-slate-800 hover:border-emerald-500/50 transition leading-relaxed text-xs text-slate-300">
            ${escapeHtml(cleanDesc)}
          </div>
          <div class="text-[11px] text-emerald-400 mt-1 font-bold flex items-center space-x-1">
            <span>🔍 Click to inspect full window</span>
          </div>
        </td>

async function triggerAutoApply(idx) {
  const j = currentJobs[idx];
  if (!j) return;

  // Record application in SQLite applied_tracker database
  try {
    await fetch('/api/tracker', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        action: 'record',
        id: j.id,
        company: j.company,
        title: j.title,
        location: j.location,
        apply_url: j.apply_url,
        applied_date: new Date().toISOString().split('T')[0],
        status: 'Applied',
        email_updates: 'Confirmation Pending'
      })
    });
  } catch(e) {}

  // Open direct application posting URL in a new tab
  window.open(j.apply_url, '_blank');
}

async function openTrackerModal() {
  await loadTrackerApplications();
  document.getElementById('trackerModal').classList.remove('hidden');
}

function closeTrackerModal() {
  document.getElementById('trackerModal').classList.add('hidden');
}

async function loadTrackerApplications() {
  try {
    const res = await fetch('/api/tracker');
    const data = await res.json();
    const apps = data.applications || [];

    // Calculate metrics
    document.getElementById('metricTotal').innerText = apps.length;
    document.getElementById('metricApplied').innerText = apps.filter(a => a.status === 'Applied' || a.status === 'In Review').length;
    document.getElementById('metricInterview').innerText = apps.filter(a => a.status === 'Interviewing').length;
    document.getElementById('metricOffer').innerText = apps.filter(a => a.status === 'Offer').length;

    const tbody = document.getElementById('trackerTableBody');
    if (apps.length === 0) {
      tbody.innerHTML = `
        <tr>
          <td colspan="6" class="px-6 py-8 text-center text-slate-500">
            No applications recorded yet. Click "⚡ Auto-Apply" on any job to track it live!
          </td>
        </tr>`;
      return;
    }

    tbody.innerHTML = apps.map(a => {
      const countBadge = (a.apply_count && a.apply_count > 1) 
        ? `<span class="ml-2 px-2 py-0.5 rounded text-[10px] font-bold bg-amber-500/20 text-amber-300 border border-amber-500/40">Applied ${a.apply_count}x</span>` 
        : '';

      const logsHtml = (a.audit_logs || []).map(l => 
        `<div class="text-[10px] text-slate-400 font-mono">• ${escapeHtml(l.timestamp)}: ${escapeHtml(l.action_type)}</div>`
      ).join('');

      return `
        <tr class="hover:bg-slate-800/60 transition border-b border-slate-800/80">
          <td class="px-4 py-3.5 font-bold text-slate-100 align-top">
            <div>${escapeHtml(a.company)}</div>
            <div>${countBadge}</div>
          </td>
          <td class="px-4 py-3.5 font-semibold text-slate-200 align-top">
            <div>${escapeHtml(a.title)}</div>
            <div class="mt-1 space-y-0.5">${logsHtml}</div>
          </td>
          <td class="px-4 py-3.5 text-xs text-slate-400 font-mono align-top">${escapeHtml(a.applied_date)}</td>
          <td class="px-4 py-3.5 text-xs align-top">
            <a href="${escapeHtml(a.apply_url)}" target="_blank" class="text-emerald-400 font-semibold hover:underline flex items-center space-x-1">
              <span>Direct Live Posting ↗</span>
            </a>
          </td>
          <td class="px-4 py-3.5 text-xs align-top">
            <span class="px-2.5 py-1 rounded-full font-bold ${getTrackerBadgeClass(a.status)}">
              ${escapeHtml(a.status)}
            </span>
          </td>
          <td class="px-4 py-3.5 text-right align-top">
            <select onchange="updateAppStatus('${escapeAttr(a.id)}', this.value)" class="bg-slate-950 border border-slate-800 rounded-lg px-2.5 py-1 text-xs text-slate-200 focus:outline-none focus:border-emerald-500">
              <option value="Applied" ${a.status === 'Applied' ? 'selected' : ''}>Applied</option>
              <option value="In Review" ${a.status === 'In Review' ? 'selected' : ''}>In Review</option>
              <option value="Interviewing" ${a.status === 'Interviewing' ? 'selected' : ''}>Interviewing</option>
              <option value="Offer" ${a.status === 'Offer' ? 'selected' : ''}>Offer</option>
              <option value="Rejected" ${a.status === 'Rejected' ? 'selected' : ''}>Rejected</option>
            </select>
          </td>
        </tr>
      `;
    }).join('');
  } catch(e) {}
}

async function updateAppStatus(appId, newStatus) {
  try {
    await fetch('/api/tracker', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: 'update_status', id: appId, status: newStatus })
    });
    await loadTrackerApplications();
  } catch(e) {}
}

function getTrackerBadgeClass(status) {
  if (status === 'Offer') return 'bg-teal-950 text-teal-300 border border-teal-800';
  if (status === 'Interviewing') return 'bg-amber-950 text-amber-300 border border-amber-800';
  if (status === 'In Review') return 'bg-indigo-950 text-indigo-300 border border-indigo-800';
  if (status === 'Rejected') return 'bg-rose-950 text-rose-300 border border-rose-800';
  return 'bg-emerald-950 text-emerald-300 border border-emerald-800';
}

function cleanClientText(str) {
  if (!str) return '';
  const doc = new DOMParser().parseFromString(str, 'text/html');
  let clean = doc.body.textContent || '';
  clean = clean.replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').strip ? clean.replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim() : clean.trim();
  return clean;
}

function formatSalary(j) {
  if (j.salary_max > 0) {
    const minK = Math.round(j.salary_min / 1000);
    const maxK = Math.round(j.salary_max / 1000);
    if (minK > 0 && minK !== maxK) return `$${minK}k - $${maxK}k / yr`;
    return `$${maxK}k / yr`;
  }
  return 'Competitive Pay';
}

function formatWorkType(locStr) {
  const loc = (locStr || '').toLowerCase();
  if (loc.includes('remote')) return '<span class="px-2 py-0.5 rounded text-[10px] font-semibold bg-emerald-950 text-emerald-400 border border-emerald-800">Remote</span>';
  if (loc.includes('hybrid')) return '<span class="px-2 py-0.5 rounded text-[10px] font-semibold bg-indigo-950 text-indigo-400 border border-indigo-800">Hybrid</span>';
  return '<span class="px-2 py-0.5 rounded text-[10px] font-semibold bg-slate-800 text-slate-300">On-Site / Office</span>';
}

async function openProfileModal() {
  const res = await fetch('/api/profile');
  const data = await res.json();
  const p = data.profile || {};
  const pers = p.personal || {};
  const auth = p.work_authorization || {};
  const pref = p.preferences || {};

  const defaultText = `FULL NAME: ${pers.fullName || 'Abhishek Singh'}
EMAIL: ${pers.email || 'asingh32us@gmail.com'}
PHONE: ${pers.phone || '(669) 203-9217'}
CURRENT LOCATION: ${pers.currentLocation || 'Fremont, CA, USA'}
LINKEDIN: ${pers.linkedin || 'https://linkedin.com/in/abhishek32'}
GITHUB: ${pers.github || 'https://github.com/abhi32dev'}

WORK AUTHORIZATION:
- Authorized to Work in US: ${auth.legallyAuthorizedUS || 'Yes'}
- Require Visa Sponsorship: ${auth.requireSponsorship || 'Yes'}
- Future Sponsorship: ${auth.futureSponsorship || 'Yes'}
- Visa Type: ${auth.visaStatus || 'Requires Sponsorship'}

PREFERENCES & INSTRUCTIONS:
- Hybrid Office Attendance: ${pref.hybridOfficeAttendance || 'Yes, 3+ days/week'}
- State of Residence: ${pref.stateOfResidence || 'California'}
- School Location: ${pref.schoolLocation || 'California, USA'}
- Notice Period: ${pref.noticePeriod || 'Immediate'}
`;

  document.getElementById('txtProfileNotepad').value = defaultText;
  document.getElementById('profileSaveBanner').classList.add('hidden');
  document.getElementById('profileModal').classList.remove('hidden');
}

async function saveProfileNotepad() {
  const text = document.getElementById('txtProfileNotepad').value;
  const banner = document.getElementById('profileSaveBanner');

  try {
    const res = await fetch('/api/profile', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ raw_text: text })
    });
    const data = await res.json();
    banner.innerText = '✅ Profile notes & vault updated successfully!';
    banner.classList.remove('hidden');
    setTimeout(() => banner.classList.add('hidden'), 3000);
  } catch (e) {
    banner.innerText = `[!] Error saving profile: ${e.message}`;
    banner.classList.remove('hidden');
  }
}

function closeProfileModal() { document.getElementById('profileModal').classList.add('hidden'); }

function openModal(idx) {
  const j = currentJobs[idx];
  if (!j) return;
  document.getElementById('modalTitle').innerText = j.title;
  document.getElementById('modalSub').innerText = `${j.company} • ${j.location} (${j.ats_provider}) • ${j.posted_date || 'Recent'}`;
  document.getElementById('modalBody').innerText = cleanClientText(j.description) || 'No description provided.';
  document.getElementById('modalApplyBtn').href = j.apply_url;
  document.getElementById('descModal').classList.remove('hidden');
}

function closeModal() { document.getElementById('descModal').classList.add('hidden'); }

function getAtsBadgeClass(ats) {
  if (ats === 'Greenhouse') return 'bg-emerald-950 text-emerald-400 border border-emerald-800';
  if (ats === 'Ashby') return 'bg-indigo-950 text-indigo-400 border border-indigo-800';
  if (ats === 'Lever') return 'bg-purple-950 text-purple-400 border border-purple-800';
  return 'bg-slate-800 text-slate-300';
}

function exportCSV() {
  if (currentJobs.length === 0) return alert('No jobs to export!');
  let csv = 'data:text/csv;charset=utf-8,Company,Job Title,Date Posted,Salary,Location,ATS Engine,Apply URL,Description\n';
  currentJobs.forEach(j => {
    csv += `"${(j.company||'').replace(/"/g, '""')}","${(j.title||'').replace(/"/g, '""')}","${j.posted_date||'Recent'}","${formatSalary(j)}","${(j.location||'').replace(/"/g, '""')}","${j.ats_provider}","${j.apply_url}","${(cleanClientText(j.description)| me).replace(/"/g, '""')}"\n`;
  });
  const a = document.createElement('a');
  a.href = encodeURI(csv);
  a.download = `openings_${currentJobs.length}_jobs.csv`;
  document.body.appendChild(a); a.click(); a.remove();
}

function escapeHtml(str) {
  return String(str || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

function escapeAttr(str) {
  return String(str || '').replace(/"/g, '&quot;').replace(/'/g, '&#39;');
}

document.addEventListener('DOMContentLoaded', init);
