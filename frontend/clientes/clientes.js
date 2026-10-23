const API = "/api/clientes/";
const form = document.getElementById("recordForm");
const feedback = document.getElementById("feedback");
const tbody = document.getElementById("tableBody");
const thead = document.getElementById("tableHead");
const token = localStorage.getItem("token");
let registros = [];
let editandoId = null;
const campos = ["cpf", "nome_completo", "email", "telefone", "tipo_cliente"];
const colunas = [["id_cliente", "ID"], ["cpf", "CPF"], ["nome_completo", "Nome completo"], ["email", "E-mail"], ["telefone", "Telefone"], ["tipo_cliente", "Tipo"]];
const opcoes = {"tipo_cliente": [["Horista", "Horista"], ["Mensalista", "Mensalista"]]};

if (!token) window.location.replace("/");
const logout = document.getElementById("logoutButton");
logout.hidden = false;
logout.addEventListener("click", async () => {
  try { await fetch("/api/auth/logout", {method:"POST",headers:{Authorization:`Bearer ${token}`}}); } catch (_) {}
  localStorage.removeItem("token"); localStorage.removeItem("token_expira_em"); window.location.replace("/");
});
document.querySelectorAll(".nav-links a").forEach(a => { if (a.getAttribute("href") === "/pagina/clientes") a.classList.add("active"); });

function avisar(texto, tipo="success") {
  feedback.textContent = texto; feedback.className = `feedback show ${tipo}`;
  window.scrollTo({top:0,behavior:"smooth"});
}
async function requisicao(url, options={}) {
  const headers = {Authorization:`Bearer ${token}`, ...(options.headers||{})};
  if (options.body) headers["Content-Type"]="application/json";
  const response = await fetch(url, {...options,headers});
  if (response.status === 401) {
    localStorage.removeItem("token"); localStorage.removeItem("token_expira_em");
    window.location.replace("/"); throw new Error("Sessão expirada. Entre novamente.");
  }
  if (response.status === 204) return null;
  const data = await response.json().catch(()=>({}));
  if (!response.ok) {
    let detail = data.detail || "Ocorreu um erro.";
    if (Array.isArray(detail)) detail = detail.map(x=>x.msg).join("; ");
    throw new Error(detail);
  }
  return data;
}
function labelFor(campo) {
  const labels = {"cpf": "CPF", "nome_completo": "Nome completo", "email": "E-mail", "telefone": "Telefone", "tipo_cliente": "Tipo de cliente"};
  return labels[campo] || campo;
}
function desenharFormulario() {
  form.innerHTML = "";
  for (const campo of [["cpf", "CPF", "text", "11", "Digite 11 números"], ["nome_completo", "Nome completo", "text", "150", "Nome e sobrenome"], ["email", "E-mail", "email", "150", "nome@exemplo.com"], ["telefone", "Telefone", "tel", "20", "(99) 99999-9999"], ["tipo_cliente", "Tipo de cliente", "select", "", ""]]) {
    const [nome, rotulo, tipo, max, placeholder] = campo;
    const wrap = document.createElement("div"); wrap.className="field";
    const label = document.createElement("label"); label.htmlFor=nome; label.textContent=rotulo;
    let input;
    if (tipo === "select") {
      input=document.createElement("select");
      input.innerHTML='<option value="">Selecione...</option>';
      if (nome === "id_cliente") {
        // opções serão preenchidas pela lista de clientes
      } else {
        for (const [valor,texto] of (opcoes[nome]||[])) {
          const opt=document.createElement("option"); opt.value=valor; opt.textContent=texto; input.appendChild(opt);
        }
      }
    } else {
      input=document.createElement("input"); input.type=tipo;
      if (max) input.maxLength=Number(max);
      if (tipo === "number") { input.step = nome.startsWith("valor_") ? "0.01" : "1"; if (nome.startsWith("valor_")) input.min="0"; else input.min="1"; }
      if (tipo === "password") input.minLength=8;
      if (nome === "cpf") { input.inputMode="numeric"; }
      if (nome === "placa") { input.autocapitalize="characters"; }
      input.placeholder=placeholder;
    }
    input.id=nome; input.name=nome; input.required=true;
    wrap.append(label,input); form.appendChild(wrap);
  }
  if (campos.includes("id_cliente")) carregarOpcoesClientes();
}
async function carregarOpcoesClientes() {
  const select=document.getElementById("id_cliente"); if (!select) return;
  try {
    const clientes=await requisicao("/api/clientes/");
    for (const c of clientes) {
      const opt=document.createElement("option"); opt.value=c.id_cliente; opt.textContent=`${c.nome_completo} (ID ${c.id_cliente})`; select.appendChild(opt);
    }
  } catch(e) { avisar("Não foi possível carregar os clientes: "+e.message,"error"); }
}
function formatar(valor) {
  if (valor === null || valor === undefined || valor === "") return "—";
  return String(valor);
}
function renderizar() {
  thead.innerHTML=""; const trh=document.createElement("tr");
  for (const [,label] of colunas) { const th=document.createElement("th"); th.textContent=label; trh.appendChild(th); }
  const acoes=document.createElement("th"); acoes.textContent="Ações"; trh.appendChild(acoes); thead.appendChild(trh);
  tbody.innerHTML="";
  document.getElementById("recordCount").textContent=`${registros.length} registro(s)`;
  if (!registros.length) {
    const tr=document.createElement("tr"), td=document.createElement("td"); td.colSpan=colunas.length+1; td.className="empty-state"; td.textContent="Nenhum registro cadastrado."; tr.appendChild(td); tbody.appendChild(tr); return;
  }
  for (const item of registros) {
    const tr=document.createElement("tr");
    for (const [key] of colunas) { const td=document.createElement("td"); td.textContent=formatar(item[key]); tr.appendChild(td); }
    const td=document.createElement("td"); td.className="table-actions";
    const editar=document.createElement("button"); editar.className="action-button"; editar.type="button"; editar.textContent="Editar"; editar.addEventListener("click",()=>prepararEdicao(item));
    const excluir=document.createElement("button"); excluir.className="action-button delete"; excluir.type="button"; excluir.textContent="Excluir"; excluir.addEventListener("click",()=>excluirRegistro(item));
    td.append(editar,excluir); tr.appendChild(td); tbody.appendChild(tr);
  }
}
// async function carregar() {
//   try { registros=await requisicao(API); renderizar(); }
//   catch(e) { avisar(e.message,"error"); }
// }
// function prepararEdicao(item) {
//   editandoId=item["id_cliente"];
//   document.getElementById("formTitle").textContent=`Editar registro #${editandoId}`;
//   document.getElementById("saveButton").textContent="Salvar alterações";
//   document.getElementById("cancelEdit").hidden=false;
//   for (const campo of campos) {
//     const input=document.getElementById(campo);
//     if (!input) continue;
//     if (campo === "senha") { input.value=""; input.required=false; input.placeholder="Deixe em branco para manter a senha atual"; continue; }
//     input.value=item[campo] ?? "";
//   }
//   window.scrollTo({top:0,behavior:"smooth"});


