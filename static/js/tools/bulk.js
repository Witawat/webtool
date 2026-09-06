(function () {
  const form = document.getElementById("tool-form");
  if (!form) return;
  const btn = document.getElementById("submit-btn");
  const result = document.getElementById("result");

  function readForm() {
    const values = document
      .getElementById("values")
      .value.split("\n")
      .map((v) => v.trim())
      .filter(Boolean);
    return { slug: document.getElementById("slug").value, values: values };
  }

  function renderResult(el, data) {
    const esc = WebTool.esc;
    const i18n = WebTool.i18n;
    if (!data.results.length) {
      el.innerHTML = "";
      return;
    }
    let html =
      '<div class="table-wrap"><table class="result-table"><thead><tr>';
    html += "<th>#</th>";
    html += "<th>" + esc(i18n("result.bulk.input")) + "</th>";
    html += "<th>" + esc(i18n("result.bulk.status")) + "</th>";
    html += "<th>" + esc(i18n("ui.result")) + "</th>";
    html += "</tr></thead><tbody>";
    data.results.forEach((r, idx) => {
      const badge = r.ok
        ? '<span class="badge badge-ok">' + esc(i18n("result.bulk.ok")) + "</span>"
        : '<span class="badge badge-err">' + esc(i18n("result.bulk.error")) + "</span>";
      let valueText;
      if (r.ok) {
        const keys = ["ip", "host", "domain", "number", "e164", "cidr", "city"];
        const found = keys.map((k) => r.data && r.data[k]).find((v) => v !== undefined && v !== null && v !== "");
        valueText = found !== undefined ? String(found) : JSON.stringify(r.data);
      } else {
        valueText = (r.error && (r.error.message || r.error.code)) || "error";
      }
      html +=
        "<tr><td>" +
        (idx + 1) +
        "</td><td>" +
        esc(r.input) +
        "</td><td>" +
        badge +
        '</td><td class="mono">' +
        esc(valueText).slice(0, 200) +
        "</td></tr>";
    });
    html += "</tbody></table></div>";
    el.innerHTML = html;
  }

  form.onsubmit = async (e) => {
    e.preventDefault();
    const payload = readForm();
    if (!payload.values.length) return;
    WebTool.showLoading(btn);
    result.innerHTML = "";
    try {
      const res = await WebTool.api("bulk", payload);
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
