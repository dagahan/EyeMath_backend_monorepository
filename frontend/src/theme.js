import { THEMES, STORAGE_KEYS } from './core/constants.js';

let currentTheme = localStorage.getItem(STORAGE_KEYS.THEME) || THEMES.SYSTEM;

export function initTheme() {
  applyTheme(currentTheme);
  setupThemeSwitcher();
}

function applyTheme(theme) {
  const root = document.documentElement;
  
  if (theme === THEMES.SYSTEM) {
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    root.setAttribute('data-theme', prefersDark ? THEMES.DARK : THEMES.LIGHT);
  } else {
    root.setAttribute('data-theme', theme);
  }
  
  currentTheme = theme;
  localStorage.setItem(STORAGE_KEYS.THEME, theme);
}

function setupThemeSwitcher() {
  const themeBtn = document.getElementById('themeBtn');
  const themeMenu = document.getElementById('themeMenu');
  const themeItems = document.querySelectorAll('.theme-item');
  
  console.log('Theme elements found:', { themeBtn, themeMenu, themeItems: themeItems.length });
  
  if (!themeBtn || !themeMenu) {
    console.warn('Theme button or menu not found');
    return;
  }
  
  themeBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    const isHidden = themeMenu.hasAttribute('hidden');
    
    if (isHidden) {
      themeMenu.removeAttribute('hidden');
      themeBtn.setAttribute('aria-expanded', 'true');
    } else {
      themeMenu.setAttribute('hidden', '');
      themeBtn.setAttribute('aria-expanded', 'false');
    }
  });
  
  document.addEventListener('click', (e) => {
    if (!themeMenu.contains(e.target) && e.target !== themeBtn) {
      themeMenu.setAttribute('hidden', '');
      themeBtn.setAttribute('aria-expanded', 'false');
    }
  });
  
  themeItems.forEach(item => {
    item.addEventListener('click', () => {
      const theme = item.dataset.theme;
      applyTheme(theme);
      
      themeItems.forEach(i => i.setAttribute('aria-checked', 'false'));
      item.setAttribute('aria-checked', 'true');
      
      themeMenu.setAttribute('hidden', '');
      themeBtn.setAttribute('aria-expanded', 'false');
    });
  });
  
  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
    if (currentTheme === THEMES.SYSTEM) {
      applyTheme(THEMES.SYSTEM);
    }
  });
  
  const currentItem = document.querySelector(`[data-theme="${currentTheme}"]`);
  if (currentItem) {
    currentItem.setAttribute('aria-checked', 'true');
  }
}