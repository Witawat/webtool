(function () {
  const form = document.getElementById("tool-form");
  if (!form) return;
  const btn = document.getElementById("submit-btn");
  const result = document.getElementById("result");

  function readForm() {
    return {
      ip: document.getElementById("ip").value.trim(),
      start_port: parseInt(document.getElementById("start_port").value, 10),
      end_port: parseInt(document.getElementById("end_port").value, 10),
    };
  }

  function renderResult(el, data) {
    const esc = WebTool.esc;
    const i18n = WebTool.i18n;
    if (!data.open_ports.length) {
      el.innerHTML =
        '<div class="result-card"><p>' +
        esc(i18n("result.port-scan.no_open")) +
        "</p></div>";
      return;
    }
    let html = '<div class="table-wrap"><table class="result-table"><thead><tr>';
    html += "<th>" + esc(i18n("result.dns.name")) + "</th>";
    html += "<th>" + esc(i18n("result.port.service")) + "</th>";
    html += "<th>" + esc(i18n("result.port.latency")) + "</th>";
    html += "</tr></thead><tbody>";
    data.open_ports.forEach((p) => {
      html +=
        "<tr><td>" +
        esc(p.port) +
        "</td><td>" +
        esc(p.service || "—") +
        "</td><td>" +
        esc(p.latency_ms) +
        " ms</td></tr>";
    });
    html += "</tbody></table></div>";
    el.innerHTML = html;
  }

  form.onsubmit = async (e) => {
    e.preventDefault();
    WebTool.showLoading(btn);
    result.innerHTML = "";
    try {
      const res = await WebTool.api("port-scan", readForm());
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
