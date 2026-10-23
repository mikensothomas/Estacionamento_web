(async function() {
  const token = localStorage.getItem("token");
  if (!token) return window.location.replace("/");
  const logout = document.getElementById("logoutButton");
  logout.hidden = false;
  logout.addEventListener("click", async () => {
    try { await fetch("/api/auth/logout", {method:"POST", headers:{Authorization:`Bearer ${token}`}}); } catch (_) {}
    localStorage.removeItem("token"); localStorage.removeItem("token_expira_em");
    window.location.replace("/");
  });
  async function buscar(url) {
    const r = await fetch(url, {headers:{Authorization:`Bearer ${token}`}});
    if (r.status === 401) { localStorage.clear(); window.location.replace("/"); throw new Error("Sessão expirada"); }
    if (!r.ok) throw new Error("Falha ao consultar dados");
    return r.json();
  }
  try {
    const [clientes, veiculos, vagas] = await Promise.all([
      buscar("/api/clientes/"), buscar("/api/veiculos/"), buscar("/api/vagas/")
    ]);
    document.getElementById("totalClientes").textContent = clientes.length;
    document.getElementById("totalVeiculos").textContent = veiculos.length;
    document.getElementById("totalVagas").textContent = vagas.filter(v => v.disponibilidade === "Disponível").length;
    document.getElementById("totalOcupadas").textContent = vagas.filter(v => v.disponibilidade === "Ocupada").length;
  } catch (e) {
    const fb=document.getElementById("feedback"); fb.textContent=e.message; fb.className="feedback show error";
  }
})();
