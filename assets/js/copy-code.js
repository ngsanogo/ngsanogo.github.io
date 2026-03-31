document.addEventListener("DOMContentLoaded", function () {
  document.querySelectorAll(".highlight").forEach(function (block) {
    var code = block.querySelector("code");
    if (!code || !navigator.clipboard) return;

    var button = document.createElement("button");
    button.type = "button";
    button.className = "copy-button";
    button.textContent = "Copier";
    button.setAttribute("aria-label", "Copier le bloc de code");

    button.addEventListener("click", function () {
      navigator.clipboard.writeText(code.textContent).then(function () {
        button.textContent = "Copié";
        setTimeout(function () {
          button.textContent = "Copier";
        }, 1500);
      });
    });

    block.appendChild(button);
  });
});
