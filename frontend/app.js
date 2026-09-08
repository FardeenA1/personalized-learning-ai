async function loadStyleProfiles() {
  const listEl = document.getElementById("profileList");
  const emptyEl = document.getElementById("emptyState");

  try {
    const response = await fetch(`${API_BASE}/style`, {
      headers: { "Authorization": `Bearer ${getToken()}` }
    });

    if (response.status === 401) {
      logout();
      return;
    }

    if (response.status === 404) {
      listEl.innerHTML = "";
      emptyEl.classList.remove("hidden");
      return;
    }

    const profiles = await response.json();
    emptyEl.classList.add("hidden");

    listEl.innerHTML = profiles.map(p => `
      <div class="card" style="display:flex; align-items:center; justify-content:space-between; margin-bottom:14px;">
        <div>
          <span class="tag">${p.subject}</span>
          <p class="text-soft" style="font-size:0.82rem; margin-top:8px; margin-bottom:0;">
            Updated ${new Date(p.updated_at).toLocaleDateString()}
          </p>
        </div>
        <div style="display:flex; gap:10px;">
          <a href="generate.html?subject=${encodeURIComponent(p.subject)}" class="btn btn-ghost">Generate notes →</a>
          <button class="btn btn-ghost" style="color: var(--coral); border-color: var(--coral);" onclick="deleteProfile('${p.subject}')">Delete</button>
        </div>
      </div>
    `).join("");

  } catch (err) {
    listEl.innerHTML = `<div class="error-box">Could not load your style profiles. Is the backend running?</div>`;
  }
}

async function deleteProfile(subject) {
  if (!confirm(`Delete your style profile for "${subject}"? This can't be undone.`)) return;

  try {
    const response = await fetch(`${API_BASE}/style/${encodeURIComponent(subject)}`, {
      method: "DELETE",
      headers: { "Authorization": `Bearer ${getToken()}` }
    });

    if (!response.ok) {
      const data = await response.json();
      throw new Error(data.detail || "Delete failed.");
    }

    loadStyleProfiles();

  } catch (err) {
    alert(err.message);
  }
}

async function handleUpload(event) {
  event.preventDefault();
  hideError();

  const subject = document.getElementById("subject").value.trim();
  const fileInput = document.getElementById("files");
  const button = document.getElementById("uploadBtn");

  if (!fileInput.files.length) {
    showError("Please select at least one file.");
    return;
  }

  const formData = new FormData();
  formData.append("subject", subject);
  for (const file of fileInput.files) {
    formData.append("files", file);
  }

  setLoading(button, true);

  try {
    const response = await fetch(`${API_BASE}/style/upload`, {
      method: "POST",
      headers: { "Authorization": `Bearer ${getToken()}` },
      body: formData
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || "Upload failed.");
    }

    document.getElementById("uploadForm").reset();
    document.getElementById("uploadCard").classList.add("hidden");
    loadStyleProfiles();

  } catch (err) {
    showError(err.message);
  } finally {
    setLoading(button, false, "Analyze my style →");
  }
}

function toggleUploadCard() {
  document.getElementById("uploadCard").classList.toggle("hidden");
}

// ---------------- GENERATE ----------------

function prefillSubjectFromUrl() {
  const params = new URLSearchParams(window.location.search);
  const subject = params.get("subject");
  if (subject) {
    document.getElementById("genSubject").value = subject;
  }
}

