(function () {
  const form = document.getElementById("tool-form");
  if (!form) return;
  const btn = document.getElementById("submit-btn");
  const result = document.getElementById("result");

  function readForm() {
    return {
      host: document.getElementById("host").value.trim(),
      port: parseInt(document.getElementById("port").value, 10),
    };
  }

  function renderResult(el, data) {
    const esc = WebTool.esc;
    const i18n = WebTool.i18n;
    let html = "";
    if (!data.connected) {
      html +=
        '<div class="alert-error">' +
        esc(i18n("result.ssl.not_connected")) +
        "</div>";
      el.innerHTML = html;
      return;
    }
    data.warnings.forEach((w) => {
      html +=
        '<div class="alert-error">' +
        esc(i18n("result.ssl.warn_" + w)) +
        "</div>";
    });
    html += '<div class="result-card">';
    html +=
      "<p>" +
      esc(i18n("result.ssl.protocol")) +
      ": <strong>" +
      esc(data.protocol || "—") +
      "</strong> · " +
      esc(i18n("result.ssl.cipher")) +
      ": <strong>" +
      esc(data.cipher || "—") +
      "</strong></p>";
    if (data.cert) {
      const c = data.cert;
      html += "<p>" + esc(i18n("result.ssl.subject")) + ": <strong>" + esc(c.subject_cn) + "</strong></p>";
      html += "<p>" + esc(i18n("result.ssl.issuer")) + ": <strong>" + esc(c.issuer) + "</strong></p>";
      if (c.sans.length) {
        html += "<p>" + esc(i18n("result.ssl.sans")) + ": <strong>" + esc(c.sans.join(", ")) + "</strong></p>";
      }
      html += "<p>" + esc(i18n("result.ssl.valid_from")) + ": <strong>" + esc(c.valid_from.replace("T", " ").slice(0, 19)) + "</strong></p>";
      html += "<p>" + esc(i18n("result.ssl.valid_to")) + ": <strong>" + esc(c.valid_to.replace("T", " ").slice(0, 19)) + "</strong></p>";
      html += "<p>" + esc(i18n("result.ssl.days_left")) + ": <strong>" + esc(c.days_left) + "</strong></p>";
      html += "<p>" + esc(i18n("result.ssl.serial")) + ': <strong class="mono">' + esc(c.serial) + "</strong></p>";
      html += "<p>" + esc(i18n("result.ssl.sig_algo")) + ": <strong>" + esc(c.sig_algo) + "</strong></p>";
    }
    html += "</div>";
    el.innerHTML = html;
  }

  form.onsubmit = async (e) => {
    e.preventDefault();
    WebTool.showLoading(btn);
    result.innerHTML = "";
    try {
      const res = await WebTool.api("ssl", readForm());
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
