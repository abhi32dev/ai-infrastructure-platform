let currentJobs = [];

async function fetchJobs() {
  const q = document.getElementById('inputQuery').value.trim();
  const res = await fetch(`/api/jobs?q=${encodeURIComponent(q)}&limit=200`);
  const data = await res.json();
  if (data.status === 'success') {
    currentJobs = data.jobs || [];
    renderJobs(currentJobs);
  }
}

function renderJobs(jobs) {
  const list = document.getElementById('jobList');
  document.getElementById('txtCount').innerText = `Showing ${jobs.length} jobs`;
  
  if (jobs.length === 0) {
    list.innerHTML = `
      <tr>
        <td colspan="5" class="px-6 py-12 text-center text-slate-500">
          No jobs found. Click "Fetch Live Openings" to aggregate fresh postings from Greenhouse, Ashby, and Lever!
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
  banner.innerText = '⚡ Aggregating live openings across Greenhouse, Ashby, and Lever APIs...';

  try {
    const res = await fetch('/api/harvest', { method: 'POST' });
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

function closeModal() {
  document.getElementById('descModal').classList.add('hidden');
}

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

document.addEventListener('DOMContentLoaded', fetchJobs);