async function handleGenerate(event) {
  event.preventDefault();
  hideError();

  const subject = document.getElementById("genSubject").value.trim();
  const topic = document.getElementById("genTopic").value.trim();
  const mode = document.getElementById("genMode").value;
  const sourceContent = document.getElementById("genContent").value.trim();
  const fileInput = document.getElementById("genFile");
  const button = document.getElementById("generateBtn");
  const outputCard = document.getElementById("outputCard");


  const formData = new FormData();
  formData.append("subject", subject);
  formData.append("topic", topic);
  formData.append("mode", mode);
  if (sourceContent) formData.append("source_content", sourceContent);
  if (fileInput.files.length) formData.append("file", fileInput.files[0]);

  setLoading(button, true);
  outputCard.classList.add("hidden");

  try {
    const response = await fetch(`${API_BASE}/generate/notes`, {
      method: "POST",
      headers: { "Authorization": `Bearer ${getToken()}` },
      body: formData
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || "Generation failed.");
    }

    
    showTab('styled');
    outputCard.classList.remove("hidden");
    document.getElementById("outputSubject").textContent = data.subject;
    document.getElementById("outputTopic").textContent = data.topic;
    document.getElementById("outputText").textContent = data.generated_notes;
    document.getElementById("rawOutputText").textContent = data.raw_notes;

    renderStyleChart(data.style_match.breakdown, data.style_match.overall_match);
    const b = data.style_match.breakdown;
    document.getElementById("matchBreakdown").textContent =
      `complexity ${b.complexity}% · paragraphs ${b.paragraph_style}% · bullets ${b.bullets}% · numbering ${b.numbering}%`;

    showTab('styled');
    document.getElementById("outputPlaceholder").classList.add("hidden");
    outputCard.classList.remove("hidden");



  } catch (err) {
    showError(err.message);
  } finally {
    setLoading(button, false, "Generate my notes →");
  }
}
function showTab(which) {
  const styledText = document.getElementById("outputText");
  const rawText = document.getElementById("rawOutputText");
  const styledBtn = document.getElementById("styledTabBtn");
  const rawBtn = document.getElementById("rawTabBtn");

  if (which === 'styled') {
    styledText.classList.remove("hidden");
    rawText.classList.add("hidden");
    styledBtn.classList.add("active");
    rawBtn.classList.remove("active");
  } else {
    styledText.classList.add("hidden");
    rawText.classList.remove("hidden");
    styledBtn.classList.remove("active");
    rawBtn.classList.add("active");
  }
}
// ---------------- ADMIN ----------------

async function requireAdmin() {
  try {
    const response = await fetch(`${API_BASE}/users/me`, {
      headers: { "Authorization": `Bearer ${getToken()}` }
    });

    if (response.status === 401) {
      logout();
      return;
    }

    const user = await response.json();

    if (!user.is_admin) {
      window.location.href = "dashboard.html";
      return;
    }

    loadAdminUsers();

  } catch (err) {
    window.location.href = "dashboard.html";
  }
}

