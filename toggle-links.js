// toggle-links.js
document.addEventListener("DOMContentLoaded", function () {
  const icon = document.getElementById("link-toggle-icon");
  const toggleBtn = document.getElementById("link-toggle-btn");

  const setLinkBehavior = (newTab) => {
    document.querySelectorAll("a").forEach(link => {
      if (link.href && !link.href.startsWith("#") && !link.classList.contains("no-toggle")) {
        if (newTab) {
          link.setAttribute("target", "_blank");
        } else {
          link.removeAttribute("target");
        }
      }
    });

    icon.classList = newTab ? "fas fa-external-link-alt" : "fas fa-link";
    toggleBtn.title = newTab ? "Links open in new tab" : "Links open in same tab";
  };

  // Initialize based on localStorage
  let openInNewTab = localStorage.getItem("openInNewTab") === "true";
  setLinkBehavior(openInNewTab);

  toggleBtn.addEventListener("click", function (e) {
    e.preventDefault();
    openInNewTab = !openInNewTab;
    localStorage.setItem("openInNewTab", openInNewTab);
    setLinkBehavior(openInNewTab);
  });
});