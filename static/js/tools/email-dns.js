(function () {
  const form = document.getElementById("tool-form");
  if (!form) return;
  const btn = document.getElementById("submit-btn");
  const result = document.getElementById("result");

  const SUMMARY = {
    pass: ["badge-ok", "result.email-dns.summary_pass"],
    warn: ["badge-warn", "result.email-dns.summary_warn"],
    fail: ["badge-err", "result.email-dns.summary_fail"],
  };

  function section(el, html, data) {
    const esc = WebTool.esc;
    const i18n = WebTool.i18n;
    // MX
    html += "<p><strong>" + esc(i18n("result.email-dns.mx")) + "</strong></p>";
    if (data.mx.length) {
      html += '<table class="result-table"><tbody>';
      data.mx.forEach((m) => {
        html +=
          "<tr><td>" +
          esc(m.priority) +
          "</td><td>" +
          esc(m.host) +
          "</td></tr>";
      });
      html += "</tbody></table>";
    } else {
      html += '<p class="result-note">' + esc(i18n("result.email-dns.no_mx")) + "</p>";
    }
    // SPF / DKIM / DMARC
    const checks = [
      ["spf", "result.email-dns.spf"],
      ["dkim", "result.email-dns.dkim"],
      ["dmarc", "result.email-dns.dmarc"],
    ];
    checks.forEach(([key, labelKey]) => {
      const present = data[key].present;
      const badge = present
        ? '<span class="badge badge-ok">' + esc(i18n("result.email-dns.present")) + "</span>"
        : '<span class="badge badge-err">' + esc(i18n("result.email-dns.missing")) + "</span>";
      html += "<p>" + esc(i18n(labelKey)) + " " + badge;
      if (key === "spf" && data.spf.record) {
        html += ' <span class="mono">' + esc(data.spf.record) + "</span>";
      }
      if (key === "dmarc" && data.dmarc.record) {
        html += ' <span class="mono">' + esc(data.dmarc.record) + "</span>";
      }
      html += "</p>";
      if (key === "dkim" && data.dkim.records.length) {
        data.dkim.records.forEach((r) => {
          html +=
            "<p class=\"result-note\">" +
            esc(r.selector) +
            ' <span class="mono">' +
            esc(r.record) +
            "</span></p>";
        });
      }
    });
    return html;
  }

  function renderResult(el, data) {
    const esc = WebTool.esc;
    const i18n = WebTool.i18n;
    const [cls, labelKey] = SUMMARY[data.summary] || ["badge-warn", "result.email-dns.summary_warn"];
    let html = '<div class="result-card">';
    html +=
      "<p>" +
      esc(data.domain) +
      ' <span class="badge ' +
      cls +
      '">' +
      esc(i18n(labelKey)) +
      "</span></p>";
    html = section(el, html, data);
    html += "</div>";
    el.innerHTML = html;
  }

  form.onsubmit = async (e) => {
    e.preventDefault();
    WebTool.showLoading(btn);
    result.innerHTML = "";
    try {
      const res = await WebTool.api("email-dns", {
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
