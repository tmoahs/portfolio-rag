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
  /* Effacement rapide de la question                                       */
  /* ---------------------------------------------------------------------- */
  const clearInputBtn = document.getElementById("clear-input");
  let clearOnNextBackspace = false;

  const clearQuestion = () => {
    if (!input) return;
    clearOnNextBackspace = false;
    input.value = "";
    input.dispatchEvent(new Event("input", { bubbles: true }));
    input.focus();
  };

  const updateClearButton = () => {
    if (!input || !clearInputBtn) return;
    clearInputBtn.hidden = input.value.length === 0;
  };

  if (input) {
    input.addEventListener("input", () => {
      // Toute modification réelle désarme l'effacement global. Notre propre
      // effacement remet le drapeau à false avant de déclencher cet événement.
      clearOnNextBackspace = false;
      updateClearButton();
    });

    input.addEventListener("keydown", (event) => {
      if (event.isComposing) return;

      if (event.key === "Backspace" && clearOnNextBackspace) {
        // On n'efface tout que si le curseur est à la fin et sans sélection :
        // un clic au milieu du texte garde l'édition précise.
        const caretAtEnd =
          input.selectionStart === input.selectionEnd &&
          input.selectionStart === input.value.length;

        if (caretAtEnd && !event.ctrlKey && !event.metaKey && !event.altKey) {
          event.preventDefault();
          clearQuestion();
          return;
        }

        clearOnNextBackspace = false;
        return;
      }

      if (
        ["ArrowLeft", "ArrowRight", "ArrowUp", "ArrowDown", "Home", "End", "PageUp", "PageDown"].includes(
          event.key
        )
      ) {
        clearOnNextBackspace = false;
      }
    });

    // Clavier virtuel mobile : `keydown` peut être « Unidentified ».
    input.addEventListener("beforeinput", (event) => {
      if (event.isComposing) return;
      if (event.inputType !== "deleteContentBackward" || !clearOnNextBackspace) return;

      const caretAtEnd =
        input.selectionStart === input.selectionEnd &&
        input.selectionStart === input.value.length;

      if (caretAtEnd) {
        event.preventDefault();
        clearQuestion();
      } else {
        clearOnNextBackspace = false;
      }
    });
  }

  if (input && clearInputBtn) {
    clearInputBtn.addEventListener("click", clearQuestion);
  }

  updateClearButton();

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

      // Envoi immédiat : plus besoin de recliquer sur le bouton.
      if (input.form) input.form.requestSubmit();
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
  const API_BASE_URL = "/api";

  const askFormApi = document.getElementById("ask-form");
  const inputField = document.getElementById("question-input");
  const submitBtn = document.getElementById("submit-button");

  const loadingState = document.getElementById("loading-state");
  const loadingMessage = document.getElementById("loading-message");
  const loadingDefaultMessage = loadingMessage ? loadingMessage.textContent : "";

  const answerSection = document.getElementById("answer-section");
  const answerHeading = document.getElementById("answer-heading");
  const answerBody = document.getElementById("answer-body");
  const answerMeta = document.getElementById("answer-meta");
  const answerDuration = document.getElementById("answer-duration");
  const answerTimestamp = document.getElementById("answer-timestamp");

  const sourcesSection = document.getElementById("sources-section");
  const sourcesList = document.getElementById("sources-list");
  const sourceTemplate = document.getElementById("source-item-template");
  const sourcesCount = document.getElementById("sources-count");

  const errorBox = document.getElementById("error-box");
  const errorTitle = document.getElementById("error-title");
  const errorMessage = document.getElementById("error-message");

  const feedbackStatus = document.getElementById("feedback-status");
  const upBtn = document.getElementById("feedback-up");
  const downBtn = document.getElementById("feedback-down");

  let currentExchangeId = null;
  let isBusy = false;

  /* --- Utilitaires d'affichage ------------------------------------------- */

  const setBusy = (busy) => {
    isBusy = busy;

    if (submitBtn) {
      submitBtn.classList.toggle("is-loading", busy);
      submitBtn.disabled = busy;
    }

    if (loadingState) {
      loadingState.toggleAttribute("hidden", !busy);
      loadingState.setAttribute("aria-busy", String(busy));
    }

    if (busy && loadingMessage) {
      loadingMessage.textContent = loadingDefaultMessage;
    }

    if (answerSection) answerSection.setAttribute("aria-busy", String(busy));
  };

  const resetResult = () => {
    if (errorBox) errorBox.setAttribute("hidden", "");
    if (answerSection) {
      answerSection.setAttribute("hidden", "");
      answerSection.classList.remove("is-fresh", "is-streaming");
    }
    if (answerBody) answerBody.replaceChildren();
    if (sourcesList) sourcesList.replaceChildren();
    if (sourcesCount) sourcesCount.textContent = "";
    if (sourcesSection) sourcesSection.removeAttribute("hidden");
    if (answerMeta) answerMeta.setAttribute("hidden", "");
    if (feedbackStatus) feedbackStatus.textContent = "";
    if (upBtn) {
      upBtn.disabled = false;
      upBtn.setAttribute("aria-pressed", "false");
    }
    if (downBtn) {
      downBtn.disabled = false;
      downBtn.setAttribute("aria-pressed", "false");
    }
    currentExchangeId = null;
  };

  const revealAnswer = () => {
    if (!answerSection) return;
    answerSection.removeAttribute("hidden");
    answerSection.classList.remove("is-fresh");
    void answerSection.offsetWidth; // force le rejeu de l'animation
    answerSection.classList.add("is-fresh");
  };

  // Écrit le texte de la réponse (texte brut : pas d'innerHTML, donc pas de XSS).
  /* --- Rendu Markdown léger (sans innerHTML) ----------------------------- */

  const SAFE_PROTOCOLS = new Set(["http:", "https:", "mailto:"]);

  // Mode strict : seuls ces domaines (et leurs sous-domaines) sont cliquables.
  const ALLOWED_LINK_HOSTS = ["linkedin.com", "github.com", "tpatout.fr"];
  const ALLOWED_MAILTO = "t.patout@proton.me";

  const safeUrl = (value) => {
    try {
      const url = new URL(value, window.location.origin);
      return SAFE_PROTOCOLS.has(url.protocol) ? url.href : null;
    } catch (_) {
      return null;
    }
  };

  const isAllowedUrl = (url) => {
    if (url.startsWith("mailto:")) {
      // Pas de paramètres (sujet/corps préremplis) : adresse exacte uniquement.
      const parts = url.slice("mailto:".length).split("?");
      return parts.length === 1 && parts[0].trim().toLowerCase() === ALLOWED_MAILTO;
    }
    try {
      const host = new URL(url).hostname.toLowerCase().replace(/^www\./, "");
      return ALLOWED_LINK_HOSTS.some(
        (base) => host === base || host.endsWith(`.${base}`)
      );
    } catch (_) {
      return false;
    }
  };

  const appendLink = (parent, label, href, showHost = false) => {
    const url = safeUrl(href);
    if (!url) {
      parent.appendChild(document.createTextNode(label));
      return;
    }

    if (!isAllowedUrl(url)) {
      // Lien hors liste blanche : on affiche le libellé et le domaine, sans lien.
      parent.appendChild(document.createTextNode(label));
      if (showHost && !url.startsWith("mailto:")) {
        try {
          const host = new URL(url).hostname.replace(/^www\./, "");
          if (host && !label.toLowerCase().includes(host)) {
            const hint = document.createElement("span");
            hint.className = "link-host";
            hint.textContent = ` (${host})`;
            parent.appendChild(hint);
          }
        } catch (_) {
          /* URL déjà validée */
        }
      }
      return;
    }

    const link = document.createElement("a");
    link.textContent = label;
    link.href = url;
    link.title = url;
    if (!url.startsWith("mailto:")) {
      link.target = "_blank";
    }
    link.rel = "noopener noreferrer";
    parent.appendChild(link);

    // Pour un lien Markdown dont le libellé masque la destination
    // (« [Mon projet](https://exemple.fr) »), on affiche le domaine.
    if (showHost && !url.startsWith("mailto:")) {
      try {
        const host = new URL(url).hostname.replace(/^www\./, "");
        if (host && !label.toLowerCase().includes(host)) {
          const hint = document.createElement("span");
          hint.className = "link-host";
          hint.textContent = ` (${host})`;
          parent.appendChild(hint);
        }
      } catch (_) {
        /* URL déjà validée : pas de cas attendu */
      }
    }
  };

  const LINK_TLDS = "fr|com|org|net|io|dev|ai|co|app|me|eu|ch|info|tech|xyz|cloud|site|blog";

  const INLINE_SOURCE =
    "(\\*\\*[^*]+\\*\\*|`[^`\\n]+`|\\[[^\\]\\n]+\\]\\((?:https?:\\/\\/|mailto:)[^)\\s]+\\)|https?:\\/\\/[^\\s<]+|[\\w.+-]+@[\\w-]+\\.[a-z]{2,}|(?:www\\.)?(?:[a-z0-9-]+\\.)+(?:" +
    LINK_TLDS +
    ")(?:\\/[^\\s<]*)?|\\*[^*\\n]+\\*)";

  const trimTrailing = (value) => {
    let url = value;
    let trailing = "";
    while (/[.,;:!?]$/.test(url)) {
      trailing = url.slice(-1) + trailing;
      url = url.slice(0, -1);
    }
    if (url.endsWith(")") && !url.includes("(")) {
      trailing = ")" + trailing;
      url = url.slice(0, -1);
    }
    return [url, trailing];
  };

  const appendInline = (parent, text) => {
    const pattern = new RegExp(INLINE_SOURCE, "gi");
    let lastIndex = 0;
    let match;

    while ((match = pattern.exec(text)) !== null) {
      if (match.index > lastIndex) {
        parent.appendChild(document.createTextNode(text.slice(lastIndex, match.index)));
      }

      const token = match[0];

      if (token.startsWith("**")) {
        const strong = document.createElement("strong");
        appendInline(strong, token.slice(2, -2));
        parent.appendChild(strong);
      } else if (token.startsWith("`")) {
        const code = document.createElement("code");
        code.textContent = token.slice(1, -1);
        parent.appendChild(code);
      } else if (token.startsWith("[")) {
        const link = /^\[([^\]]+)\]\(([^)\s]+)\)$/.exec(token);
        if (link) appendLink(parent, link[1], link[2], true);
        else parent.appendChild(document.createTextNode(token));
      } else if (/^https?:\/\//i.test(token)) {
        const [url, trailing] = trimTrailing(token);
        appendLink(parent, url, url);
        if (trailing) parent.appendChild(document.createTextNode(trailing));
      } else if (token.includes("@")) {
        appendLink(parent, token, `mailto:${token}`);
      } else if (token.startsWith("*")) {
        const em = document.createElement("em");
        em.textContent = token.slice(1, -1);
        parent.appendChild(em);
      } else {
        // Domaine sans schéma : linkedin.com/in/..., github.com/tmoahs, tpatout.fr
        const [domain, trailing] = trimTrailing(token);
        appendLink(parent, domain, `https://${domain}`);
        if (trailing) parent.appendChild(document.createTextNode(trailing));
      }

      lastIndex = pattern.lastIndex;
    }

    if (lastIndex < text.length) {
      parent.appendChild(document.createTextNode(text.slice(lastIndex)));
    }
  };

  const renderRichText = (container, text) => {
    const lines = String(text || "").split(/\r?\n/);
    let paragraphLines = [];
    let currentList = null;
    let currentListType = null;

    const closeList = () => {
      currentList = null;
      currentListType = null;
    };

    const flushParagraph = () => {
      if (!paragraphLines.length) return;
      const paragraph = document.createElement("p");
      appendInline(paragraph, paragraphLines.join("\n"));
      container.appendChild(paragraph);
      paragraphLines = [];
    };

    const openList = (type) => {
      if (currentList && currentListType === type) return currentList;
      closeList();
      currentList = document.createElement(type === "ol" ? "ol" : "ul");
      currentListType = type;
      container.appendChild(currentList);
      return currentList;
    };

    for (const line of lines) {
      const trimmed = line.trim();

      if (!trimmed) {
        flushParagraph();
        closeList();
        continue;
      }

      const heading = /^(#{1,6})\s+(.*)$/.exec(trimmed);
      if (heading) {
        flushParagraph();
        closeList();
        const title = document.createElement("h3");
        appendInline(title, heading[2]);
        container.appendChild(title);
        continue;
      }

      const bullet = /^[-*•]\s+(.*)$/.exec(trimmed);
      if (bullet) {
        flushParagraph();
        const list = openList("ul");
        const item = document.createElement("li");
        appendInline(item, bullet[1]);
        list.appendChild(item);
        continue;
      }

      const ordered = /^\d+[.)]\s+(.*)$/.exec(trimmed);
      if (ordered) {
        flushParagraph();
        const list = openList("ol");
        const item = document.createElement("li");
        appendInline(item, ordered[1]);
        list.appendChild(item);
        continue;
      }

      closeList();
      paragraphLines.push(trimmed);
    }

    flushParagraph();
    closeList();
  };

  const appendStreamCaret = (container) => {
    const caret = document.createElement("span");
    caret.className = "stream-caret";
    caret.setAttribute("aria-hidden", "true");

    let target = container.lastElementChild;
    if (target && (target.tagName === "UL" || target.tagName === "OL")) {
      target = target.lastElementChild || target;
    }
    (target || container).appendChild(caret);
  };

  const renderAnswer = (text, streaming) => {
    if (!answerBody) return;

    answerBody.replaceChildren();
    renderRichText(answerBody, text);
    if (streaming) appendStreamCaret(answerBody);
    if (answerSection) answerSection.classList.toggle("is-streaming", Boolean(streaming));
  };

  const showMeta = (latency, cached = false) => {
    if (!answerMeta) return;
    if (answerDuration) {
      if (cached) {
        answerDuration.textContent = "en cache";
      } else {
        answerDuration.textContent = Number.isFinite(latency)
          ? `${latency.toFixed(1)} s`
          : "";
      }
    }
    if (answerTimestamp) {
      answerTimestamp.textContent = new Date().toLocaleTimeString("fr-FR", {
        hour: "2-digit",
        minute: "2-digit",
      });
    }
    answerMeta.removeAttribute("hidden");
  };

  const extractFileName = (value) => {
    if (!value) return "";
    if (typeof value === "string") return value.split(/[\\/]/).pop();
    if (typeof value === "object") {
      const nested =
        value.source || value.file || value.filename || value.document ||
        (value.metadata
          ? value.metadata.source || value.metadata.file_name || value.metadata.filename
          : "");
      return extractFileName(nested);
    }
    return "";
  };

  // Les chunks sont préfixés d'un en-tête technique "[fichier.md > Titre]" :
  // on le retire à l'affichage uniquement (l'API conserve le texte brut).
  const stripChunkHeader = (text) =>
    String(text || "").replace(/^\s*\[[^\]\n]{1,200}\]\s*/, "");

  // L'API renvoie désormais des chunks typés { text, source, title, distance }.
  const normaliseSources = (chunks, sources) => {
    const chunkList = Array.isArray(chunks) ? chunks : [];
    const sourceList = Array.isArray(sources) ? sources : [];

    if (chunkList.length) {
      return chunkList.map((chunk, index) => {
        const value = chunk && typeof chunk === "object" ? chunk : {};
        const fileName =
          extractFileName(value.source) ||
          extractFileName(sourceList[index]) ||
          `Source ${index + 1}`;

        return {
          fileName,
          title: value.title || fileName,
          text: stripChunkHeader(value.text || value.content || ""),
        };
      });
    }

    return sourceList.map((source, index) => {
      const fileName = extractFileName(source) || `Source ${index + 1}`;
      return { fileName, title: fileName, text: "" };
    });
  };

  const renderSources = (chunks, sources) => {
    if (!sourcesList || !sourceTemplate) return;

    const entries = normaliseSources(chunks, sources);
    sourcesList.replaceChildren();

    if (sourcesCount) {
      sourcesCount.textContent = entries.length
        ? `${entries.length} source${entries.length > 1 ? "s" : ""}`
        : "";
    }

    if (!entries.length) {
      if (sourcesSection) sourcesSection.setAttribute("hidden", "");
      return;
    }

    if (sourcesSection) sourcesSection.removeAttribute("hidden");

    const fragment = document.createDocumentFragment();

    entries.forEach((source, index) => {
      const clone = sourceTemplate.content.cloneNode(true);
      const { fileName, title, text } = source;

      clone.querySelector(".source-num").textContent = String(index + 1).padStart(2, "0");

      const trigger = clone.querySelector(".source-link");
      const detail = clone.querySelector(".source-detail");
      const detailId = `source-detail-${index}`;
      const titleEl = clone.querySelector(".source-title");
      const excerpt = clone.querySelector(".source-excerpt");
      const fileEl = clone.querySelector(".source-file");

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
      detail.setAttribute("aria-labelledby", titleEl.id);
      trigger.setAttribute("aria-controls", detailId);
      trigger.dataset.doc = fileName;

      if (text) {
        // L'aperçu est tronqué en CSS ; le panneau affiche le texte complet du chunk.
        excerpt.textContent = text;
        detail.querySelector(".source-detail-text").textContent = text;
      } else {
        excerpt.remove();
        detail.remove();
        trigger.disabled = true;
        trigger.removeAttribute("aria-controls");
        trigger.removeAttribute("aria-expanded");
        clone.querySelector(".source-chevron")?.remove();
      }

      fragment.appendChild(clone);
    });

    sourcesList.appendChild(fragment);
  };

  // Ouvre / referme l'extrait complet d'une source (accordéon accessible).
  if (sourcesList) {
    sourcesList.addEventListener("click", (event) => {
      const trigger = event.target.closest(".source-link");
      if (!trigger || !sourcesList.contains(trigger) || trigger.disabled) return;

      const detailId = trigger.getAttribute("aria-controls");
      const detail = detailId ? document.getElementById(detailId) : null;
      if (!detail) return;

      const isOpen = trigger.getAttribute("aria-expanded") === "true";
      trigger.setAttribute("aria-expanded", String(!isOpen));
      trigger.closest(".source-item")?.classList.toggle("is-open", !isOpen);
      detail.hidden = isOpen;
    });
  }

  /* --- Lecture du flux SSE ----------------------------------------------- */

  const readSseStream = async (response, onEvent) => {
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";

    for (;;) {
      const { value, done } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });

      const separator = /\r?\n\r?\n/g;
      let match;
      let consumed = 0;

      while ((match = separator.exec(buffer)) !== null) {
        const block = buffer.slice(consumed, match.index);
        consumed = match.index + match[0].length;

        const dataLine = block.split(/\r?\n/).find((line) => line.startsWith("data:"));
        if (!dataLine) continue;

        const raw = dataLine.slice(5).trim();
        if (!raw) continue;

        try {
          onEvent(JSON.parse(raw));
        } catch (error) {
          console.warn("Événement SSE illisible :", raw, error);
        }
      }

      buffer = buffer.slice(consumed);
    }
  };

  /* --- Appels API -------------------------------------------------------- */

  const askClassic = async (question) => {
    const response = await fetch(`${API_BASE_URL}/ask`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
    });

    if (!response.ok) {
      await handleError(response.status);
      return;
    }

    const data = await response.json();

    currentExchangeId = data.exchange_id || null;
    if (answerHeading) answerHeading.textContent = question;
    renderAnswer(data.answer || "", false);
    renderSources(data.chunks, data.sources);
    showMeta(Number.NaN, Boolean(data.cached));
    revealAnswer();
    if (loadingState) loadingState.setAttribute("hidden", "");
  };

  const askStream = async (question) => {
    const response = await fetch(`${API_BASE_URL}/ask/stream`, {
      method: "POST",
      headers: { "Content-Type": "application/json", Accept: "text/event-stream" },
      body: JSON.stringify({ question }),
    });

    // Backend pas encore à jour : on retombe sur le POST classique.
    if (response.status === 404 || response.status === 405) return false;

    if (!response.ok) {
      await handleError(response.status);
      return true;
    }

    if (!response.body) return false;

    let answer = "";
    let started = false;
    let completed = false;
    let streamError = null;

    const startStreamingUi = () => {
      if (started) return;
      started = true;
      revealAnswer();
      if (loadingState) loadingState.setAttribute("hidden", "");
    };

    await readSseStream(response, (event) => {
      if (!event || typeof event.type !== "string") return;

      switch (event.type) {
        case "meta":
          currentExchangeId = event.exchange_id || null;
          break;

        case "sources":
          renderSources(event.chunks, null);
          if (loadingMessage) loadingMessage.textContent = "Rédaction de la réponse…";
          break;

        case "delta":
          startStreamingUi();
          answer += event.text || "";
          renderAnswer(answer, true);
          break;

        case "done":
          completed = true;
          currentExchangeId = event.exchange_id || currentExchangeId;
          answer = event.answer || answer;
          renderAnswer(answer, false);
          if (sourcesSection && Array.isArray(event.sources) && !event.sources.length) {
            sourcesSection.setAttribute("hidden", "");
          }
          showMeta(Number(event.latency), Boolean(event.cached));
          startStreamingUi();
          if (loadingState) loadingState.setAttribute("hidden", "");
          if (answerHeading) answerHeading.focus();
          break;

        case "error":
          streamError = event.message || "Le service est momentanément indisponible.";
          if (loadingState) loadingState.setAttribute("hidden", "");
          showError("Service indisponible", streamError);
          break;

        default:
          break;
      }
    });

    if (!completed && !streamError && answer) {
      showError(
        "Réponse incomplète",
        "La réponse s'est interrompue avant la fin. Vous pouvez réessayer."
      );
    }

    return true;
  };

  if (askFormApi) {
    askFormApi.addEventListener("submit", async (event) => {
      event.preventDefault();
      if (isBusy) return;

      const question = inputField ? inputField.value.trim() : "";
      const maxLength = inputField
        ? Number.parseInt(inputField.getAttribute("maxlength"), 10) || 500
        : 500;

      if (!question || question.length > maxLength) return;

      // La question vient d'être posée : un seul Backspace effacera tout.
      clearOnNextBackspace = true;

      resetResult();
      setBusy(true);
      if (answerHeading) answerHeading.textContent = question;

      try {
        const handled = await askStream(question);
        if (!handled) await askClassic(question);
      } catch (error) {
        console.error("Erreur lors de la requête :", error);
        if (loadingState) loadingState.setAttribute("hidden", "");
        showError(
          "Erreur de connexion",
          "Impossible de contacter le serveur. Veuillez réessayer plus tard."
        );
      } finally {
        setBusy(false);
        if (answerSection) answerSection.classList.remove("is-streaming");
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

  /* ---------------------------------------------------------------------- */
  /* Contact : copie de l'adresse email                                     */
  /* ---------------------------------------------------------------------- */
  const contactLink = document.getElementById("contact-link");
  const contactTooltip = document.getElementById("contact-tooltip");

  if (contactLink && contactTooltip) {
    const EMAIL = "t.patout@proton.me";
    let tooltipTimer = null;

    const hideTooltip = () => {
      contactTooltip.classList.remove("is-visible");
      if (tooltipTimer) {
        clearTimeout(tooltipTimer);
        tooltipTimer = null;
      }
    };

    const showTooltip = () => {
      // Le texte est injecté au clic : la région aria-live est ainsi annoncée.
      contactTooltip.textContent = `Email copié : ${EMAIL}`;
      contactTooltip.classList.add("is-visible");
      if (tooltipTimer) clearTimeout(tooltipTimer);
      tooltipTimer = setTimeout(hideTooltip, 2600);
    };

    const copyWithFallback = () => {
      const area = document.createElement("textarea");
      area.value = EMAIL;
      area.setAttribute("readonly", "");
      area.style.position = "fixed";
      area.style.opacity = "0";
      document.body.appendChild(area);
      area.select();
      let copied = false;
      try {
        copied = document.execCommand("copy");
      } catch (_) {
        copied = false;
      }
      area.remove();
      return copied;
    };

    contactLink.addEventListener("click", async (event) => {
      // Pas d'API presse-papiers (http non sécurisé) : on laisse le mailto agir.
      if (!navigator.clipboard && !document.queryCommandSupported?.("copy")) return;

      event.preventDefault();

      let copied = false;
      try {
        if (navigator.clipboard) {
          await navigator.clipboard.writeText(EMAIL);
          copied = true;
        } else {
          copied = copyWithFallback();
        }
      } catch (_) {
        copied = copyWithFallback();
      }

      if (copied) {
        showTooltip();
      } else {
        // Dernier recours : comportement mailto classique.
        window.location.href = contactLink.getAttribute("href");
      }
    });

    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape") hideTooltip();
    });
  }

})(); // Fin de la fonction IIFE globale