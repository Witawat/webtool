(function () {
  const form = document.getElementById("tool-form");
  if (!form) return;
  const btn = document.getElementById("submit-btn");
  const result = document.getElementById("result");

  function renderResult(el, data) {
    const esc = WebTool.esc;
    const i18n = WebTool.i18n;
    if (!data.domains.length) {
      el.innerHTML =
        '<div class="result-card"><p>' +
        esc(i18n("result.reverse-ip.no_domains")) +
        "</p></div>";
      return;
    }
    let html = '<div class="result-card">';
    html +=
      "<p>" +
      esc(i18n("result.reverse-ip.count")) +
      ": <strong>" +
      esc(data.count) +
      "</strong></p>";
    html += "<p><strong>" + esc(i18n("result.reverse-ip.domains")) + "</strong></p>";
    html += '<table class="result-table"><tbody>';
    data.domains.forEach((d) => {
      html += "<tr><td>" + esc(d) + "</td></tr>";
    });
    html += "</tbody></table>";
    html += "</div>";
    el.innerHTML = html;
  }

  form.onsubmit = async (e) => {
    e.preventDefault();
    WebTool.showLoading(btn);
    result.innerHTML = "";
    try {
      const res = await WebTool.api("reverse-ip", {
        ip: document.getElementById("ip").value.trim(),
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
