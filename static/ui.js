/**
 * ui.js — JavaScript minimaliste d'interface.
 * Aucune logique métier / API ici.
 *
 * Contenu :
 *  - bascule thème clair / sombre (mémorisée, respecte prefers-color-scheme) ;
 *  - compteur de caractères (+ annonce accessible près de la limite) ;
 *  - remplissage du champ via les pilules d'exemples ;
 *  - raccourci Ctrl / Cmd + Entrée pour soumettre.
 *
 * À brancher dans votre code : l'événement "submit" de #ask-form, le feedback
 * (#feedback-up / #feedback-down) et l'ouverture des sources.
 */
(() => {
  "use strict";

  const root = document.documentElement;

  /* ---------------------------------------------------------------------- */
  /* Thème                                                                  */
  /* ---------------------------------------------------------------------- */
  const themeToggle = document.getElementById("theme-toggle");
  const darkMedia = window.matchMedia("(prefers-color-scheme: dark)");

  const readStoredTheme = () => {
    try {
      const value = localStorage.getItem("theme");
      return value === "light" || value === "dark" ? value : null;
    } catch (_) {
      return null;
    }
  };

  const applyTheme = (theme) => {
    root.dataset.theme = theme;

    if (!themeToggle) return;
    const isDark = theme === "dark";
    themeToggle.setAttribute("aria-checked", String(isDark));
    themeToggle.title = isDark ? "Passer au thème clair" : "Passer au thème sombre";
  };

  applyTheme(readStoredTheme() || (darkMedia.matches ? "dark" : "light"));

  if (themeToggle) {
    themeToggle.addEventListener("click", () => {
      const nextTheme = root.dataset.theme === "dark" ? "light" : "dark";
      applyTheme(nextTheme);
      try {
        localStorage.setItem("theme", nextTheme);
      } catch (_) {
        /* mode privé : le choix reste valable pour la session */
      }
    });
  }

  // Suit le système uniquement si l'utilisateur n'a pas choisi explicitement.
  const handleSystemThemeChange = (event) => {
    if (!readStoredTheme()) applyTheme(event.matches ? "dark" : "light");
  };

  if (typeof darkMedia.addEventListener === "function") {
    darkMedia.addEventListener("change", handleSystemThemeChange);
  } else if (typeof darkMedia.addListener === "function") {
    darkMedia.addListener(handleSystemThemeChange);
  }

  // Synchronise le thème entre plusieurs onglets.
  window.addEventListener("storage", (event) => {
    if (event.key === "theme" && (event.newValue === "light" || event.newValue === "dark")) {
      applyTheme(event.newValue);
    }
  });

  /* ---------------------------------------------------------------------- */
  /* Compteur de caractères                                                 */
  /* ---------------------------------------------------------------------- */
  const input = document.getElementById("question-input");
  const counter = document.getElementById("char-counter");
  const currentEl = document.getElementById("char-current");
  const maxEl = document.getElementById("char-max");
  const limitStatus = document.getElementById("char-limit-status");

  if (input && counter && currentEl && maxEl) {
    const maxLength =
      Number.parseInt(input.dataset.maxLength, 10) ||
      Number.parseInt(input.getAttribute("maxlength"), 10) ||
      500;

    maxEl.textContent = String(maxLength);

    let lastAnnouncement = "";

    const updateCounter = () => {
      const length = input.value.length;
      const remaining = maxLength - length;

      currentEl.textContent = String(length);
      counter.classList.toggle("is-near-limit", length >= maxLength * 0.9 && length <= maxLength);
      counter.classList.toggle("is-over-limit", length > maxLength);

      if (limitStatus) {
        let announcement = "";

        if (length > maxLength) {
          announcement = `Limite dépassée de ${length - maxLength} caractère${length - maxLength > 1 ? "s" : ""}.`;
        } else if (length === maxLength) {
          announcement = `Limite de ${maxLength} caractères atteinte.`;
        } else if (remaining <= 25 && length > 0) {
          announcement = `Il vous reste ${remaining} caractère${remaining > 1 ? "s" : ""}.`;
        }

        // Évite les annonces répétées à chaque frappe.
        if (announcement !== lastAnnouncement) {
          limitStatus.textContent = announcement;
          lastAnnouncement = announcement;
        }
      }
    };

    input.addEventListener("input", updateCounter);
    updateCounter();
  }

  /* ---------------------------------------------------------------------- */
  /* Pilules d'exemples                                                     */
  /* ---------------------------------------------------------------------- */
  const exampleChips = document.querySelectorAll("#example-chips [data-question]");

  exampleChips.forEach((chip) => {
    chip.addEventListener("click", () => {
      if (!input) return;

      input.value = chip.dataset.question || "";
      input.focus();
      input.setSelectionRange(input.value.length, input.value.length);

      // Notifie aussi votre logique métier (compteur, activation du bouton, etc.).
      input.dispatchEvent(new Event("input", { bubbles: true }));
    });
  });

  /* ---------------------------------------------------------------------- */
  /* Raccourci Ctrl / Cmd + Entrée                                          */
  /* ---------------------------------------------------------------------- */
  if (input && input.form) {
    input.addEventListener("keydown", (event) => {
      if ((event.ctrlKey || event.metaKey) && event.key === "Enter") {
        event.preventDefault();
        input.form.requestSubmit();
      }
    });
  }

/* ---------------------------------------------------------------------- */
  /* Logique API & Feedback (Intégration finale)                            */
  /* ---------------------------------------------------------------------- */
  const API_BASE_URL = window.location.origin;

  const askFormApi = document.getElementById("ask-form");
  const inputField = document.getElementById("question-input");
  const submitBtn = document.getElementById("submit-button");

  const loadingState = document.getElementById("loading-state");
  const answerSection = document.getElementById("answer-section");
  const answerHeading = document.getElementById("answer-heading");
  const answerBody = document.getElementById("answer-body");
  const sourcesList = document.getElementById('sources-list');
  const sourceTemplate = document.getElementById('source-item-template');
  const sourcesCount = document.getElementById('sources-count');

  // Ouvre / referme l'extrait complet d'une source (accordéon accessible).
  if (sourcesList) {
    sourcesList.addEventListener('click', (event) => {
      const trigger = event.target.closest('.source-link');
      if (!trigger || !sourcesList.contains(trigger) || trigger.disabled) return;

      const detailId = trigger.getAttribute('aria-controls');
      const detail = detailId ? document.getElementById(detailId) : null;
      if (!detail) return;

      const isOpen = trigger.getAttribute('aria-expanded') === 'true';
      trigger.setAttribute('aria-expanded', String(!isOpen));
      trigger.closest('.source-item')?.classList.toggle('is-open', !isOpen);
      detail.hidden = isOpen;
    });
  }

  const errorBox = document.getElementById("error-box");
  const errorTitle = document.getElementById("error-title");
  const errorMessage = document.getElementById("error-message");

  const feedbackStatus = document.getElementById("feedback-status");
  const upBtn = document.getElementById("feedback-up");
  const downBtn = document.getElementById("feedback-down");
  let currentExchangeId = null;

  if (askFormApi) {
    askFormApi.addEventListener('submit', async (e) => {
        e.preventDefault();

        const question = inputField.value.trim();
        const maxLength = Number.parseInt(inputField.getAttribute("maxlength"), 10) || 500;

        if (!question || question.length > maxLength) return;

        // 1. Réinitialisation et affichage du chargement
        errorBox.setAttribute('hidden', '');
        answerSection.setAttribute('hidden', '');
        feedbackStatus.textContent = '';
        sourcesList.replaceChildren();
        if (sourcesCount) sourcesCount.textContent = '';
        currentExchangeId = null;

        // Réinitialise le feedback de la réponse précédente.
        if (upBtn) {
            upBtn.disabled = false;
            upBtn.setAttribute('aria-pressed', 'false');
        }
        if (downBtn) {
            downBtn.disabled = false;
            downBtn.setAttribute('aria-pressed', 'false');
        }

        submitBtn.classList.add('is-loading');
        submitBtn.disabled = true;
        loadingState.removeAttribute('hidden');
        loadingState.setAttribute('aria-busy', 'true');

        try {
            const response = await fetch(`${API_BASE_URL}/ask`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ question: question })
            });

            if (!response.ok) {
                await handleError(response.status);
                return;
            }

            const data = await response.json();

            // 2. Remplissage sécurisé des données
            if (answerBody) answerBody.textContent = data.answer;
            if (answerHeading) answerHeading.textContent = question;
            currentExchangeId = data.exchange_id;

        // Sources
        // L'API renvoie "sources" (documents) et "chunks" (extraits) : on combine les deux.
        const rawChunks = Array.isArray(data.chunks) ? data.chunks : [];
        const rawSources = Array.isArray(data.sources) ? data.sources : [];

        const extractFileName = (value) => {
            if (!value) return "";
            if (typeof value === "string") return value.split(/[\\/]/).pop();
            if (typeof value === "object") {
                const nested = value.source || value.file || value.filename || value.document ||
                    (value.metadata ? (value.metadata.source || value.metadata.file_name || value.metadata.filename) : "");
                return extractFileName(nested);
            }
            return "";
        };

        const sourceEntries = rawChunks.length
            ? rawChunks.map((chunk, index) => {
                const isString = typeof chunk === "string";
                const metadata = !isString && chunk.metadata ? chunk.metadata : {};
                const paired = rawSources[index];
                const pairedName = extractFileName(paired);

                if (isString) {
                    const trimmed = chunk.trim();
                    // Un chunk texte contient souvent des espaces ; un simple nom de fichier n'en a pas.
                    const looksLikeFileName = !/\s/.test(trimmed) && /\.[a-z0-9]{2,5}$/i.test(trimmed);
                    return {
                        fileName: pairedName || (looksLikeFileName ? extractFileName(trimmed) : "") || `Source ${index + 1}`,
                        title: pairedName || (looksLikeFileName ? extractFileName(trimmed) : "") || `Source ${index + 1}`,
                        textContent: looksLikeFileName && !pairedName ? "" : chunk
                    };
                }

                const fileName = extractFileName(chunk) || pairedName || `Source ${index + 1}`;
                const title = chunk.title || metadata.title || fileName;
                const pairedText = paired && typeof paired === "object"
                    ? (paired.text || paired.content || paired.page_content || paired.excerpt)
                    : "";
                const textContent = chunk.text || chunk.content || chunk.page_content || chunk.excerpt || pairedText || "";
                return { fileName, title, textContent };
            })
            : rawSources.map((source, index) => {
                const isString = typeof source === "string";
                const metadata = !isString && source.metadata ? source.metadata : {};
                const fileName = extractFileName(source) || `Source ${index + 1}`;
                const title = (!isString && (source.title || metadata.title)) || fileName;
                const textContent = isString
                    ? ""
                    : source.text || source.content || source.page_content || source.excerpt || "";
                return { fileName, title, textContent };
            });

        if (sourceEntries.length > 0 && sourcesList && sourceTemplate) {
            if (sourcesCount) {
                sourcesCount.textContent = `${sourceEntries.length} source${sourceEntries.length > 1 ? "s" : ""}`;
            }

            const fragment = document.createDocumentFragment();

            sourceEntries.forEach((source, index) => {
                const clone = sourceTemplate.content.cloneNode(true);
                const { fileName, title, textContent } = source;

                clone.querySelector('.source-num').textContent = String(index + 1).padStart(2, '0');

                const trigger = clone.querySelector('.source-link');
                const detail = clone.querySelector('.source-detail');
                const detailId = `source-detail-${index}`;
                const titleEl = clone.querySelector('.source-title');
                const excerpt = clone.querySelector('.source-excerpt');
                const fileEl = clone.querySelector('.source-file');

                titleEl.id = `${detailId}-title`;
                titleEl.textContent = title;

                // Évite de répéter le nom du fichier quand il sert déjà de titre.
                if (fileEl) {
                    if (fileName && fileName !== title) {
                        fileEl.textContent = fileName;
                    } else {
                        fileEl.remove();
                    }
                }

                detail.id = detailId;
                detail.setAttribute('aria-labelledby', titleEl.id);
                trigger.setAttribute('aria-controls', detailId);
                trigger.dataset.doc = fileName;

                if (textContent) {
                    // L'aperçu est tronqué en CSS ; le panneau affiche le texte complet.
                    excerpt.textContent = textContent;
                    detail.querySelector('.source-detail-text').textContent = textContent;
                } else {
                    excerpt.remove();
                    detail.remove();
                    trigger.disabled = true;
                    trigger.removeAttribute('aria-controls');
                    trigger.removeAttribute('aria-expanded');
                    clone.querySelector('.source-chevron')?.remove();
                }

                fragment.appendChild(clone);
            });

            sourcesList.appendChild(fragment);
        }

            // 3. Affichage de la réponse
            loadingState.setAttribute('hidden', '');
            loadingState.setAttribute('aria-busy', 'false');
            answerSection.removeAttribute('hidden');
            answerSection.classList.remove('is-fresh');
            void answerSection.offsetWidth; // force le rejeu de l'animation
            answerSection.classList.add('is-fresh');
            if (answerHeading) answerHeading.focus();

        } catch (error) {
            console.error("Erreur lors de la requête :", error);
            loadingState.setAttribute('hidden', '');
            loadingState.setAttribute('aria-busy', 'false');
            showError("Erreur de connexion", "Impossible de contacter le serveur. Veuillez réessayer plus tard.");
        } finally {
            submitBtn.classList.remove('is-loading');
            submitBtn.disabled = false;
        }
    });
  }

  // --- Gestion des erreurs ---
  async function handleError(statusCode) {
      loadingState.setAttribute('hidden', '');
      loadingState.setAttribute('aria-busy', 'false');
      let title = "Erreur inattendue";
      let msg = "Une erreur inconnue est survenue.";

      if (statusCode === 400) { title = "Requête invalide"; msg = "Votre question est invalide ou trop longue."; }
      if (statusCode === 429) { title = "Service saturé"; msg = "Trop de requêtes. Veuillez patienter un instant."; }
      if (statusCode === 500 || statusCode === 503) { title = "Service indisponible"; msg = "L'assistant est temporairement hors ligne."; }

      showError(title, msg);
  }

  function showError(title, msg) {
      if (errorBox) {
          if (errorTitle) errorTitle.textContent = title;
          if (errorMessage) errorMessage.textContent = msg;
          errorBox.removeAttribute('hidden');
      }
  }

