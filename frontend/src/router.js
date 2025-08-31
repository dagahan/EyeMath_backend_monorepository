// router.js
/** простая карта маршрутов: path -> factory(qs) -> Node */
const routes = new Map();

/** @param {string} path @param {(qs: URLSearchParams) => Node} factory */
export function route(path, factory) {
  routes.set(path, factory);
}

/** @param {string} to */
export function go(to) {
  location.hash = to.startsWith("#") ? to : `#${to}`;
}

/** @param {HTMLElement} mount */
export function startRouter(mount) {
  if (!mount) throw new Error("startRouter: mount element not found");

  function render() {
    const raw = location.hash.replace(/^#/, "") || "/";
    const [path, query] = raw.split("?");
    const make = routes.get(path) || routes.get("*") || routes.get("/");
    if (!make) {
      console.warn("No route for", path);
      return;
    }

    mount.replaceChildren(make(new URLSearchParams(query || "")));

    // show/hide menu elements by authorization
    const authed =
      !!localStorage.getItem("em_access") || !!localStorage.getItem("em_refresh");
    document.querySelectorAll(".auth-only").forEach((el) => {
      const needIn = el.dataset.auth === "in";
      el.style.display = (needIn ? authed : !authed) ? "" : "none";
    });
  }

  addEventListener("hashchange", render);
  render();
}