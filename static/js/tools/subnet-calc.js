(function () {
  const form = document.getElementById("tool-form");
  if (!form) return;
  const btn = document.getElementById("submit-btn");
  const result = document.getElementById("result");

  const FIELDS = [
    "network",
    "broadcast",
    "netmask",
    "wildcard",
    "first_host",
    "last_host",
    "usable_hosts",
    "total_hosts",
    "prefix",
    "ip_version",
  ];

  function renderResult(el, data) {
    const esc = WebTool.esc;
    const i18n = WebTool.i18n;
    let html = '<div class="result-card">';
    FIELDS.forEach((f) => {
      html +=
        "<p>" +
        esc(i18n("result.subnet." + f)) +
        ": <strong>" +
        esc(data[f]) +
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
      const res = await WebTool.api("subnet-calc", {
        cidr: document.getElementById("cidr").value.trim(),
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
