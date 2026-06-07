document.addEventListener("click", (event) => {
  const trigger = event.target.closest("[data-mobile-menu]");
  if (!trigger) return;
  const menu = document.querySelector("[data-mobile-nav]");
  if (!menu) return;
  menu.classList.toggle("hidden");
  menu.classList.toggle("grid");
});

document.addEventListener("DOMContentLoaded", () => {
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
