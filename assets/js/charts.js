// Hover and keyboard tooltips for charts: any element with data-tip inside [data-chart].
document.querySelectorAll("[data-chart]").forEach((chart) => {
  const tip = document.createElement("div");
  tip.className = "chart-tip";
  tip.hidden = true;
  tip.setAttribute("role", "status");
  chart.appendChild(tip);

  const show = (el, x, y) => {
    tip.textContent = el.dataset.tip;
    tip.hidden = false;
    const box = chart.getBoundingClientRect();
    const left = Math.min(x - box.left + 12, box.width - tip.offsetWidth - 8);
    tip.style.left = Math.max(8, left) + "px";
    tip.style.top = (y - box.top - tip.offsetHeight - 10) + "px";
  };
  const hide = () => { tip.hidden = true; };

  chart.querySelectorAll("[data-tip]").forEach((el) => {
    el.setAttribute("tabindex", "0");
    el.addEventListener("pointermove", (e) => show(el, e.clientX, e.clientY));
    el.addEventListener("pointerleave", hide);
    el.addEventListener("focus", () => {
      const r = el.getBoundingClientRect();
      show(el, r.left + r.width / 2, r.top);
    });
    el.addEventListener("blur", hide);
  });
});
