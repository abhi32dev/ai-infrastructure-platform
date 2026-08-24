let currentJobs = [];
let allCompanies = [];
let selectedCompanyNames = new Set();

async function init() {
  await loadCompanies();
  await fetchJobs();
}

async function loadCompanies() {
  try {
    const res = await fetch('/api/companies');
    const data = await res.json();
    if (data.status === 'success') {
      allCompanies = data.companies || [];
      // Default to selecting all companies initially
      if (selectedCompanyNames.size === 0) {
        allCompanies.forEach(c => selectedCompanyNames.add(c.name));
      }
      renderCompanyGrid();
      document.getElementById('companyCount').innerText = allCompanies.length;
    }
  } catch(e) {}
}

function renderCompanyGrid() {
  const grid = document.getElementById('companyCheckboxGrid');
  grid.innerHTML = allCompanies.map(c => `
    <label class="flex items-center space-x-2 bg-slate-950 border border-slate-800/80 p-2.5 rounded-lg cursor-pointer hover:border-slate-700 transition text-xs">
      <input type="checkbox" value="${escapeHtml(c.name)}" ${selectedCompanyNames.has(c.name) ? 'checked' : ''} onchange="toggleCompanySelection('${escapeHtml(c.name)}', this.checked)" class="rounded border-slate-800 text-emerald-500 focus:ring-emerald-500">
      <span class="font-semibold text-slate-200">${escapeHtml(c.name)}</span>
      <span class="text-[10px] text-slate-500 uppercase">(${escapeHtml(c.ats)})</span>
    </label>
  `).join('');
  updateSelectedCount();
}

function toggleCompanySelection(name, isChecked) {
  if (isChecked) selectedCompanyNames.add(name);
  else selectedCompanyNames.delete(name);
  updateSelectedCount();
  fetchJobs();
}

function selectAllCompanies(shouldSelect) {
  if (shouldSelect) {
    allCompanies.forEach(c => selectedCompanyNames.add(c.name));
  } else {
    selectedCompanyNames.clear();
  }
  renderCompanyGrid();
  fetchJobs();
}

function updateSelectedCount() {
  document.getElementById('selectedCompanyCount').innerText = `${selectedCompanyNames.size} of ${allCompanies.length} selected`;
}

async function fetchJobs() {
  const q = document.getElementById('inputQuery').value.trim();
  const loc = document.getElementById('inputLocation').value.trim();
  const ats = document.getElementById('atsSelect').value;
  const sort = document.getElementById('sortSelect').value;
  const minSal = document.getElementById('salarySelect').value;

  const compList = Array.from(selectedCompanyNames).join(',');
  const url = `/api/jobs?q=${encodeURIComponent(q)}&loc=${encodeURIComponent(loc)}&ats=${encodeURIComponent(ats)}&companies=${encodeURIComponent(compList)}&min_salary=${minSal}&sort_by=${sort}&limit=300`;

  try {
    const res = await fetch(url);
    const data = await res.json();
    if (data.status === 'success') {
      currentJobs = data.jobs || [];
      renderJobs(currentJobs);
    }
  } catch(e) {}
}

function renderJobs(jobs) {
  const list = document.getElementById('jobList');
  document.getElementById('txtCount').innerText = `Showing ${jobs.length} target openings`;

  if (jobs.length === 0) {
    list.innerHTML = `
      <tr>
        <td colspan="5" class="px-6 py-12 text-center text-slate-500">
          No openings match your current search criteria. Click "Fetch Selected Openings" to update target feeds!
        </td>
      </tr>`;
    return;
  }

  list.innerHTML = jobs.map((j, idx) => `
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
          Apply ↗
        </a>
      </td>
    </tr>
  `).join('');
}

async function triggerHarvest() {
  const btn = document.getElementById('btnHarvest');
  const banner = document.getElementById('statusBanner');
  btn.disabled = true;
  btn.classList.add('opacity-50');

  banner.className = 'mb-6 p-4 rounded-xl text-sm border bg-emerald-950/40 border-emerald-500/30 text-emerald-300 block';
  banner.innerText = '⚡ Aggregating target company APIs...';

  try {
    const compList = Array.from(selectedCompanyNames);
    const res = await fetch('/api/harvest', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ companies: compList })
    });
    const data = await res.json();
    banner.innerText = `✅ ${data.message || 'Harvest completed!'}`;
    await fetchJobs();
  } catch (e) {
    banner.className = 'mb-6 p-4 rounded-xl text-sm border bg-rose-950/40 border-rose-500/30 text-rose-300 block';
    banner.innerText = `[!] Error harvesting jobs: ${e.message}`;
  } finally {
    btn.disabled = false;
    btn.classList.remove('opacity-50');
  }
}

async function addCustomCompany() {
  const name = document.getElementById('addCompName').value.trim();
  const ats = document.getElementById('addCompAts').value;
  const token = document.getElementById('addCompToken').value.trim();
  if (!name || !token) return alert('Please enter company name and board token!');

  const res = await fetch('/api/companies', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ action: 'add', name, ats, token })
  });
  const data = await res.json();
  if (data.status === 'success') {
    selectedCompanyNames.add(name);
    await loadCompanies();
    document.getElementById('addCompName').value = '';
    document.getElementById('addCompToken').value = '';
    alert(`Added ${name} to target list!`);
  }
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
      <div><strong>Resume File:</strong> <span class="text-emerald-400 font-mono">Abhishek_Singh_Resume.html</span></div>
    </div>
  `;
  document.getElementById('profileModal').classList.remove('hidden');
}

function closeProfileModal() { document.getElementById('profileModal').classList.add('hidden'); }
function openCompanyModal() { document.getElementById('companyModal').classList.remove('hidden'); }
function closeCompanyModal() { document.getElementById('companyModal').classList.add('hidden'); }

function setQuery(q) {
  document.getElementById('inputQuery').value = q;
  fetchJobs();
}

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
  a.download = `openings_aggregator_${currentJobs.length}_jobs.csv`;
  document.body.appendChild(a); a.click(); a.remove();
}

function escapeHtml(str) {
  return String(str || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

document.addEventListener('DOMContentLoaded', init);
