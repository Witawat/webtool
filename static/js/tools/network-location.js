(function () {
  const form = document.getElementById("tool-form");
  if (!form) return;
  const btn = document.getElementById("submit-btn");
  const result = document.getElementById("result");
  let mapInstance = null;

  const FIELDS = [
    ["ip", "result.network-location.ip"],
    ["city", "result.network-location.city"],
    ["region", "result.network-location.region"],
    ["country", "result.network-location.country"],
    ["isp", "result.network-location.isp"],
    ["org", "result.network-location.org"],
    ["asn", "result.network-location.asn"],
    ["provider", "result.network-location.provider"],
  ];

  function initMap(lat, lon) {
    if (mapInstance) {
      mapInstance.remove();
      mapInstance = null;
    }
    mapInstance = L.map("locmap").setView([lat, lon], 5);
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      maxZoom: 18,
      attribution: "&copy; OpenStreetMap contributors",
    }).addTo(mapInstance);
    L.marker([lat, lon]).addTo(mapInstance);
  }

  function renderResult(el, data) {
    const esc = WebTool.esc;
    const i18n = WebTool.i18n;
    let html = '<div class="result-card">';
    FIELDS.forEach(([key, labelKey]) => {
      const value = data[key];
      if (value === null || value === undefined || value === "") return;
      html +=
        "<p>" +
        esc(i18n(labelKey)) +
        ": <strong>" +
        esc(value) +
        "</strong></p>";
    });
    html += "</div>";
    if (data.lat !== null && data.lat !== undefined && data.lon !== null && data.lon !== undefined) {
      html += '<div id="locmap" class="locmap"></div>';
    }
    el.innerHTML = html;
    if (document.getElementById("locmap")) {
      initMap(data.lat, data.lon);
    }
  }

  form.onsubmit = async (e) => {
    e.preventDefault();
    WebTool.showLoading(btn);
    result.innerHTML = "";
    if (mapInstance) {
      mapInstance.remove();
      mapInstance = null;
    }
    try {
      const res = await WebTool.api("network-location", {
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
