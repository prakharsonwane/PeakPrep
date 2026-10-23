"use strict";

document.addEventListener("DOMContentLoaded", () => {
  const menuToggle = document.getElementById("menuToggle");
  const navLinks = document.getElementById("navLinks");
  const themeToggle = document.getElementById("themeToggle");

  // Mobile navigation
  if (menuToggle && navLinks) {
    menuToggle.addEventListener("click", () => {
      const isOpen = navLinks.classList.toggle("is-open");

      menuToggle.setAttribute("aria-expanded", String(isOpen));
      menuToggle.setAttribute(
        "aria-label",
        isOpen ? "Close navigation" : "Open navigation"
      );
    });

    navLinks.querySelectorAll("a").forEach((link) => {
      link.addEventListener("click", () => {
        navLinks.classList.remove("is-open");
        menuToggle.setAttribute("aria-expanded", "false");
        menuToggle.setAttribute("aria-label", "Open navigation");
      });
    });
  }

  // Light and dark theme
  const savedTheme = (() => {
    try {
      return localStorage.getItem("peakprep-theme");
    } catch {
      return null;
    }
  })();

  function applyTheme(theme) {
    const isDark = theme === "dark";

    document.body.classList.toggle("dark-theme", isDark);

    if (themeToggle) {
      themeToggle.textContent = isDark ? "☀" : "☾";
      themeToggle.setAttribute(
        "aria-label",
        isDark ? "Switch to light theme" : "Switch to dark theme"
      );
      themeToggle.setAttribute(
        "title",
        isDark ? "Switch to light theme" : "Switch to dark theme"
      );
    }
  }

  applyTheme(savedTheme === "dark" ? "dark" : "light");

  if (themeToggle) {
    themeToggle.addEventListener("click", () => {
      const nextTheme = document.body.classList.contains("dark-theme")
        ? "light"
        : "dark";

      applyTheme(nextTheme);

      try {
        localStorage.setItem("peakprep-theme", nextTheme);
      } catch {
        // Theme still works if browser storage is unavailable.
      }
    });
  }

  console.log("PeakPrep is ready.");
});