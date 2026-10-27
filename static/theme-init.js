// Applique le thème avant le premier rendu pour éviter un flash clair.
// Fichier externe (et non script inline) pour rester compatible avec une CSP
// stricte : `script-src 'self'`.
(() => {
  try {
    const stored = localStorage.getItem("theme");
    const theme = stored === "light" || stored === "dark"
      ? stored
      : (window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
    document.documentElement.dataset.theme = theme;
  } catch (_) {
    /* localStorage indisponible : on garde le thème clair */
  }
})();
