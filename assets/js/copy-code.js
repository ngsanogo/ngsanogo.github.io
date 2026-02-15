document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".highlight").forEach(function (block) {
        var code = block.querySelector("code");
        if (!code) return;

        var button = document.createElement("button");
        button.type = "button";
        button.className = "copy-button";
        button.textContent = "Copy";

        button.addEventListener("click", function () {
            if (!navigator.clipboard) return;
            navigator.clipboard.writeText(code.innerText).then(function () {
                button.textContent = "Copied";
                setTimeout(function () {
                    button.textContent = "Copy";
                }, 1500);
            });
        });

        block.appendChild(button);
    });
});
