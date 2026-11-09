// Add Bootstrap styling to Django-generated form controls.
document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll("input:not([type=radio]):not([type=checkbox]), textarea, select").forEach(function (field) {
        if (!field.classList.contains("form-control") && !field.classList.contains("form-select")) {
            field.classList.add(field.tagName === "SELECT" ? "form-select" : "form-control");
        }
    });
});
