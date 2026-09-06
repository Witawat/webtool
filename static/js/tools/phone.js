(function () {
  const form = document.getElementById("tool-form");
  if (!form) return;
  const btn = document.getElementById("submit-btn");
  const result = document.getElementById("result");

  const FIELDS = [
    ["e164", "result.phone.e164"],
    ["country", "result.phone.country"],
    ["region", "result.phone.region"],
    ["carrier", "result.phone.carrier"],
    ["timezones", "result.phone.timezones"],
    ["number_type", "result.phone.number_type"],
  ];

  function renderResult(el, data) {
    const esc = WebTool.esc;
    const i18n = WebTool.i18n;
    let html = '<div class="result-card">';
    if (!data.valid) {
      html +=
        '<span class="badge badge-err">' +
        esc(i18n("result.phone.invalid")) +
        "</span>";
      html += "</div>";
      el.innerHTML = html;
      return;
    }
    html +=
      '<span class="badge badge-ok">' +
      esc(i18n("result.phone.valid")) +
      "</span>";
    FIELDS.forEach(([key, labelKey]) => {
      let value = data[key];
      if (value === null || value === undefined || value === "") return;
      if (Array.isArray(value)) value = value.join(", ");
      html +=
        "<p>" +
        esc(i18n(labelKey)) +
        ": <strong>" +
        esc(value) +
        "</strong></p>";
    });
    html += "</div>";
    el.innerHTML = html;
  }

  form.onsubmit = async (e) => {
    e.preventDefault();
    WebTool.showLoading(btn);
    result.innerHTML = "";
    try {
      const res = await WebTool.api("phone", {
        number: document.getElementById("number").value.trim(),
        country: document.getElementById("country").value.trim() || null,
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
