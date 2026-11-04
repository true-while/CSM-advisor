document.querySelectorAll(".copy-btn").forEach((button) => {
  button.addEventListener("click", async () => {
    const code = button.previousElementSibling.textContent;
    try {
      await navigator.clipboard.writeText(code);
      const original = button.textContent;
      button.textContent = "Copied!";
      setTimeout(() => { button.textContent = original; }, 1500);
    } catch (err) {
      button.textContent = "Copy failed";
    }
  });
});
