(function () {
  const I18N = window.I18N || {};
  const LANG = window.LANG || "th";

  function esc(s) {
    if (s === null || s === undefined) return "";
    return String(s).replace(/[&<>"']/g, (c) => ({
      "&": "&amp;",
      "<": "&lt;",
      ">": "&gt;",
      '"': "&quot;",
      "'": "&#39;",
    }[c]));
  }

  function i18n(key) {
    return I18N[key] !== undefined ? I18N[key] : key;
  }

  function fmtDuration(ms) {
    return i18n("common.duration").replace("{ms}", ms);
  }

  async function api(slug, payload) {
    const res = await fetch("/api/" + slug, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload || {}),
    });
    let body;
    try {
      body = await res.json();
    } catch (e) {
      body = {
        ok: false,
        error: { code: "INTERNAL", message: i18n("err.INTERNAL") },
      };
    }
    if (!res.ok) {
      const err = body.error || {
        code: "INTERNAL",
        message: i18n("err.INTERNAL"),
      };
      const e = new Error(err.message);
      e.code = err.code;
      e.field = err.field;
      throw e;
    }
    return body;
  }

  function showError(el, err) {
    const code = (err && err.code) || "INTERNAL";
    const msg = (err && err.message) || i18n("err." + code);
    el.innerHTML = '<div class="alert-error">' + esc(msg) + "</div>";
  }

  function showLoading(btn) {
    if (btn && !btn.disabled) {
      btn.disabled = true;
      btn.dataset.orig = btn.textContent;
      btn.textContent = i18n("common.loading");
    }
  }

  function stopLoading(btn) {
    if (btn && btn.dataset.orig) {
      btn.disabled = false;
      btn.textContent = btn.dataset.orig;
    }
  }

  const ls = document.getElementById("lang-switch");
  if (ls) {
    ls.addEventListener("click", () => {
      const target = LANG === "th" ? "en" : "th";
      document.cookie = "lang=" + target + ";path=/;max-age=31536000";
    });
  }

  const tt = document.getElementById("theme-toggle");
  if (tt) {
    tt.addEventListener("click", () => {
      const root = document.documentElement;
      const next = root.getAttribute("data-theme") === "dark" ? "light" : "dark";
      root.setAttribute("data-theme", next);
      document.cookie = "theme=" + next + ";path=/;max-age=31536000";
      tt.textContent =
        next === "dark"
          ? tt.dataset.labelLight || ""
          : tt.dataset.labelDark || "";
    });
  }

  window.WebTool = {
    api,
    showError,
    showLoading,
    stopLoading,
    esc,
    i18n,
    fmtDuration,
    I18N,
    LANG,
  };
})();
