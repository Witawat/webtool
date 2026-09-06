(function () {
  const form = document.getElementById("tool-form");
  if (!form) return;
  const btn = document.getElementById("submit-btn");
  const result = document.getElementById("result");

  function readForm() {
    return {
      host: document.getElementById("host").value.trim(),
      max_hops: parseInt(document.getElementById("max_hops").value, 10),
    };
  }

  function renderResult(el, data) {
    const esc = WebTool.esc;
    const i18n = WebTool.i18n;
    if (!data.hops.length) {
      el.innerHTML =
        '<div class="result-card"><p>' +
        esc(i18n("result.traceroute.timed_out")) +
        "</p></div>";
      return;
    }
    let html = '<div class="table-wrap"><table class="result-table"><thead><tr>';
    html += "<th>" + esc(i18n("result.traceroute.ttl")) + "</th>";
    html += "<th>" + esc(i18n("result.traceroute.ip")) + "</th>";
    html += "<th>" + esc(i18n("result.traceroute.hostname")) + "</th>";
    html += "<th>" + esc(i18n("result.traceroute.rtt")) + "</th>";
    html += "</tr></thead><tbody>";
    data.hops.forEach((h) => {
      const rtt =
        h.timed_out || !h.rtt_ms.length
          ? esc(i18n("result.traceroute.timed_out"))
          : esc(h.rtt_ms.join(", "));
      html +=
        "<tr><td>" +
        esc(h.ttl) +
        "</td><td>" +
        esc(h.ip || "—") +
        "</td><td>" +
        esc(h.hostname || "—") +
        '</td><td class="mono">' +
        rtt +
        "</td></tr>";
    });
    html += "</tbody></table></div>";
    el.innerHTML = html;
  }

  form.onsubmit = async (e) => {
    e.preventDefault();
    WebTool.showLoading(btn);
    result.innerHTML = "";
    try {
      const res = await WebTool.api("traceroute", readForm());
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
