const STORAGE_KEY = "theme";
const root = document.documentElement;
const mediaDark = window.matchMedia("(prefers-color-scheme: dark)");
const btn = document.getElementById("themeBtn");
const menu = document.getElementById("themeMenu");


function setColorSchemeHint(mode) {
  if (mode === "system") {
    root.style.colorScheme = mediaDark.matches ? "dark" : "light";
  } else {
    root.style.colorScheme = mode;
  }
}


function applyTheme(mode) {
  if (mode === "system") {
    root.removeAttribute("data-theme");
  } else {
    root.setAttribute("data-theme", mode);
  }

  localStorage.setItem(STORAGE_KEY, mode);
  setColorSchemeHint(mode);

  menu.querySelectorAll(".theme-item").forEach((el) => {
    el.setAttribute("aria-checked", String(el.dataset.theme === mode));
  });
}


function currentMode() {
  return localStorage.getItem(STORAGE_KEY) || "system";
}


function openMenu() {
  menu.hidden = false;
  btn.setAttribute("aria-expanded", "true");

  const current = menu.querySelector('.theme-item[aria-checked="true"]');
  (current || menu.querySelector(".theme-item"))?.focus();
}


function closeMenu() {
  menu.hidden = true;
  btn.setAttribute("aria-expanded", "false");
  btn.focus();
}


function toggleMenu() {
  if (menu.hidden) openMenu();
  else closeMenu();
}


function handleOutsideClick(e) {
  if (!menu.contains(e.target) && e.target !== btn) closeMenu();
}


function handleMenuClick(e) {
  const item = e.target.closest(".theme-item");
  if (!item) return;
  applyTheme(item.dataset.theme);
  closeMenu();
}


function handleMenuKeydown(e) {
  const items = Array.from(menu.querySelectorAll(".theme-item"));
  const idx = items.indexOf(document.activeElement);

  switch (e.key) {
    case "ArrowDown":
      e.preventDefault();
      items[(idx + 1) % items.length]?.focus();
      break;
    case "ArrowUp":
      e.preventDefault();
      items[(idx - 1 + items.length) % items.length]?.focus();
      break;
    case "Home":
      e.preventDefault();
      items[0]?.focus();
      break;
    case "End":
      e.preventDefault();
      items[items.length - 1]?.focus();
      break;
    case "Enter":
    case " ":
      e.preventDefault();
      document.activeElement?.click();
      break;
    case "Escape":
      e.preventDefault();
      closeMenu();
      break;
  }
}

document.addEventListener("DOMContentLoaded", () => {
  // Проставить aria-checked по сохранённому выбору
  applyTheme(currentMode());

  btn.addEventListener("click", toggleMenu);
  document.addEventListener("click", handleOutsideClick);
  menu.addEventListener("click", handleMenuClick);
  menu.addEventListener("keydown", handleMenuKeydown);

  // Реакция на смену системной темы в режиме "system"
  mediaDark.addEventListener?.("change", () => {
    if (currentMode() === "system") setColorSchemeHint("system");
  });
});
