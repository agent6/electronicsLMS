document.addEventListener("click", (event) => {
  const trigger = event.target.closest("[data-mobile-menu]");
  if (!trigger) return;
  const menu = document.querySelector("[data-mobile-nav]");
  if (!menu) return;
  menu.classList.toggle("hidden");
  menu.classList.toggle("grid");
});

document.addEventListener("DOMContentLoaded", () => {
  const lightbox = document.querySelector("[data-part-lightbox]");
  if (lightbox) {
    const image = lightbox.querySelector("[data-lightbox-image]");
    const title = lightbox.querySelector("[data-lightbox-title]");
    const caption = lightbox.querySelector("[data-lightbox-caption]");
    const closeButton = lightbox.querySelector(".part-lightbox__close");
    let lastFocusedElement = null;

    const closeLightbox = () => {
      lightbox.hidden = true;
      lightbox.classList.remove("is-open");
      lightbox.setAttribute("aria-hidden", "true");
      document.body.classList.remove("lightbox-open");
      if (image) {
        image.removeAttribute("src");
        image.alt = "";
      }
      if (lastFocusedElement) {
        lastFocusedElement.focus();
      }
    };

    document.querySelectorAll("[data-lightbox-src]").forEach((trigger) => {
      trigger.addEventListener("click", () => {
        lastFocusedElement = trigger;
        if (image) {
          image.src = trigger.dataset.lightboxSrc;
          image.alt = trigger.dataset.lightboxAlt || "";
        }
        if (title) {
          title.textContent = trigger.dataset.lightboxTitle || "";
        }
        if (caption) {
          caption.textContent = trigger.dataset.lightboxCaption || "";
          caption.hidden = !trigger.dataset.lightboxCaption;
        }
        lightbox.hidden = false;
        lightbox.classList.add("is-open");
        lightbox.setAttribute("aria-hidden", "false");
        document.body.classList.add("lightbox-open");
        closeButton?.focus();
      });
    });

    lightbox.querySelectorAll("[data-lightbox-close]").forEach((trigger) => {
      trigger.addEventListener("click", closeLightbox);
    });

    document.addEventListener("keydown", (event) => {
      if (lightbox.hidden) return;
      if (event.key === "Escape") {
        closeLightbox();
      }
    });
  }

  if (!window.Quill) return;

  document.querySelectorAll("[data-rich-text-editor]").forEach((editor) => {
    if (editor.dataset.quillReady === "true") return;

    const field = editor.closest("[data-rich-text-field]");
    const input = field?.querySelector("[data-rich-text-input]");
    if (!input) return;

    const quill = new window.Quill(editor, {
      theme: "snow",
      placeholder: editor.dataset.placeholder || "",
      modules: {
        toolbar: [
          ["bold", "italic", "underline"],
          [{ list: "ordered" }, { list: "bullet" }],
          ["blockquote", "link"],
          ["clean"],
        ],
      },
    });

    if (input.value) {
      quill.root.innerHTML = input.value;
    }

    const syncEditor = () => {
      input.value = quill.root.innerHTML.trim();
    };

    quill.on("text-change", syncEditor);
    editor.closest("form")?.addEventListener("submit", syncEditor);
    editor.dataset.quillReady = "true";
  });
});
