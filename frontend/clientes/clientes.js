const API = "/api/clientes/";

const form = document.getElementById("recordForm");
const feedback = document.getElementById("feedback");
const tbody = document.getElementById("tableBody");
const thead = document.getElementById("tableHead");
const token = localStorage.getItem("token");

let registros = [];
let editandoId = null;
let consultandoCEP = false;
let consultaCEPId = 0;

const campos = [
  ["tipo_pessoa", "Tipo de pessoa", "select"],
  ["documento", "CPF", "text"],
  ["nome_completo", "Nome completo", "text"],
  ["email", "E-mail", "email"],
  ["telefone", "Telefone", "tel"],
  ["cep", "CEP", "text"],
  ["rua", "Rua", "text"],
  ["bairro", "Bairro", "text"],
  ["estado", "Estado (UF)", "text"],
  ["numero_casa", "Número da casa", "text"],
  ["numero_apartamento", "Número do apartamento (opcional)", "text"],
  ["complemento", "Complemento (opcional)", "text"],
  ["tipo_cliente", "Tipo de cliente", "select"]
];

const obrigatorios = [
  "tipo_pessoa",
  "documento",
  "nome_completo",
  "email",
  "telefone",
  "cep",
  "rua",
  "bairro",
  "estado",
  "numero_casa",
  "tipo_cliente"
];

const colunas = [
  ["id_cliente", "ID"],
  ["tipo_pessoa", "Pessoa"],
  ["documento", "CPF/CNPJ"],
  ["nome_completo", "Nome / Razão social"],
  ["email", "E-mail"],
  ["telefone", "Telefone"],
  ["cep", "CEP"],
  ["rua", "Rua"],
  ["bairro", "Bairro"],
  ["estado", "Estado"],
  ["numero_casa", "Número"],
  ["numero_apartamento", "Apartamento"],
  ["tipo_cliente", "Cobrança"]
];

const opcoes = {
  tipo_pessoa: [
    ["Fisica", "Pessoa Física"],
    ["Juridica", "Pessoa Jurídica"]
  ],
  tipo_cliente: [
    ["Horista", "Horista"],
    ["Mensalista", "Mensalista"]
  ]
};

if (!token) {
  window.location.replace("/");
}

const logout = document.getElementById("logoutButton");

logout.hidden = false;

