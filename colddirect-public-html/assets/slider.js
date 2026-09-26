(function () {
  var root = document.getElementById("home-slider");
  var track = document.getElementById("coldSlider");
  var dotsContainer = document.getElementById("home-slider-dots");
  if (!root || !track || !dotsContainer) return;
  var current = 0;
  dotsContainer.innerHTML = "";
  for (let i = 0; i < 7; i++) dotsContainer.innerHTML += `<span onclick="goTo(${i})"></span>`;
  function goTo(next) {
    current = ((next % 7) + 7) % 7;
    track.style.transform = `translateX(-${current * 14.2857}%)`;
    for (var d = 0; d < dotsContainer.children.length; d++) {
      dotsContainer.children[d].className = d === current ? "on" : "";
    }
  }
  window.goTo = goTo;
  goTo(0);
  var nextBtn = root.querySelector(".next");
  var prevBtn = root.querySelector(".prev");
  if (nextBtn) nextBtn.addEventListener("click", function () { goTo(current + 1); });
  if (prevBtn) prevBtn.addEventListener("click", function () { goTo(current - 1); });
  var startX = 0;
  root.addEventListener("touchstart", function (e) {
    if (e.changedTouches && e.changedTouches[0]) startX = e.changedTouches[0].clientX;
  }, { passive: true });
  root.addEventListener("touchend", function (e) {
    if (!e.changedTouches || !e.changedTouches[0]) return;
    var dx = e.changedTouches[0].clientX - startX;
    if (dx > 40) goTo(current - 1);
    else if (dx < -40) goTo(current + 1);
  }, { passive: true });
  setInterval(function () { goTo(current + 1); }, 3500);
})();
