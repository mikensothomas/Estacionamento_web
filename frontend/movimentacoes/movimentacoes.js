const API_MOV = "/api/movimentacoes";
const token = localStorage.getItem("token");
const feedback = document.getElementById("feedback");
const entryForm = document.getElementById("entryForm");
let veiculos = [], clientes = [], vagas = [], abertas = [], historico = [];

if (!token) window.location.replace("/");
const logout = document.getElementById("logoutButton");
logout.hidden = false;
logout.addEventListener("click", async () => {
  try { await fetch("/api/auth/logout", { method: "POST", headers: { Authorization: `Bearer ${token}` } }); } catch (_) {}
  localStorage.removeItem("token");
  localStorage.removeItem("token_expira_em");
  window.location.replace("/");
});

function avisar(mensagem, tipo = "success") {
  feedback.textContent = mensagem;
  feedback.className = `feedback show ${tipo}`;
  window.scrollTo({ top: 0, behavior: "smooth" });
}

async function requisicao(url, options = {}) {
  const headers = { Authorization: `Bearer ${token}`, ...(options.headers || {}) };
  if (options.body) headers["Content-Type"] = "application/json";
  const response = await fetch(url, { ...options, headers });
  if (response.status === 401) {
    localStorage.removeItem("token");
    localStorage.removeItem("token_expira_em");
    window.location.replace("/");
    throw new Error("Sessão expirada. Entre novamente.");
  }
  const data = response.status === 204 ? null : await response.json().catch(() => ({}));
  if (!response.ok) {
    let detail = data?.detail || "Ocorreu um erro.";
    if (Array.isArray(detail)) detail = detail.map(item => item.msg).join("; ");
    throw new Error(detail);
  }
  return data;
}

function dataHora(valor) {
  if (!valor) return "—";
  const data = new Date(valor);
  return Number.isNaN(data.getTime()) ? valor : data.toLocaleString("pt-BR");
}
function moeda(valor) {
  return Number(valor || 0).toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
}
function tempoDecorrido(valor) {
  const inicio = new Date(valor).getTime();
  const minutos = Math.max(0, Math.floor((Date.now() - inicio) / 60000));
  const dias = Math.floor(minutos / 1440);
  const horas = Math.floor((minutos % 1440) / 60);
  const resto = minutos % 60;
  return dias ? `${dias}d ${horas}h ${resto}min` : `${horas}h ${resto}min`;
}
function veiculoPorId(id) { return veiculos.find(item => item.id_veiculo === id); }
function clientePorId(id) { return clientes.find(item => item.id_cliente === id); }
function vagaPorId(id) { return vagas.find(item => item.id_vaga === id); }

function preencherSelects() {
  const selectVeiculo = document.getElementById("id_veiculo");
  const selectVaga = document.getElementById("id_vaga");
  selectVeiculo.innerHTML = '<option value="">Selecione um veículo...</option>';
  veiculos.forEach(item => {
    const cliente = clientePorId(item.id_cliente);
    const option = document.createElement("option");
    option.value = item.id_veiculo;
    option.textContent = `${item.placa} — ${item.modelo} (${cliente?.nome_completo || "Cliente não identificado"})`;
    selectVeiculo.appendChild(option);
  });
  selectVaga.innerHTML = '<option value="">Selecione uma vaga...</option>';
  vagas.filter(item => item.disponibilidade === "Disponível").forEach(item => {
    const option = document.createElement("option");
    option.value = item.id_vaga;
    option.textContent = `Vaga ${item.numero_vaga}`;
    selectVaga.appendChild(option);
  });
  selectVeiculo.disabled = veiculos.length === 0;
  selectVaga.disabled = !vagas.some(item => item.disponibilidade === "Disponível");
  document.getElementById("entryButton").disabled = selectVeiculo.disabled || selectVaga.disabled;
}