async function loadAdminUsers() {
  const wrap = document.getElementById("adminTableWrap");

  try {
    const response = await fetch(`${API_BASE}/admin/users`, {
      headers: { "Authorization": `Bearer ${getToken()}` }
    });

    const users = await response.json();

    if (!response.ok) {
      throw new Error(users.detail || "Could not load users.");
    }

    document.getElementById("userCountLabel").textContent = `${users.length} registered user${users.length === 1 ? '' : 's'}`;

    wrap.innerHTML = `
      <div class="card" style="padding: 0; overflow: hidden;">
        <table style="width: 100%; border-collapse: collapse;">
          <thead>
            <tr style="border-bottom: 1px solid var(--rule); text-align: left;">
              <th style="padding: 14px 20px; font-size: 0.82rem; color: var(--ink-soft);">Name</th>
              <th style="padding: 14px 20px; font-size: 0.82rem; color: var(--ink-soft);">Email</th>
              <th style="padding: 14px 20px; font-size: 0.82rem; color: var(--ink-soft);">Subjects</th>
              <th style="padding: 14px 20px; font-size: 0.82rem; color: var(--ink-soft);">Joined</th>
              <th style="padding: 14px 20px; font-size: 0.82rem; color: var(--ink-soft);"></th>
            </tr>
          </thead>
          <tbody>
            ${users.map(u => `
              <tr style="border-bottom: 1px solid var(--rule);">
                <td style="padding: 14px 20px; font-size: 0.9rem;">
                  ${u.full_name} ${u.is_admin ? '<span class="tag" style="margin-left:6px;">admin</span>' : ''}
                </td>
                <td style="padding: 14px 20px; font-size: 0.9rem;" class="text-soft">${u.email}</td>
                <td style="padding: 14px 20px; font-size: 0.85rem;">
                  ${u.subjects.length ? u.subjects.map(s => `<span class="tag" style="margin-right:4px;">${s}</span>`).join('') : '<span class="text-soft">none</span>'}
                </td>
                <td style="padding: 14px 20px; font-size: 0.85rem;" class="text-soft mono">
                  ${new Date(u.created_at).toLocaleDateString()}
                </td>
                <td style="padding: 14px 20px; text-align: right;">
                  ${u.is_admin ? '' : `<button class="btn btn-ghost" style="color: var(--coral); border-color: var(--coral); padding: 6px 14px; font-size: 0.82rem;" onclick="deleteUser(${u.id}, '${u.email}')">Remove</button>`}
                </td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>
    `;

  } catch (err) {
    wrap.innerHTML = `<div class="error-box">${err.message}</div>`;
  }
}

async function deleteUser(userId, email) {
  if (!confirm(`Remove user "${email}"? This deletes their account and all their style profiles permanently.`)) return;

  try {
    const response = await fetch(`${API_BASE}/admin/users/${userId}`, {
      method: "DELETE",
      headers: { "Authorization": `Bearer ${getToken()}` }
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || "Delete failed.");
    }

    loadAdminUsers();

  } catch (err) {
    alert(err.message);
  }
}
async function showAdminLinkIfAdmin() {
  try {
    const response = await fetch(`${API_BASE}/users/me`, {
      headers: { "Authorization": `Bearer ${getToken()}` }
    });
    const user = await response.json();
    if (user.is_admin) {
      document.getElementById("adminLink").classList.remove("hidden");
    }
  } catch (err) {}
}
function renderStyleChart(breakdown, overall) {
  const wrap = document.getElementById("styleChartWrap");

  const axes = [
    { key: "complexity", label: "Complexity" },
    { key: "paragraph_style", label: "Paragraphs" },
    { key: "bullets", label: "Bullets" },
    { key: "numbering", label: "Numbering" }
  ];

  const cx = 110, cy = 110, maxR = 78;
  const n = axes.length;

  function pointOn(angleDeg, r) {
    const rad = ((angleDeg - 90) * Math.PI) / 180;
    return { x: cx + r * Math.cos(rad), y: cy + r * Math.sin(rad) };
  }

  let gridRings = "";
  [0.25, 0.5, 0.75, 1].forEach(fraction => {
    const pts = axes.map((_, i) => {
      const angle = i * (360 / n);
      const p = pointOn(angle, maxR * fraction);
      return `${p.x},${p.y}`;
    }).join(" ");
    gridRings += `<polygon points="${pts}" fill="none" stroke="var(--rule)" stroke-width="1"/>`;
  });

  let axisLines = "";
  let axisLabels = "";
  axes.forEach((axis, i) => {
    const angle = i * (360 / n);
    const end = pointOn(angle, maxR);
    const labelPos = pointOn(angle, maxR + 22);
    axisLines += `<line x1="${cx}" y1="${cy}" x2="${end.x}" y2="${end.y}" stroke="var(--rule)" stroke-width="1"/>`;
    axisLabels += `<text x="${labelPos.x}" y="${labelPos.y}" text-anchor="middle" dominant-baseline="middle" font-family="var(--font-mono)" font-size="10" fill="var(--ink-soft)">${axis.label}</text>`;
  });

  const dataPoints = axes.map((axis, i) => {
    const angle = i * (360 / n);
    const value = breakdown[axis.key] || 0;
    const r = maxR * (value / 100);
    const p = pointOn(angle, r);
    return `${p.x},${p.y}`;
  }).join(" ");

  const dataDots = axes.map((axis, i) => {
    const angle = i * (360 / n);
    const value = breakdown[axis.key] || 0;
    const r = maxR * (value / 100);
    const p = pointOn(angle, r);
    return `<circle cx="${p.x}" cy="${p.y}" r="3.5" fill="var(--ink)"/>`;
  }).join("");

  const svg = `
    <svg width="220" height="220" viewBox="0 0 220 220">
      ${gridRings}
      ${axisLines}
      <polygon points="${dataPoints}" fill="rgba(244,183,64,0.28)" stroke="var(--amber)" stroke-width="2.5"/>
      ${dataDots}
      ${axisLabels}
      <text x="${cx}" y="${cy - 4}" text-anchor="middle" font-family="var(--font-display)" font-weight="600" font-size="24" fill="var(--ink)">${overall}%</text>
      <text x="${cx}" y="${cy + 14}" text-anchor="middle" font-family="var(--font-mono)" font-size="9" fill="var(--ink-soft)">MATCH</text>
    </svg>
  `;

  wrap.innerHTML = svg;
}