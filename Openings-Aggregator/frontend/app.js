let currentJobs = [];
let viewMode = 'batch50';
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

    return `
      <tr class="hover:bg-slate-800/50 transition">
        <!-- 1. Company & ATS Badge -->
        <td class="px-5 py-4 font-bold text-slate-200">
          <div>${escapeHtml(j.company)}</div>
          <span class="inline-block mt-1 px-2 py-0.5 rounded text-[10px] uppercase font-mono ${getAtsBadgeClass(j.ats_provider)}">
            ${escapeHtml(j.ats_provider)}
          </span>
        </td>

        <!-- 2. Job Title -->
        <td class="px-5 py-4 font-semibold text-slate-100">
          ${escapeHtml(j.title)}
        </td>

        <!-- 3. Date Posted -->
        <td class="px-5 py-4 text-xs text-slate-400 font-mono">
          ${escapeHtml(dateStr)}
        </td>

        <!-- 4. Salary Band -->
        <td class="px-5 py-4 text-xs font-semibold text-emerald-400">
          ${escapeHtml(salaryStr)}
        </td>

        <!-- 5. Location & Work Type -->
        <td class="px-5 py-4 text-xs">
          <div class="text-slate-300 font-medium">${escapeHtml(j.location)}</div>
          <div class="mt-1">${workTypePill}</div>
        </td>

        <!-- 6. Hover & Click Description Popover -->
        <td class="px-5 py-4 text-xs text-slate-400 max-w-md cursor-pointer hover:text-slate-200 transition"
            title="${escapeAttr(j.description)}"
            onclick="openModal(${idx})">
          <div class="line-clamp-2 bg-slate-950/60 p-2 rounded-lg border border-slate-800/80 hover:border-emerald-500/40 transition">
            ${escapeHtml(j.description)}
          </div>
          <span class="text-[10px] text-emerald-400 mt-1 inline-block font-semibold">🔍 Click to inspect full window</span>
        </td>

        <!-- 7. Direct ⚡ Auto-Apply Action -->
        <td class="px-5 py-4 text-right">
          <a href="${escapeHtml(j.apply_url)}" target="_blank" 
             class="bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold px-3.5 py-2 rounded-lg text-xs shadow-lg shadow-emerald-500/20 transition inline-flex items-center space-x-1">
            <span>⚡ Auto-Apply</span>
            <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3"></path></svg>
          </a>
        </td>
      </tr>
    `;
  }).join('');
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
  let csv = 'data:text/csv;charset=utf-8,Company,Job Title,Date Posted,Salary,Location,ATS Engine,Apply URL,Description\n';
  currentJobs.forEach(j => {
    csv += `"${(j.company||'').replace(/"/g, '""')}","${(j.title||'').replace(/"/g, '""')}","${j.posted_date||'Recent'}","${formatSalary(j)}","${(j.location||'').replace(/"/g, '""')}","${j.ats_provider}","${j.apply_url}","${(j.description||'').replace(/"/g, '""')}"\n`;
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
