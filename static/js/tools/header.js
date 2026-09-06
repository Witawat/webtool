(function () {
  const form = document.getElementById("tool-form");
  if (!form) return;
  const btn = document.getElementById("submit-btn");
  const result = document.getElementById("result");

  const SEC = [
    ["hsts", "result.header.hsts"],
    ["csp", "result.header.csp"],
    ["x_frame_options", "result.header.x_frame_options"],
    ["x_content_type_options", "result.header.x_content_type_options"],
    ["referrer_policy", "result.header.referrer_policy"],
    ["permissions_policy", "result.header.permissions_policy"],
  ];

  function renderResult(el, data) {
    const esc = WebTool.esc;
    const i18n = WebTool.i18n;
    const s = data.security;
    let html = '<div class="result-card">';
    html +=
      "<p>" +
      esc(data.url) +
      ' → <span class="badge ' +
      (data.status < 400 ? "badge-ok" : "badge-err") +
      '">' +
      esc(data.status) +
      "</span></p>";
    html +=
      "<p>" +
      esc(i18n("result.header.score")) +
      ": <strong>" +
      esc(data.score) +
      "/6</strong></p>";
    html += "<p><strong>" + esc(i18n("result.header.security")) + "</strong></p>";
    SEC.forEach(([key, labelKey]) => {
      let present = false;
      let value = null;
      if (key === "hsts" || key === "csp") {
        present = s[key].present;
        value = s[key].value;
      } else {
        present = !!s[key];
        value = s[key];
      }
      const badge = present
        ? '<span class="badge badge-ok">' + esc(i18n("result.header.present")) + "</span>"
        : '<span class="badge badge-err">' + esc(i18n("result.header.missing")) + "</span>";
      html += "<p>" + esc(i18n(labelKey)) + " " + badge;
      if (present && value) {
        html += ' <span class="mono">' + esc(value) + "</span>";
      }
      html += "</p>";
    });
    html +=
      "<details><summary>" +
      esc(i18n("result.header.all_headers")) +
      '</summary><pre class="raw">' +
      esc(JSON.stringify(data.headers, null, 2)) +
      "</pre></details>";
    html += "</div>";
    el.innerHTML = html;
  }

  form.onsubmit = async (e) => {
    e.preventDefault();
    WebTool.showLoading(btn);
    result.innerHTML = "";
    try {
      const res = await WebTool.api("header", {
        url: document.getElementById("url").value.trim(),
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
