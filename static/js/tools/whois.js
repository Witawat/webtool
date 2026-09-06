(function () {
  const form = document.getElementById("tool-form");
  if (!form) return;
  const btn = document.getElementById("submit-btn");
  const result = document.getElementById("result");

  function renderResult(el, data) {
    const esc = WebTool.esc;
    const i18n = WebTool.i18n;
    let html = '<div class="result-card">';
    if (data.tld_privacy) {
      html +=
        '<p class="result-note">' + esc(i18n("result.whois.tld_privacy")) + "</p>";
    }
    if (data.registrar) {
      html +=
        "<p>" +
        esc(i18n("result.whois.registrar")) +
        ": <strong>" +
        esc(data.registrar) +
        "</strong></p>";
    }
    if (data.created) {
      html +=
        "<p>" +
        esc(i18n("result.whois.created")) +
        ": <strong>" +
        esc(data.created.replace("T", " ").slice(0, 19)) +
        "</strong></p>";
    }
    if (data.updated) {
      html +=
        "<p>" +
        esc(i18n("result.whois.updated")) +
        ": <strong>" +
        esc(data.updated.replace("T", " ").slice(0, 19)) +
        "</strong></p>";
    }
    if (data.expires) {
      html +=
        "<p>" +
        esc(i18n("result.whois.expires")) +
        ": <strong>" +
        esc(data.expires.replace("T", " ").slice(0, 19)) +
        "</strong></p>";
    }
    if (data.status && data.status.length) {
      html +=
        "<p>" +
        esc(i18n("result.whois.status")) +
        ": <strong>" +
        esc(data.status.join(", ")) +
        "</strong></p>";
    }
    if (data.nameservers && data.nameservers.length) {
      html +=
        "<p>" +
        esc(i18n("result.whois.nameservers")) +
        ": <strong>" +
        esc(data.nameservers.join(", ")) +
        "</strong></p>";
    }
    if (data.raw_text) {
      html +=
        "<details><summary>" +
        esc(i18n("result.whois.raw_text")) +
        '</summary><pre class="raw">' +
        esc(data.raw_text) +
        "</pre></details>";
    }
    if (!data.registrar && !data.created && !data.raw_text) {
      html += "<p>" + esc(i18n("result.whois.no_data")) + "</p>";
    }
    html += "</div>";
    el.innerHTML = html;
  }

  form.onsubmit = async (e) => {
    e.preventDefault();
    WebTool.showLoading(btn);
    result.innerHTML = "";
    try {
      const res = await WebTool.api("whois", {
        domain: document.getElementById("domain").value.trim(),
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
