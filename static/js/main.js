// Reusable vanilla-JS utilities used across the SPMS frontend.

function spmsToggleSidebar() {
  document.querySelector(".spms-sidebar").classList.toggle("show");
}

function spmsConfirm(message) {
  return window.confirm(message || "Are you sure?");
}

function spmsAttachConfirm() {
  document.querySelectorAll("[data-confirm]").forEach((form) => {
    form.addEventListener("submit", (e) => {
      if (!spmsConfirm(form.getAttribute("data-confirm"))) {
        e.preventDefault();
      }
    });
  });
}

function getCsrfToken() {
  const el = document.querySelector("[name=csrfmiddlewaretoken]");
  return el ? el.value : "";
}

async function spmsPost(url) {
  const response = await fetch(url, {
    method: "POST",
    headers: { "X-CSRFToken": getCsrfToken() },
  });
  return response;
}

function spmsInitTooltips() {
  if (window.bootstrap) {
    document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach((el) => new bootstrap.Tooltip(el));
  }
}

document.addEventListener("DOMContentLoaded", () => {
  spmsAttachConfirm();
  spmsInitTooltips();
  const toggleBtn = document.getElementById("sidebarToggle");
  if (toggleBtn) toggleBtn.addEventListener("click", spmsToggleSidebar);
});
