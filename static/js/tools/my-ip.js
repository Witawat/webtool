(function () {
  const form = document.getElementById("tool-form");
  if (!form) return;
  const btn = document.getElementById("submit-btn");
  const result = document.getElementById("result");

  function renderResult(el, data) {
    const esc = WebTool.esc;
    let html = '<div class="result-card">';
    html +=
      "<p>" +
      esc(WebTool.i18n("result.myip.ip")) +
      ": <strong>" +
      esc(data.ip) +
      "</strong></p>";
    html +=
      "<p>" +
      esc(WebTool.i18n("result.myip.version")) +
      ": <strong>IPv" +
      esc(data.version) +
      "</strong></p>";
    if (data.hostname) {
      html +=
        "<p>" +
        esc(WebTool.i18n("result.myip.hostname")) +
        ": <strong>" +
        esc(data.hostname) +
        "</strong></p>";
    }
    if (data.geo) {
      const loc = [data.geo.city, data.geo.region, data.geo.country]
        .filter(Boolean)
        .join(", ");
      html +=
        "<p>" +
        esc(WebTool.i18n("result.myip.location")) +
        ": <strong>" +
        esc(loc) +
        "</strong></p>";
      if (data.geo.isp) {
        html +=
          "<p>" +
          esc(WebTool.i18n("result.myip.isp")) +
          ": <strong>" +
          esc(data.geo.isp) +
          "</strong></p>";
      }
    }
    html += "</div>";
    el.innerHTML = html;
  }

  form.onsubmit = async (e) => {
    e.preventDefault();
    WebTool.showLoading(btn);
    result.innerHTML = "";
    try {
      const res = await WebTool.api("my-ip", {});
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
