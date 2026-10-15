// Design-notes toggle, mobile menu and theme chips for the wireframes.
const notesBtn = document.querySelector("[data-toggle-notes]");
if (notesBtn) {
  const set = (on) => {
    document.body.classList.toggle("show-notes", on);
    notesBtn.setAttribute("aria-pressed", String(on));
  };
  set(new URLSearchParams(location.search).has("notes"));
  notesBtn.addEventListener("click", () => set(notesBtn.getAttribute("aria-pressed") !== "true"));
}

const nav = document.querySelector(".nav");
const navBtn = document.querySelector(".nav-toggle");
if (nav && navBtn) {
  navBtn.addEventListener("click", () => {
    const open = nav.classList.toggle("open");
    navBtn.setAttribute("aria-expanded", String(open));
  });
}

document.querySelectorAll(".chips button").forEach((chip, _, all) => {
  chip.addEventListener("click", () => {
    all.forEach((c) => c.setAttribute("aria-pressed", String(c === chip)));
  });
});

const theme = document.getElementById("theme");
const themeBtn = document.querySelector("[data-toggle-theme]");
const label = document.querySelector("[data-fidelity-label]");
if (theme && themeBtn) {
  const setTheme = (on) => {
    theme.disabled = !on;
    themeBtn.setAttribute("aria-pressed", String(on));
    themeBtn.textContent = on ? "Styled" : "Wireframe";
    if (label) label.textContent = on ? "STYLED" : "WIREFRAME";
  };
  setTheme(!new URLSearchParams(location.search).has("wireframe"));
  themeBtn.addEventListener("click", () => setTheme(theme.disabled));
}