// --- Gestion du Feedback ---
  if (upBtn) upBtn.addEventListener('click', () => sendFeedback("positive", upBtn));
  if (downBtn) downBtn.addEventListener('click', () => sendFeedback("negative", downBtn));

  async function sendFeedback(ratingValue, clickedBtn) {
      console.log("Clic détecté ! exchange_id actuel :", currentExchangeId);

      if (!currentExchangeId) {
          console.error("Impossible d'envoyer le feedback : currentExchangeId est vide.");
          return;
      }

      // Désactive les boutons pour éviter les clics multiples
      if (upBtn) upBtn.disabled = true;
      if (downBtn) downBtn.disabled = true;

      try {
          const response = await fetch(`${API_BASE_URL}/feedback`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ exchange_id: currentExchangeId, rating: ratingValue, comment: ""})
          });

          if (response.ok) {
              console.log("Feedback enregistré avec succès !");
              if (feedbackStatus) feedbackStatus.textContent = 'Merci pour votre retour !';
              clickedBtn.setAttribute('aria-pressed', 'true'); // Retour visuel (accessibilité)
          } else {
              console.error("Erreur de l'API lors du feedback :", response.status);
          }
      } catch (error) {
          console.error("Erreur réseau pour le feedback :", error);
      }
  }

})(); // Fin de la fonction IIFE globale