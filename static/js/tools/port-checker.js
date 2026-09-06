(function () {
  const form = document.getElementById("tool-form");
  if (!form) return;
  const btn = document.getElementById("submit-btn");
  const result = document.getElementById("result");

  document.querySelectorAll(".chip").forEach((ch) => {
    ch.addEventListener("click", () => {
      document.getElementById("port").value = ch.dataset.port;
    });
  });

  function readForm() {
    return {
      host: document.getElementById("host").value.trim(),
      port: parseInt(document.getElementById("port").value, 10),
    };
  }

  function stateClass(state) {
    if (state === "open") return "badge-ok";
    if (state === "filtered") return "badge-warn";
    return "badge-err";
  }

  function renderResult(el, data) {
    const esc = WebTool.esc;
    const i18n = WebTool.i18n;
    let html = '<div class="result-card">';
    html +=
      "<p>" +
      esc(data.host) +
      ":" +
      esc(data.port) +
      ' <span class="badge ' +
      stateClass(data.state) +
      '">' +
      esc(i18n("result.port.state_" + data.state)) +
      "</span></p>";
    html +=
      "<p>" +
      esc(i18n("result.port.ip")) +
      ": <strong>" +
      esc(data.ip) +
      "</strong></p>";
    if (data.service) {
      html +=
        "<p>" +
        esc(i18n("result.port.service")) +
        ": <strong>" +
        esc(data.service) +
        "</strong></p>";
    }
    html +=
      "<p>" +
      esc(i18n("result.port.latency")) +
      ": <strong>" +
      esc(data.latency_ms) +
      " ms</strong></p>";
    html += "</div>";
    el.innerHTML = html;
  }

  form.onsubmit = async (e) => {
    e.preventDefault();
    WebTool.showLoading(btn);
    result.innerHTML = "";
    try {
      const res = await WebTool.api("port-checker", readForm());
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
