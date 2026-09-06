(function () {
  const form = document.getElementById("tool-form");
  if (!form) return;
  const btn = document.getElementById("submit-btn");
  const result = document.getElementById("result");

  function readForm() {
    const types = Array.from(
      document.querySelectorAll('input[name="types"]:checked')
    ).map((cb) => cb.value);
    return {
      domain: document.getElementById("domain").value.trim(),
      types: types,
    };
  }

  function renderResult(el, data) {
    const esc = WebTool.esc;
    const i18n = WebTool.i18n;
    if (!data.records.length) {
      el.innerHTML =
        '<div class="result-card"><p>' +
        esc(i18n("result.dns.no_records")) +
        "</p></div>";
      return;
    }
    let html =
      '<div class="table-wrap"><table class="result-table"><thead><tr>';
    html += "<th>" + esc(i18n("result.dns.type")) + "</th>";
    html += "<th>" + esc(i18n("result.dns.name")) + "</th>";
    html += "<th>" + esc(i18n("result.dns.ttl")) + "</th>";
    html += "<th>" + esc(i18n("result.dns.value")) + "</th>";
    html += "</tr></thead><tbody>";
    data.records.forEach((r) => {
      html +=
        "<tr><td>" +
        esc(r.type) +
        "</td><td>" +
        esc(r.name) +
        "</td><td>" +
        esc(r.ttl) +
        '</td><td class="mono">' +
        esc(r.value) +
        "</td></tr>";
    });
    html += "</tbody></table></div>";
    if (data.reverse) {
      html +=
        '<p class="result-note">' +
        esc(i18n("result.dns.reverse")) +
        ": <strong>" +
        esc(data.reverse) +
        "</strong></p>";
    }
    el.innerHTML = html;
  }

  form.onsubmit = async (e) => {
    e.preventDefault();
    WebTool.showLoading(btn);
    result.innerHTML = "";
    try {
      const res = await WebTool.api("dns", readForm());
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
