const form = document.getElementById("loginForm");
const feedback = document.getElementById("feedback");
const senha = document.getElementById("senha");
const mostrarSenha = document.getElementById("mostrarSenha");

function mensagem(texto, tipo = "error") {
  feedback.textContent = texto;
  feedback.className = `feedback show ${tipo}`;
}
if (mostrarSenha) {
  mostrarSenha.addEventListener("click", () => {
    const visivel = senha.type === "password";
    senha.type = visivel ? "text" : "password";
    mostrarSenha.textContent = visivel ? "Ocultar" : "Mostrar";
  });
}
if (localStorage.getItem("token")) {
  window.location.replace("/pagina/inicial");
}
form?.addEventListener("submit", async (event) => {
  event.preventDefault();
  const email = document.getElementById("email").value.trim();
  const password = senha.value;
  try {
    const response = await fetch("/api/auth/login", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({email, senha: password})
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || "Não foi possível entrar.");
    localStorage.setItem("token", data.access_token);
    localStorage.setItem("token_expira_em", String(Date.now() + data.expires_in * 1000));
    window.location.replace("/pagina/inicial");
  } catch (error) {
    mensagem(error.message || "Erro de conexão com o servidor.");
  }
});
