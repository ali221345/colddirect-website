(function () {
  var sharedNav = document.querySelector(".cd-nav");
  if (sharedNav) {
    var menuButton = document.createElement("button");
    menuButton.type = "button";
    menuButton.className = "cd-nav-toggle";
    menuButton.textContent = "Menu";
    if (!sharedNav.id) sharedNav.id = "cd-main-navigation";
    menuButton.setAttribute("aria-controls", sharedNav.id);
    menuButton.setAttribute("aria-expanded", "false");
    sharedNav.parentElement.insertBefore(menuButton, sharedNav);
    function closeMenu() {
      sharedNav.classList.remove("open");
      menuButton.setAttribute("aria-expanded", "false");
    }
    menuButton.addEventListener("click", function () {
      var opened = sharedNav.classList.toggle("open");
      menuButton.setAttribute("aria-expanded", String(opened));
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && sharedNav.classList.contains("open")) {
        closeMenu();
        menuButton.focus();
      }
    });
    sharedNav.addEventListener("click", function (e) {
      if (e.target.closest("a") && window.matchMedia("(max-width: 900px)").matches) closeMenu();
    });
  }

  var btn = document.querySelector(".nav-toggle");
  var nav = document.querySelector("nav");
  if (btn && nav) {
    btn.addEventListener("click", function () {
      nav.classList.toggle("open");
    });
  }
  document.querySelectorAll(".has-sub > a").forEach(function (link) {
    link.addEventListener("click", function (e) {
      if (window.matchMedia("(max-width: 900px)").matches) {
        e.preventDefault();
        link.parentElement.classList.toggle("open");
      }
    });
  });
})();