function renderizarAbertas() {
  const body = document.getElementById("openBody");
  body.innerHTML = "";
  document.getElementById("openCount").textContent = `${abertas.length} veículo(s) no estacionamento`;
  document.getElementById("totalAbertas").textContent = abertas.length;
  if (!abertas.length) {
    body.innerHTML = '<tr><td colspan="7" class="empty-state">Nenhum veículo no estacionamento.</td></tr>';
    return;
  }
  abertas.forEach(mov => {
    const veiculo = veiculoPorId(mov.id_veiculo);
    const cliente = veiculo ? clientePorId(veiculo.id_cliente) : null;
    const vaga = vagaPorId(mov.id_vaga);
    const tr = document.createElement("tr");
    const valores = [veiculo?.placa || `Veículo #${mov.id_veiculo}`, veiculo ? `${veiculo.marca} ${veiculo.modelo}` : "—", cliente?.nome_completo || "—", vaga ? `Vaga ${vaga.numero_vaga}` : `Vaga #${mov.id_vaga}`, dataHora(mov.data_hora_entrada), tempoDecorrido(mov.data_hora_entrada)];
    valores.forEach(valor => { const td = document.createElement("td"); td.textContent = valor; tr.appendChild(td); });
    const td = document.createElement("td");
    const button = document.createElement("button");
    button.type = "button"; button.className = "action-button"; button.textContent = "Registrar saída";
    button.addEventListener("click", () => registrarSaida(mov));
    td.appendChild(button); tr.appendChild(td); body.appendChild(tr);
  });
}

function renderizarHistorico() {
  const body = document.getElementById("historyBody");
  body.innerHTML = "";
  document.getElementById("historyCount").textContent = `${historico.length} movimentação(ões) finalizada(s)`;
  if (!historico.length) {
    body.innerHTML = '<tr><td colspan="6" class="empty-state">Nenhuma saída registrada.</td></tr>';
    return;
  }
  historico.forEach(mov => {
    const veiculo = veiculoPorId(mov.id_veiculo);
    const vaga = vagaPorId(mov.id_vaga);
    const tr = document.createElement("tr");
    [veiculo?.placa || `Veículo #${mov.id_veiculo}`, vaga ? `Vaga ${vaga.numero_vaga}` : `Vaga #${mov.id_vaga}`, dataHora(mov.data_hora_entrada), dataHora(mov.data_hora_saida), moeda(mov.valor_total)].forEach(valor => {
      const td = document.createElement("td"); td.textContent = valor; tr.appendChild(td);
    });
    const td = document.createElement("td"); td.innerHTML = '<span class="status-pill">Finalizada</span>'; tr.appendChild(td);
    body.appendChild(tr);
  });
}

async function registrarSaida(mov) {
  const veiculo = veiculoPorId(mov.id_veiculo);
  const placa = veiculo?.placa || `veículo #${mov.id_veiculo}`;
  if (!window.confirm(`Confirma a saída do ${placa}? O sistema calculará o valor conforme o tipo de cliente.`)) return;
  try {
    const resultado = await requisicao(`${API_MOV}/saida/${mov.id_movimentacao}`, { method: "POST" });
    avisar(`Saída registrada. Valor calculado: ${moeda(resultado.valor_total)}.`, "success");
    await carregarTudo();
  } catch (erro) { avisar(erro.message, "error"); }
}

async function carregarTudo() {
  try {
    const resultados = await Promise.all([
      requisicao("/api/veiculos/"), requisicao("/api/clientes/"),
      requisicao("/api/vagas/"), requisicao(`${API_MOV}/abertas`),
      requisicao(`${API_MOV}/historico`)
    ]);
    [veiculos, clientes, vagas, abertas, historico] = resultados;
    preencherSelects();
    renderizarAbertas();
    renderizarHistorico();
    const disponiveis = vagas.filter(item => item.disponibilidade === "Disponível").length;
    const ocupadas = vagas.filter(item => item.disponibilidade === "Ocupada").length;
    const hoje = new Date().toLocaleDateString("pt-BR");
    const saidasHoje = historico.filter(item => item.data_hora_saida && new Date(item.data_hora_saida).toLocaleDateString("pt-BR") === hoje).length;
    document.getElementById("totalDisponiveis").textContent = disponiveis;
    document.getElementById("totalOcupadas").textContent = ocupadas;
    document.getElementById("totalSaidas").textContent = saidasHoje;
  } catch (erro) { avisar(erro.message, "error"); }
}

entryForm.addEventListener("submit", async event => {
  event.preventDefault();
  const button = document.getElementById("entryButton");
  button.disabled = true;
  try {
    await requisicao(`${API_MOV}/entrada`, {
      method: "POST",
      body: JSON.stringify({ id_veiculo: Number(document.getElementById("id_veiculo").value), id_vaga: Number(document.getElementById("id_vaga").value) })
    });
    entryForm.reset();
    avisar("Entrada registrada e vaga ocupada com sucesso.", "success");
    await carregarTudo();
  } catch (erro) { avisar(erro.message, "error"); }
  finally { button.disabled = false; }
});

document.getElementById("refreshButton").addEventListener("click", carregarTudo);
document.getElementById("historyButton").addEventListener("click", carregarTudo);
carregarTudo();
setInterval(carregarTudo, 30000);