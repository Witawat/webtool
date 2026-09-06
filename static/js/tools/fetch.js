(function () {
  const form = document.getElementById("tool-form");
  if (!form) return;
  const btn = document.getElementById("submit-btn");
  const result = document.getElementById("result");

  function parseHeaders(text) {
    const out = {};
    String(text || "")
      .split("\n")
      .forEach((line) => {
        const i = line.indexOf(":");
        if (i > 0) out[line.slice(0, i).trim()] = line.slice(i + 1).trim();
      });
    return out;
  }

  function readForm() {
    return {
      method: document.getElementById("method").value,
      url: document.getElementById("url").value.trim(),
      headers: parseHeaders(document.getElementById("headers").value),
      body: document.getElementById("body").value || null,
      follow_redirects: document.getElementById("follow").checked,
    };
  }

  function renderResult(el, data) {
    const esc = WebTool.esc;
    const i18n = WebTool.i18n;
    let html = '<div class="result-card">';
    html +=
      "<p>" +
      esc(data.method) +
      " " +
      esc(data.url) +
      ' → <span class="badge ' +
      (data.status < 400 ? "badge-ok" : "badge-err") +
      '">' +
      esc(data.status) +
      " " +
      esc(data.reason) +
      "</span></p>";
    if (data.final_url !== data.url) {
      html +=
        "<p>" +
        esc(i18n("result.fetch.final_url")) +
        ": <strong>" +
        esc(data.final_url) +
        "</strong></p>";
    }
    html +=
      "<p>" +
      esc(i18n("result.fetch.size")) +
      ": <strong>" +
      esc(data.size_bytes) +
      "</strong> · " +
      esc(i18n("result.fetch.time")) +
      ": <strong>" +
      esc(data.time_ms) +
      " ms</strong></p>";
    if (data.redirects.length) {
      html +=
        "<p>" +
        esc(i18n("result.fetch.redirects")) +
        ": <strong>" +
        esc(data.redirects.join(" → ")) +
        "</strong></p>";
    }
    html +=
      "<details><summary>" +
      esc(i18n("result.fetch.headers")) +
      '</summary><pre class="raw">' +
      esc(JSON.stringify(data.headers, null, 2)) +
      "</pre></details>";
    html +=
      "<details open><summary>" +
      esc(i18n("result.fetch.body")) +
      "</summary><pre class=\"raw\">" +
      esc(data.body) +
      (data.body_truncated ? "\n\n" + esc(i18n("result.fetch.body_truncated")) : "") +
      "</pre></details>";
    html += "</div>";
    el.innerHTML = html;
  }

  form.onsubmit = async (e) => {
    e.preventDefault();
    WebTool.showLoading(btn);
    result.innerHTML = "";
    try {
      const res = await WebTool.api("fetch", readForm());
      renderResult(result, res.data);
      const dur = document.createElement("p");
      dur.className = "duration";
      dur.textContent = WebTool.fmtDuration(res.duration_ms);
      result.appendChild(dur);
    } catch (err) {
      WebTool.showError(result, err);
    } finally {
      WebTool.stopLoading(btn);
    }
  };
})();
