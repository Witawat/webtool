(function () {
  const form = document.getElementById("tool-form");
  if (!form) return;
  const btn = document.getElementById("submit-btn");
  const result = document.getElementById("result");

  function renderResult(el, data) {
    const esc = WebTool.esc;
    const i18n = WebTool.i18n;
    let html = '<div class="result-card">';
    const badge = data.available
      ? '<span class="badge badge-ok">' + esc(i18n("result.email-lookup.available")) + "</span>"
      : '<span class="badge badge-err">' + esc(i18n("result.email-lookup.not_available")) + "</span>";
    html += "<p>" + esc(data.email) + " " + badge + "</p>";
    if (data.provider) {
      html +=
        "<p>" +
        esc(i18n("result.email-lookup.provider")) +
        ": <strong>" +
        esc(data.provider) +
        "</strong></p>";
    }
    if (data.result) {
      html +=
        "<p>" +
        esc(i18n("result.email-lookup.result")) +
        ': <pre class="raw">' +
        esc(JSON.stringify(data.result, null, 2)) +
        "</pre></p>";
    }
    html += "</div>";
    el.innerHTML = html;
  }

  form.onsubmit = async (e) => {
    e.preventDefault();
    WebTool.showLoading(btn);
    result.innerHTML = "";
    try {
      const res = await WebTool.api("email-lookup", {
        email: document.getElementById("email").value.trim(),
      });
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
