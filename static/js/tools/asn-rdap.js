(function () {
  const form = document.getElementById("tool-form");
  if (!form) return;
  const btn = document.getElementById("submit-btn");
  const result = document.getElementById("result");

  const FIELDS = [
    ["handle", "result.asn-rdap.handle"],
    ["name", "result.asn-rdap.name"],
    ["type", "result.asn-rdap.type"],
    ["start_address", "result.asn-rdap.start"],
    ["end_address", "result.asn-rdap.end"],
    ["cidr", "result.asn-rdap.cidr"],
    ["country", "result.asn-rdap.country"],
    ["asn", "result.asn-rdap.asn"],
    ["org", "result.asn-rdap.org"],
    ["source", "result.asn-rdap.provider"],
  ];

  function renderResult(el, data) {
    const esc = WebTool.esc;
    const i18n = WebTool.i18n;
    let html = '<div class="result-card">';
    FIELDS.forEach(([key, labelKey]) => {
      let value = data[key];
      if (value === null || value === undefined) return;
      if (key === "asn" && typeof value === "object") {
        value = "AS" + value.number + " (" + (value.name || "—") + ")";
      }
      if (key === "org" && typeof value === "object") {
        value = value.name + (value.handle ? " [" + value.handle + "]" : "");
      }
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
      const res = await WebTool.api("asn-rdap", {
        query: document.getElementById("query").value.trim(),
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
