let currentJobs = [];
let viewMode = 'batch50'; // 'batch50' or 'all'
let currentPage = 1;
const BATCH_SIZE = 50;

async function init() {
  await triggerHarvest();
}

async function triggerHarvest() {
  const btn = document.getElementById('btnHarvest');
  const banner = document.getElementById('statusBanner');
  btn.disabled = true;
  btn.classList.add('opacity-50');

  const q = document.getElementById('inputQuery').value.trim();
  const loc = document.getElementById('inputLocation').value.trim();
  const minSal = parseInt(document.getElementById('salarySelect').value || "0");

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
  const totalCount = currentJobs.length;

  let displayJobs = currentJobs;
  if (viewMode === 'batch50') {
    const totalPages = Math.ceil(totalCount / BATCH_SIZE) || 1;
    const start = (currentPage - 1) * BATCH_SIZE;
    displayJobs = currentJobs.slice(start, start + BATCH_SIZE);

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
        <td colspan="5" class="px-6 py-12 text-center text-slate-500">
          No live US openings matched your search parameters. Click "Fetch All US Openings" to update target feeds!
        </td>
      </tr>`;
    return;
  }

  list.innerHTML = displayJobs.map((j, idx) => `
    <tr class="hover:bg-slate-800/40 transition">
      <td class="px-6 py-4 font-bold text-slate-200">${escapeHtml(j.company)}</td>
      <td class="px-6 py-4">
        <div class="font-semibold text-slate-100">${escapeHtml(j.title)}</div>
        <div class="text-xs text-slate-400 mt-0.5">${escapeHtml(j.location)}</div>
      </td>
      <td class="px-6 py-4 text-xs text-slate-400">${escapeHtml(j.location)}</td>
      <td class="px-6 py-4 text-xs">
        <span class="px-2.5 py-1 rounded-full font-medium ${getAtsBadgeClass(j.ats_provider)}">
          ${escapeHtml(j.ats_provider)}
        </span>
      </td>
      <td class="px-6 py-4 text-right space-x-2">
        <button onclick="openModal(${idx})" class="text-xs bg-slate-800 hover:bg-slate-700 text-slate-200 px-3 py-1.5 rounded-lg border border-slate-700 transition">
          View Desc
        </button>
        <a href="${escapeHtml(j.apply_url)}" target="_blank" class="text-xs bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-400 font-semibold px-3 py-1.5 rounded-lg border border-emerald-500/30 transition inline-block">
          ⚡ Auto-Apply ↗
        </a>
      </td>
    </tr>
  `).join('');
}

async function openProfileModal() {
  const res = await fetch('/api/profile');
  const data = await res.json();
  const p = data.profile || {};
  const pers = p.personal || {};
  const auth = p.work_authorization || {};

  document.getElementById('profileBody').innerHTML = `
    <div class="bg-slate-950 p-4 rounded-xl border border-slate-800 space-y-2 text-xs">
      <div class="font-bold text-slate-100 text-sm mb-1">${escapeHtml(pers.fullName || 'Abhishek Singh')}</div>
      <div><strong>Email:</strong> ${escapeHtml(pers.email)}</div>
      <div><strong>Phone:</strong> ${escapeHtml(pers.phone)}</div>
      <div><strong>Location:</strong> ${escapeHtml(pers.currentLocation)}</div>
      <div><strong>US Authorization:</strong> ${escapeHtml(auth.legallyAuthorizedUS)} (Sponsorship: ${escapeHtml(auth.requireSponsorship)})</div>
      <div><strong>Resume Vault:</strong> <span class="text-emerald-400 font-mono">Abhishek_Singh_Resume.html</span></div>
    </div>
  `;
  document.getElementById('profileModal').classList.remove('hidden');
}

function closeProfileModal() { document.getElementById('profileModal').classList.add('hidden'); }

function openModal(idx) {
  const j = currentJobs[idx];
  if (!j) return;
  document.getElementById('modalTitle').innerText = j.title;
  document.getElementById('modalSub').innerText = `${j.company} • ${j.location} (${j.ats_provider})`;
  document.getElementById('modalBody').innerText = j.description || 'No description provided.';
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
  let csv = 'data:text/csv;charset=utf-8,Company,Job Title,Location,ATS Engine,Apply URL,Description\n';
  currentJobs.forEach(j => {
    csv += `"${(j.company||'').replace(/"/g, '""')}","${(j.title||'').replace(/"/g, '""')}","${(j.location||'').replace(/"/g, '""')}","${j.ats_provider}","${j.apply_url}","${(j.description||'').replace(/"/g, '""')}"\n`;
  });
  const a = document.createElement('a');
  a.href = encodeURI(csv);
  a.download = `openings_${currentJobs.length}_jobs.csv`;
  document.body.appendChild(a); a.click(); a.remove();
}

function escapeHtml(str) {
  return String(str || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

document.addEventListener('DOMContentLoaded', init);
