(function () {
  var root = document.getElementById("home-slider");
  if (!root) return;
  var slides = root.querySelectorAll(".slide");
  var dots = document.getElementById("home-slider-dots");
  if (!slides.length || !dots) return;
  var i = 0;
  var n;
  for (n = 0; n < slides.length; n++) {
    var b = document.createElement("button");
    b.type = "button";
    if (n === 0) b.className = "on";
    b.setAttribute("aria-label", "Go to slide " + (n + 1));
    b.addEventListener("click", (function (idx) {
      return function () { go(idx); };
    })(n));
    dots.appendChild(b);
  }
  function go(next) {
    slides[i].classList.remove("on");
    if (dots.children[i]) dots.children[i].classList.remove("on");
    i = (next + slides.length) % slides.length;
    slides[i].classList.add("on");
    if (dots.children[i]) dots.children[i].classList.add("on");
  }
  var nextBtn = root.querySelector(".next");
  var prevBtn = root.querySelector(".prev");
  if (nextBtn) nextBtn.addEventListener("click", function () { go(i + 1); });
  if (prevBtn) prevBtn.addEventListener("click", function () { go(i - 1); });
  setInterval(function () { go(i + 1); }, 4500);
})();