logout.addEventListener("click", async () => {
  try {
    await fetch("/api/auth/logout", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`
      }
    });
  } catch (_) {}

  localStorage.removeItem("token");
  localStorage.removeItem("token_expira_em");
  window.location.replace("/");
});

document.querySelectorAll(".nav-links a").forEach((a) => {
  if (a.getAttribute("href") === "/pagina/clientes") {
    a.classList.add("active");
  }
});

function avisar(texto, tipo = "success") {
  feedback.textContent = texto;
  feedback.className = `feedback show ${tipo}`;
  window.scrollTo({ top: 0, behavior: "smooth" });
}

async function requisicao(url, options = {}) {
  const headers = {
    Authorization: `Bearer ${token}`,
    ...(options.headers || {})
  };

  if (options.body) {
    headers["Content-Type"] = "application/json";
  }

  const response = await fetch(url, {
    ...options,
    headers
  });

  if (response.status === 401) {
    localStorage.removeItem("token");
    localStorage.removeItem("token_expira_em");
    window.location.replace("/");
    throw new Error("Sessão expirada. Entre novamente.");
  }

  if (response.status === 204) return null;

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    let detail = data.detail || "Ocorreu um erro.";

    if (Array.isArray(detail)) {
      detail = detail.map((x) => x.msg).join("; ");
    }

    throw new Error(detail);
  }

  return data;
}

function somenteNumeros(valor) {
  return String(valor || "").replace(/\D/g, "");
}

function mascararCPF(valor) {
  return somenteNumeros(valor)
    .slice(0, 11)
    .replace(/(\d{3})(\d)/, "$1.$2")
    .replace(/(\d{3})(\d)/, "$1.$2")
    .replace(/(\d{3})(\d{1,2})$/, "$1-$2");
}

function mascararCNPJ(valor) {
  return somenteNumeros(valor)
    .slice(0, 14)
    .replace(/^(\d{2})(\d)/, "$1.$2")
    .replace(/^(\d{2})\.(\d{3})(\d)/, "$1.$2.$3")
    .replace(/\.(\d{3})(\d)/, ".$1/$2")
    .replace(/(\d{4})(\d)/, "$1-$2");
}

function mascararTelefone(valor) {
  const numeros = somenteNumeros(valor).slice(0, 11);

  if (numeros.length <= 10) {
    return numeros
      .replace(/^(\d{2})(\d)/, "($1) $2")
      .replace(/(\d{4})(\d)/, "$1-$2");
  }

  return numeros
    .replace(/^(\d{2})(\d)/, "($1) $2")
    .replace(/(\d{5})(\d)/, "$1-$2");
}

function mascararCEP(valor) {
  return somenteNumeros(valor)
    .slice(0, 8)
    .replace(/^(\d{5})(\d)/, "$1-$2");
}

function validarCPF(cpf) {
  cpf = somenteNumeros(cpf);

  if (cpf.length !== 11 || /^(\d)\1{10}$/.test(cpf)) {
    return false;
  }

  let soma = 0;

  for (let i = 0; i < 9; i++) {
    soma += Number(cpf[i]) * (10 - i);
  }

  let resto = (soma * 10) % 11;
  const digito1 = resto === 10 ? 0 : resto;

  if (digito1 !== Number(cpf[9])) {
    return false;
  }

  soma = 0;

  for (let i = 0; i < 10; i++) {
    soma += Number(cpf[i]) * (11 - i);
  }

  resto = (soma * 10) % 11;
  const digito2 = resto === 10 ? 0 : resto;

  return digito2 === Number(cpf[10]);
}

function validarCNPJ(cnpj) {
  cnpj = somenteNumeros(cnpj);

  if (cnpj.length !== 14 || /^(\d)\1{13}$/.test(cnpj)) {
    return false;
  }

  const calcularDigito = (base, pesos) => {
    const soma = base
      .split("")
      .reduce((total, numero, index) => {
        return total + Number(numero) * pesos[index];
      }, 0);

    const resto = soma % 11;
    return resto < 2 ? 0 : 11 - resto;
  };

  const primeiro = calcularDigito(
    cnpj.substring(0, 12),
    [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
  );

  const segundo = calcularDigito(
    cnpj.substring(0, 12) + primeiro,
    [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
  );

  return (
    primeiro === Number(cnpj[12]) &&
    segundo === Number(cnpj[13])
  );
}

function validarDocumento() {
  const tipo = document.getElementById("tipo_pessoa").value;
  const documento = document.getElementById("documento").value;

  if (tipo === "Fisica") {
    return validarCPF(documento);
  }

  if (tipo === "Juridica") {
    return validarCNPJ(documento);
  }

  return false;
}

function criarCampo(nome, rotulo, tipo) {
  const wrap = document.createElement("div");
  wrap.className = "field";

  const label = document.createElement("label");
  label.htmlFor = nome;
  label.textContent = rotulo;

  let input;

  if (tipo === "select") {
    input = document.createElement("select");

    input.innerHTML = '<option value="">Selecione...</option>';

    for (const [valor, texto] of opcoes[nome]) {
      const option = document.createElement("option");
      option.value = valor;
      option.textContent = texto;
      input.appendChild(option);
    }
  } else {
    input = document.createElement("input");
    input.type = tipo;

    if (nome === "documento") {
      input.inputMode = "numeric";
      input.maxLength = 14;
      input.placeholder = "Digite o CPF ou CNPJ";
    }

    if (nome === "telefone") {
      input.inputMode = "numeric";
      input.maxLength = 15;
      input.placeholder = "(99) 99999-9999";
    }

    if (nome === "cep") {
      input.inputMode = "numeric";
      input.maxLength = 9;
      input.placeholder = "00000-000";
    }

    if (nome === "estado") {
      input.maxLength = 2;
    }

    if (nome === "numero_apartamento") {
      input.placeholder = "Opcional";
    }

    if (nome === "complemento") {
      input.placeholder = "Opcional";
    }
  }

  input.id = nome;
  input.name = nome;

  if (!["numero_apartamento", "complemento"].includes(nome)) {
    input.required = true;
  }

  wrap.append(label, input);
  form.appendChild(wrap);

  return input;
}

function desenharFormulario() {
  form.innerHTML = "";

  campos.forEach(([nome, rotulo, tipo]) => {
    criarCampo(nome, rotulo, tipo);
  });

  configurarFormulario();
  bloquearCampos();
}

function bloquearCampos() {
  campos.forEach(([nome]) => {
    const input = document.getElementById(nome);

    if (input) {
      input.disabled = nome !== "tipo_pessoa";
    }
  });

  atualizarBotao();
}

function liberarCampo(nome) {
  const input = document.getElementById(nome);

  if (input) {
    input.disabled = false;
  }

  atualizarBotao();
}

function atualizarRotulos() {
  const tipo = document.getElementById("tipo_pessoa").value;
  const juridica = tipo === "Juridica";

  document.querySelector('label[for="documento"]').textContent =
    juridica ? "CNPJ" : "CPF";

  document.querySelector('label[for="nome_completo"]').textContent =
    juridica ? "Razão social" : "Nome completo";

  const documento = document.getElementById("documento");

  documento.maxLength = juridica ? 18 : 14;
  documento.placeholder = juridica
    ? "00.000.000/0000-00"
    : "000.000.000-00";
}

function atualizarBotao() {
  const botao = document.getElementById("saveButton");

  if (!botao) return;

  const incompleto = obrigatorios.some((nome) => {
    const input = document.getElementById(nome);

    return (
      !input ||
      input.disabled ||
      !input.value.trim()
    );
  });

  const email = document.getElementById("email");
  const documentoValido = validarDocumento();
  const cepValido =
    somenteNumeros(document.getElementById("cep").value).length === 8;

  botao.disabled =
    incompleto ||
    !documentoValido ||
    !email.validity.valid ||
    !cepValido ||
    consultandoCEP;
}

function limparCamposPosteriores(inicio) {
  const ordem = campos.map(([nome]) => nome);
  const indice = ordem.indexOf(inicio);

  ordem.slice(indice + 1).forEach((nome) => {
    const input = document.getElementById(nome);

    if (input) {
      input.value = "";
      input.disabled = true;
      input.readOnly = false;
    }
  });

  atualizarBotao();
}

function limparEndereco() {
  [
    "rua",
    "bairro",
    "estado",
    "numero_casa",
    "numero_apartamento",
    "complemento",
    "tipo_cliente"
  ].forEach((nome) => {
    const input = document.getElementById(nome);

    if (input) {
      input.value = "";
      input.disabled = true;
      input.readOnly = false;
    }
  });

  atualizarBotao();
}

function configurarFormulario() {
  const tipoPessoa = document.getElementById("tipo_pessoa");
  const documento = document.getElementById("documento");
  const nome = document.getElementById("nome_completo");
  const email = document.getElementById("email");
  const telefone = document.getElementById("telefone");
  const cep = document.getElementById("cep");

  tipoPessoa.addEventListener("change", () => {
    limparCamposPosteriores("documento");
    atualizarRotulos();

    documento.disabled = !tipoPessoa.value;

    atualizarBotao();
  });

  documento.addEventListener("input", () => {
    documento.value = tipoPessoa.value === "Juridica"
      ? mascararCNPJ(documento.value)
      : mascararCPF(documento.value);

    limparCamposPosteriores("nome_completo");
  });

  documento.addEventListener("blur", () => {
    if (!documento.value) return;

    if (!validarDocumento()) {
      avisar(
        `${tipoPessoa.value === "Juridica" ? "CNPJ" : "CPF"} inválido.`,
        "error"
      );
      return;
    }

    liberarCampo("nome_completo");
  });

  nome.addEventListener("input", () => {
    const valido = nome.value.trim().length >= 2;

    email.disabled = !valido;

    if (!valido) {
      limparCamposPosteriores("email");
    }

    atualizarBotao();
  });

  email.addEventListener("input", () => {
    telefone.disabled = !email.validity.valid || !email.value.trim();

    if (telefone.disabled) {
      limparCamposPosteriores("telefone");
    }

    atualizarBotao();
  });

  telefone.addEventListener("input", () => {
    telefone.value = mascararTelefone(telefone.value);

    const valido = somenteNumeros(telefone.value).length >= 10;

    cep.disabled = !valido;

    if (!valido) {
      limparCamposPosteriores("cep");
      consultaCEPId++;
      consultandoCEP = false;
    }

    atualizarBotao();
  });

  cep.addEventListener("input", () => {
    consultaCEPId++;
    consultandoCEP = false;

    cep.value = mascararCEP(cep.value);

    limparEndereco();
    atualizarBotao();
  });

  cep.addEventListener("blur", consultarCEP);

  document.getElementById("numero_casa")
    .addEventListener("input", atualizarBotao);

  document.getElementById("tipo_cliente")
    .addEventListener("change", atualizarBotao);
}

async function consultarCEP() {
  const cep = document.getElementById("cep");
  const numeros = somenteNumeros(cep.value);

  if (numeros.length !== 8) {
    return;
  }

  const identificador = ++consultaCEPId;

  consultandoCEP = true;
  atualizarBotao();

  try {
    const response = await fetch(
      `https://viacep.com.br/ws/${numeros}/json/`
    );

    if (!response.ok) {
      throw new Error("Não foi possível consultar o CEP.");
    }

    const dados = await response.json();

    if (identificador !== consultaCEPId) return;

    if (dados.erro) {
      throw new Error("CEP não encontrado.");
    }

    const endereco = {
      rua: dados.logradouro || "",
      bairro: dados.bairro || "",
      estado: dados.uf || ""
    };

    for (const [nome, valor] of Object.entries(endereco)) {
      const input = document.getElementById(nome);

      input.value = valor;
      input.disabled = false;
      input.readOnly = false;
    }

    liberarCampo("numero_casa");
    liberarCampo("numero_apartamento");
    liberarCampo("complemento");
    liberarCampo("tipo_cliente");

    avisar("Endereço localizado. Confira os dados e complete o endereço.", "success");

  } catch (erro) {
    if (identificador !== consultaCEPId) return;

    limparEndereco();

    ["rua", "bairro", "estado"].forEach((nome) => {
      document.getElementById(nome).disabled = false;
    });

    liberarCampo("numero_casa");
    liberarCampo("numero_apartamento");
    liberarCampo("complemento");
    liberarCampo("tipo_cliente");

    avisar(
      `${erro.message} Você pode preencher o endereço manualmente.`,
      "info"
    );

  } finally {
    if (identificador === consultaCEPId) {
      consultandoCEP = false;
      atualizarBotao();
    }
  }
}

function formatar(valor) {
  if (valor === null || valor === undefined || valor === "") {
    return "—";
  }

  return String(valor);
}

function renderizar() {
  thead.innerHTML = "";

  const trh = document.createElement("tr");

  for (const [, label] of colunas) {
    const th = document.createElement("th");
    th.textContent = label;
    trh.appendChild(th);
  }

  const acoes = document.createElement("th");
  acoes.textContent = "Ações";
  trh.appendChild(acoes);

  thead.appendChild(trh);
  tbody.innerHTML = "";

  document.getElementById("recordCount").textContent =
    `${registros.length} registro(s)`;

  if (!registros.length) {
    const tr = document.createElement("tr");
    const td = document.createElement("td");

    td.colSpan = colunas.length + 1;
    td.className = "empty-state";
    td.textContent = "Nenhum registro cadastrado.";

    tr.appendChild(td);
    tbody.appendChild(tr);
    return;
  }

  for (const item of registros) {
    const tr = document.createElement("tr");

    for (const [key] of colunas) {
      const td = document.createElement("td");
      td.textContent = formatar(item[key]);
      tr.appendChild(td);
    }

    const td = document.createElement("td");
    td.className = "table-actions";

    const editar = document.createElement("button");
    editar.className = "action-button";
    editar.type = "button";
    editar.textContent = "Editar";
    editar.addEventListener("click", () => prepararEdicao(item));

    const excluir = document.createElement("button");
    excluir.className = "action-button delete";
    excluir.type = "button";
    excluir.textContent = "Excluir";
    excluir.addEventListener("click", () => excluirRegistro(item));

    td.append(editar, excluir);
    tr.appendChild(td);
    tbody.appendChild(tr);
  }
}

async function carregar() {
  try {
    const resposta = await requisicao(API);

    if (!Array.isArray(resposta)) {
      throw new Error("A API não retornou uma lista de clientes.");
    }

    registros = resposta;
    renderizar();

  } catch (e) {
    console.error(e);
    avisar("Não foi possível carregar os clientes: " + e.message, "error");
  }
}

function prepararEdicao(item) {
  editandoId = item.id_cliente;

  campos.forEach(([nome]) => {
    const input = document.getElementById(nome);

    input.disabled = false;
    input.readOnly = false;
  });

  document.getElementById("tipo_pessoa").value =
    item.tipo_pessoa || "Fisica";

  atualizarRotulos();

  const documento = document.getElementById("documento");

  documento.value = item.tipo_pessoa === "Juridica"
    ? mascararCNPJ(item.documento || "")
    : mascararCPF(item.documento || "");

  const valores = {
    nome_completo: item.nome_completo,
    email: item.email,
    telefone: mascararTelefone(item.telefone),
    cep: mascararCEP(item.cep),
    rua: item.rua,
    bairro: item.bairro,
    estado: item.estado,
    numero_casa: item.numero_casa,
    numero_apartamento: item.numero_apartamento,
    complemento: item.complemento,
    tipo_cliente: item.tipo_cliente
  };

  Object.entries(valores).forEach(([nome, valor]) => {
    document.getElementById(nome).value = valor || "";
  });

  document.getElementById("formTitle").textContent = "Editar cliente";
  document.getElementById("saveButton").textContent = "Salvar alterações";
  document.getElementById("cancelEdit").hidden = false;

  atualizarBotao();

  window.scrollTo({ top: 0, behavior: "smooth" });
}

async function excluirRegistro(item) {
  if (!confirm(`Deseja excluir o cliente ${item.nome_completo}?`)) {
    return;
  }

  try {
    await requisicao(API + item.id_cliente, {
      method: "DELETE"
    });

    avisar("Cliente excluído com sucesso.");
    await carregar();

  } catch (e) {
    avisar(e.message, "error");
  }
}

function resetarFormulario() {
  editandoId = null;
  consultaCEPId++;
  consultandoCEP = false;

  form.reset();

  document.getElementById("formTitle").textContent = "Novo registro";
  document.getElementById("saveButton").textContent = "Salvar registro";
  document.getElementById("cancelEdit").hidden = true;

  desenharFormulario();
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  if (consultandoCEP) {
    avisar("Aguarde a consulta do CEP terminar.", "error");
    return;
  }

  if (!validarDocumento()) {
    avisar("Informe um CPF ou CNPJ válido.", "error");
    return;
  }

  if (!form.reportValidity()) {
    return;
  }

  const dados = {};

  campos.forEach(([nome]) => {
    const input = document.getElementById(nome);
    let valor = input.value.trim();

    if (["documento", "telefone", "cep"].includes(nome)) {
      valor = somenteNumeros(valor);
    }

    dados[nome] = valor || null;
  });

  try {
    const url = editandoId ? API + editandoId : API;
    const method = editandoId ? "PUT" : "POST";

    await requisicao(url, {
      method,
      body: JSON.stringify(dados)
    });

    avisar(
      editandoId
        ? "Cliente atualizado com sucesso."
        : "Cliente cadastrado com sucesso."
    );

    resetarFormulario();
    await carregar();

  } catch (e) {
    avisar(e.message, "error");
  }
});

document.getElementById("cancelEdit")
  .addEventListener("click", resetarFormulario);

document.getElementById("refreshButton")
  .addEventListener("click", carregar);

desenharFormulario();
carregar();