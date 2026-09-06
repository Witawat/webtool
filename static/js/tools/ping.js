(function () {
  const form = document.getElementById("tool-form");
  if (!form) return;
  const btn = document.getElementById("submit-btn");
  const result = document.getElementById("result");

  function readForm() {
    return {
      host: document.getElementById("host").value.trim(),
      count: parseInt(document.getElementById("count").value, 10),
    };
  }

  function renderResult(el, data) {
    const esc = WebTool.esc;
    const i18n = WebTool.i18n;
    const aliveBadge = data.alive
      ? '<span class="badge badge-ok">' + esc(i18n("result.ping.alive")) + "</span>"
      : '<span class="badge badge-err">' + esc(i18n("result.ping.dead")) + "</span>";
    const mode = data.icmp
      ? i18n("result.ping.mode_icmp")
      : i18n("result.ping.mode_tcp");

    let html = '<div class="result-card">';
    html += "<p>" + esc(data.host) + " (" + esc(data.ip) + ") " + aliveBadge + " · " + esc(mode) + "</p>";
    html +=
      "<p>" +
      esc(i18n("result.ping.sent")) +
      ": <strong>" +
      esc(data.sent) +
      "</strong> · " +
      esc(i18n("result.ping.received")) +
      ": <strong>" +
      esc(data.received) +
      "</strong> · " +
      esc(i18n("result.ping.loss")) +
      ": <strong>" +
      esc(data.loss_pct) +
      "%</strong></p>";
    html +=
      "<p>" +
      esc(i18n("result.ping.rtt_min")) +
      ": <strong>" +
      esc(data.rtt_ms.min) +
      " ms</strong> · " +
      esc(i18n("result.ping.rtt_avg")) +
      ": <strong>" +
      esc(data.rtt_ms.avg) +
      " ms</strong> · " +
      esc(i18n("result.ping.rtt_max")) +
      ": <strong>" +
      esc(data.rtt_ms.max) +
      " ms</strong></p>";
    html += "</div>";
    el.innerHTML = html;
  }

  form.onsubmit = async (e) => {
    e.preventDefault();
    WebTool.showLoading(btn);
    result.innerHTML = "";
    try {
      const res = await WebTool.api("ping", readForm());
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
