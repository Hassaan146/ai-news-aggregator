const form = document.querySelector("#digestForm");
const results = document.querySelector("#results");
const resultTitle = document.querySelector("#resultTitle");
const resultMeta = document.querySelector("#resultMeta");
const methodBadge = document.querySelector("#methodBadge");
const previewEmail = document.querySelector("#previewEmail");
const sendEmail = document.querySelector("#sendEmail");
const emailPreview = document.querySelector("#emailPreview");
const startCheckout = document.querySelector("#startCheckout");
const stripeStatus = document.querySelector("#stripeStatus");

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  await loadDigests();
});

previewEmail.addEventListener("click", async () => {
  await buildEmailPreview(false);
});

sendEmail.addEventListener("click", async () => {
  const ok = window.confirm("Send a live email using Gmail SMTP?");
  if (!ok) return;
  await buildEmailPreview(true);
});

startCheckout.addEventListener("click", async () => {
  await createCheckout();
});

async function loadDigests() {
  setBusy("Loading");
  results.innerHTML = "";
  try {
    const data = await postJson("/api/digests", buildDigestPayload());
    renderDigestResponse(data);
  } catch (error) {
    showError(error.message);
  }
}

async function buildEmailPreview(sendLive) {
  const payload = {
    ...buildDigestPayload(),
    name: document.querySelector("#emailName").value.trim() || "Sample User",
    email: document.querySelector("#emailTo").value.trim(),
  };

  if (sendLive && !payload.email) {
    emailPreview.textContent = "Enter a Gmail address before sending.";
    return;
  }

  emailPreview.textContent = sendLive ? "Sending..." : "Building preview...";
  try {
    const data = await postJson(
      sendLive ? "/api/email/send" : "/api/email/preview",
      payload,
    );
    if (sendLive) {
      emailPreview.textContent = `Sent to ${data.to}\nSubject: ${data.subject}\nRanking: ${data.ranking_method}`;
      return;
    }
    emailPreview.textContent = `Subject: ${data.subject}\nRanking: ${data.ranking_method}\n\n${data.text_body}`;
  } catch (error) {
    emailPreview.textContent = error.message;
  }
}

async function createCheckout() {
  const payload = {
    name: document.querySelector("#stripeName").value.trim() || "Sample User",
    email: document.querySelector("#stripeEmail").value.trim(),
  };
  if (!payload.email) {
    stripeStatus.textContent = "Enter an email address before starting checkout.";
    return;
  }

  stripeStatus.textContent = "Opening Stripe Checkout for secure card entry...";
  try {
    const data = await postJson("/api/payments/checkout", payload);
    if (!data.url) {
      throw new Error("Stripe did not return a checkout URL.");
    }
    window.location.href = data.url;
  } catch (error) {
    stripeStatus.textContent = error.message;
  }
}

function buildDigestPayload() {
  return {
    profile_name: document.querySelector("#profileName").value,
    hours: Number(document.querySelector("#hours").value || 24),
    top_n: Number(document.querySelector("#topN").value || 10),
    use_llm: document.querySelector("#useLlm").checked,
    gemini_api_key: document.querySelector("#geminiKey").value.trim() || null,
    preferred_sources: csv("#sources"),
    keywords: csv("#keywords"),
    preferred_kinds: csv("#kinds"),
    excluded_keywords: csv("#excluded"),
  };
}

function csv(selector) {
  const value = document.querySelector(selector).value.trim();
  if (!value) return [];
  return value
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);
}

async function postJson(url, payload) {
  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.detail || "Request failed");
  }
  return data;
}

function renderDigestResponse(data) {
  methodBadge.className = `status ${data.ranking_method}`;
  methodBadge.textContent = data.ranking_method.toUpperCase();
  resultTitle.textContent = `${data.total_items} ranked digest items`;
  resultMeta.textContent = data.fallback_reason
    ? `Fallback reason: ${data.fallback_reason}`
    : `Profile: ${data.profile.name} | Last ${data.lookback_hours} hours`;

  if (!data.items.length) {
    results.innerHTML = `<div class="item">No digest rows found for this window.</div>`;
    return;
  }

  results.innerHTML = data.items.map(renderItem).join("");
}

function renderItem(item) {
  const badges = item.badges
    .map((badge) => `<span class="badge">${escapeHtml(badge.label)}: ${escapeHtml(badge.value)}</span>`)
    .join("");
  const date = item.published_at ? new Date(item.published_at).toLocaleString() : "No date";
  const reason = item.llm_reason ? `<p class="meta">LLM reason: ${escapeHtml(item.llm_reason)}</p>` : "";

  return `
    <article class="item">
      <div class="item-header">
        <div class="rank">${item.rank}</div>
        <div>
          <h3>${escapeHtml(item.title)}</h3>
          <p class="meta">${escapeHtml(item.source)} | ${escapeHtml(item.kind)} | ${date}</p>
        </div>
        <div class="score">${item.score}</div>
      </div>
      <p class="summary-text">${escapeHtml(item.summary)}</p>
      ${reason}
      <div class="badges">${badges}</div>
      <a href="${item.url}" target="_blank" rel="noreferrer">Open source</a>
    </article>
  `;
}

function setBusy(label) {
  methodBadge.className = "status";
  methodBadge.textContent = label;
  resultTitle.textContent = "Working...";
  resultMeta.textContent = "Fetching and ranking digests.";
}

function showError(message) {
  methodBadge.className = "status fallback";
  methodBadge.textContent = "ERROR";
  resultTitle.textContent = "Request failed";
  resultMeta.textContent = message;
  results.innerHTML = "";
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}