async function carregar() {
  try {
    const resposta = await requisicao(API);

    if (!Array.isArray(resposta)) {
      throw new Error("A API não retornou uma lista de clientes.");
    }

    registros = resposta;
    renderizar();

    console.log("Clientes carregados:", registros);
  } catch (e) {
    console.error("Erro ao carregar clientes:", e);
    avisar("Não foi possível carregar os clientes: " + e.message, "error");
  }
}


// }
function resetarFormulario() {
  editandoId=null; form.reset();
  document.getElementById("formTitle").textContent="Novo registro";
  document.getElementById("saveButton").textContent="Salvar registro";
  document.getElementById("cancelEdit").hidden=true;
  const senhaInput=document.getElementById("senha"); if (senhaInput) {senhaInput.required=true;senhaInput.placeholder="Mínimo 8 caracteres";}
}
form.addEventListener("submit", async event => {
  event.preventDefault();
  const dados={};
  for (const campo of campos) {
    const input=document.getElementById(campo);
    if (campo==="senha" && editandoId && !input.value) continue;
    let valor=input.value;
    if (campo==="cpf") valor=valor.replace(/\D/g,"");
    if (campo==="placa") valor=valor.replace(/[^a-zA-Z0-9]/g,"").toUpperCase();
    if (input.type==="number") valor=Number(valor);
    if (campo==="id_cliente") valor=Number(valor);
    dados[campo]=valor;
  }
  try {
    const url=editandoId ? API+editandoId : API;
    const method=editandoId ? "PUT" : "POST";
    await requisicao(url,{method,body:JSON.stringify(dados)});
    avisar(editandoId ? "Registro atualizado com sucesso." : "Registro cadastrado com sucesso.","success");
    resetarFormulario(); await carregar();
  } catch(e) { avisar(e.message,"error"); }
});
document.getElementById("cancelEdit").addEventListener("click",resetarFormulario);
document.getElementById("refreshButton").addEventListener("click",carregar);
desenharFormulario();
carregar();
