document.addEventListener("DOMContentLoaded", function() {
    const form = document.querySelector("form");
    const button = document.querySelector("button");

    form.addEventListener("submit", function() {
        button.innerHTML = "⏳ Converting...";
        button.style.background = "#555";
        button.disabled = true;
    });
});
