from flask import (
    Flask,
    request,
    jsonify,
    redirect,
    send_from_directory,
    render_template_string,
)
import json
import os
from datetime import datetime
from fpdf import FPDF
from io import BytesIO
from flask import send_file

app = Flask(__name__)

DEFAULT_OFICIO = 112
DEFAULT_NUMEROS = {
    "laudo": 58,
    "informacao": 54,
    "informacao_int": 1,
    "relatorio": 0,
    "memorando": 2,
}

# Lista padrão de papiloscopistas
DEFAULT_PAPILOS = ["ALLAN", "ANDERSON", "BERTUOL", "CLAUDIONOR", "ELISA"]

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "numeros_gerados.json")
print("Diretório atual:", os.getcwd())
TOKEN_SECRETO = "MEUSEGREDO"  # Altere se necessário


def carregar_dados():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
    else:
        # Usa os valores padrão para ofício, papiloscopistas e registros
        data = {
            "oficio": DEFAULT_OFICIO,
            "papiloscopistas": DEFAULT_PAPILOS,
            "registros": [],
        }
    # Garante que a chave "papiloscopistas" exista mesmo se o JSON for antigo
    if "papiloscopistas" not in data:
        data["papiloscopistas"] = DEFAULT_PAPILOS

    # Migração de ID e garantia dos campos "observacao" e "invalido"
    max_id = 0
    for reg in data["registros"]:
        if "id" in reg and reg["id"] > max_id:
            max_id = reg["id"]
    for reg in data["registros"]:
        if "id" not in reg:
            max_id += 1
            reg["id"] = max_id
        if "observacao" not in reg:
            reg["observacao"] = ""
        if "invalido" not in reg:
            reg["invalido"] = False

    return data


def salvar_dados(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)


# Rota para servir arquivos da pasta 'imagens'
@app.route("/imagens/<path:filename>")
def serve_image(filename):
    return send_from_directory(os.path.join(BASE_DIR, "imagens"), filename)


@app.route("/")
def index():
    return render_template_string(
        """
    <html>
      <head>
        <title>SETOR DE REPRESENTAÇÃO FACIAL HUMANA</title>
        <style>
          html, body {
            margin: 0;
            padding: 0;
            font-family: Arial, sans-serif;
            text-align: center;
          }
          /* Cabeçalho para os logos e título */
          header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 10px 20px;
            background-color: #fff;
          }
          header .logo-left {
            height: 90px;
            margin-left: 50px;
            margin-right: 10px;
          }
          header .logo-right {
            height: 90px;
            margin-right: 50px;
            margin-left: 10px;
          }
          header h1 {
            flex: 1;
            margin: 0;
          }
          /* Container principal */
          .container {
            width: 95%;
            margin: 0 auto;
            padding: 0;
            margin-top: 10px;
          }
          .box {
            border: 1px solid black;
            padding: 8px;
            margin: 4px;
            border-radius: 5px;
          }
          .usuario-box { background-color: #f4f4f4; }
          .botao-box { background-color: #e0e0e0; }
          .tabela-box { background-color: #dcdcdc; }
          table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 5px;
          }
          th, td {
            border: 1px solid black;
            padding: 6px;
            text-align: center;
          }

          table th {
            background-color: #bbb;
          }

          /* Data (coluna 1) */
          th:nth-child(1), td:nth-child(1) { width: 10%; }

          /* Ofício (coluna 2) */
          th:nth-child(2), td:nth-child(2) { width: 10%; }

          /* Laudo (coluna 3) */
          th:nth-child(3), td:nth-child(3) { width: 10%; }

          /* Informação (coluna 4) */
          th:nth-child(4), td:nth-child(4) { width: 10%; }

          /* Informação Int. (coluna 5) */
          th:nth-child(5), td:nth-child(5) { width: 10%; }

          /* Relatório (coluna 6) */
          th:nth-child(6), td:nth-child(6) { width: 10%; }

          /* Memorando (coluna 7) */
          th:nth-child(7), td:nth-child(7) { width: 10%; }

          /* Papiloscopista (coluna 8) */
          th:nth-child(8), td:nth-child(8) { width: 15%; }

          /* Inválido (coluna 9) */
          th:nth-child(9), td:nth-child(9) { width: 5%; }

          /* Observação (coluna 10) */
          th:nth-child(10), td:nth-child(10) { width: 10%; }


          .elisa, .allan, .claudionor, .bertuol, .anderson {
            background-color: white !important;
            color: black !important;
          }
          .invalido { background-color: #aaa !important; }
          .pagination-controls {
            margin: 2px 0;
          }

          .pagination-controls button {
            background-color: #00abbd;
            color: white;
            border: none;
            padding: 5px 15px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 12px;
            margin: 4px;
            transition: background-color 0.3s;
          }

          .pagination-controls button:hover {
            background-color: #0056b3;
          }

          .pagination-controls button.pagina-ativa {
            background-color: #014e59; /* cor para a página ativa */
            color: white;
            font-weight: bold;
            border: none;
            padding: 5px 15px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 12px;
            margin: 4px;
            transition: background-color 0.3s;
          }

          footer {
            font-size: 11px;
            padding: 2px;
            text-align: center;
            background-color: #f4f4f4;
          }
          .totals {
            background-color: #bbb;
            font-weight: bold;
            font-size: 16px;
            padding: 4px;
            text-align: center;
            /* Remova a propriedade 'color' aqui, se existir, para que não afete os textos */
          }

          .totals-number {
            color: #b40207;
          }

          .modal {
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            overflow: auto;
            background-color: rgba(0,0,0,0.4);
          }
          .modal-content {
            background-color: #fefefe;
            margin: 10% auto;
            padding: 20px;
            border: 1px solid #888;
            width: 50%;
            max-height: 70%;
            overflow-y: auto;
          }
          .botao-box button {
            background-color: #00abbd;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
            margin: 4px;
            transition: background-color 0.3s;
          }
          .botao-box button:hover {
            background-color: #0056b3;
          }
          .botao-box button.botao-oficio {
            background-color: #01656f;
          }
          .botao-box button.botao-oficio:hover {
            background-color: #014e59;
          }

          .botao-box button.botao-pdf {
            background-color: #298c4e;
          }
          .botao-box button.botao-pdf:hover {
            background-color: #216c3b;
          }

          .botao-box button.botao-graficos {
            background-color: #ed3237;
          }
          .botao-box button.botao-graficos:hover {
            background-color: #c52b2f;
          }

        </style>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
      </head>
      <body>
        <header>
          <img src="{{ url_for('serve_image', filename='pcpr.png') }}"
              alt="PCPR Logo"
              class="logo-left"
              onclick="contarCliquesSecreto()" />
              
          <h1>SETOR DE REPRESENTAÇÃO FACIAL HUMANA</h1>
          
          <img src="{{ url_for('serve_image', filename='iipr.png') }}"
              alt="IIPR Logo"
              class="logo-right">
        </header>

        <div class="container">
          <div class="box usuario-box">
            <label for="usuario">Examinador Facial:</label>
            <select id="usuario">
              <option value="ALLAN">Allan</option>
              <option value="ANDERSON">Anderson</option>
              <option value="BERTUOL">Bertuol</option>
              <option value="CLAUDIONOR">Claudionor</option>
              <option value="ELISA">Elisa</option>
            </select>
          </div>
          <div class="box botao-box">
            <button onclick="gerarNumero('laudo')">Laudo</button>
            <button onclick="gerarNumero('informacao')">Informação</button>
            <button onclick="gerarNumero('informacao_int')">Informação Int.</button>
            <button onclick="gerarNumero('relatorio')">Relatório</button>
            <button onclick="gerarNumero('memorando')">Memorando</button>
            <button class="botao-oficio" onclick="gerarOficio()">Gerar Ofício</button>
            <button class="botao-pdf" onclick="window.open('/exportar_pdf', '_blank')">Exportar PDF</button>
            <button class="botao-graficos" onclick="window.open('/graficos', '_blank')">Gerar Gráficos</button>
          </div>

          <p id="resultado"></p>
          <div class="box tabela-box">
            <h2 id="titulo-tabela"></h2>
            <table id="tabela">
              <tr>
                <th>Data</th>
                <th>Ofício</th>
                <th>Laudo</th>
                <th>Informação</th>
                <th>Informação Int.</th>
                <th>Relatório</th>
                <th>Memorando</th>
                <th>Papiloscopista</th>
                <th>Inválido</th>
                <th>Observação</th>
              </tr>
            </table>

            <div class="pagination-controls">
            </div>
          </div>
        </div>
        <footer>
          Desenvolvido com Python e Flask por pp_elisapinna - Versão 2.0 - 2025
        </footer>

        <!-- Modal de Observação -->
        <div id="obsModal" class="modal">
          <div class="modal-content">
            <h3>Observação</h3>
            <textarea id="obsTextarea" rows="10" style="width: 100%;"></textarea>
            <br>
            <button id="saveObsButton" onclick="salvarObservacao()">Salvar</button>
            <button onclick="fecharModal()">Fechar</button>
          </div>
        </div>

        <!-- Modal de Sucesso -->
        <div id="successModal" class="modal">
          <div class="modal-content">
            <h3>Sucesso</h3>
            <p id="successMessage"></p>
            <button onclick="fecharSuccessModal()">Fechar</button>
          </div>
        </div>

        <!-- Modal de Erro -->
        <div id="errorModal" class="modal">
          <div class="modal-content">
            <h3>Erro</h3>
            <p id="errorMessage"></p>
            <button onclick="fecharErrorModal()">Fechar</button>
          </div>
        </div>

        <div id="secretModal" class="modal">
          <div class="modal-content">
            <h3>Gerenciar Papiloscopistas</h3>
            <input type="text" id="novoPap" placeholder="Novo nome" />
            <button onclick="adicionarPap()">Adicionar</button>
            <br/><br/>
            <select id="papRemover"></select>
            <button onclick="removerPap()">Remover</button>
            <br/><br/>
            <button onclick="fecharSecretModal()">Fechar</button>
          </div>
        </div>


        <script>
          function mostrarSuccess(message) {
            document.getElementById("successMessage").innerText = message;
            document.getElementById("successModal").style.display = "block";
          }

          function fecharSuccessModal() {
            document.getElementById("successModal").style.display = "none";
          }

          function mostrarError(message) {
            document.getElementById("errorMessage").innerText = message;
            document.getElementById("errorModal").style.display = "block";
          }

          function fecharErrorModal() {
            document.getElementById("errorModal").style.display = "none";
          }

        </script>
      <script>

          // Valores default passados do Flask
          var defaultOficio = {{ defaultOficio }};
          var defaultNumeros = {{ defaultNumeros|tojson }};
          
          function tipoComAcento(tipo) {
            switch (tipo) {
              case "laudo":
                return "LAUDO";
              case "informacao":
                return "INFORMAÇÃO";
              case "informacao_int":
                return "INFORMAÇÃO INT."; // Aqui tratamos o novo tipo
              case "relatorio":
                return "RELATÓRIO";
              case "memorando":
                return "MEMORANDO";
              default:
                return tipo.toUpperCase();
            }
          }

          let groupedData = [];
          let currentPage = 1;
          let itemsPerPage = 14;
          let currentObsId = null;

          function gerarNumero(tipo) {
            let usuario = document.getElementById("usuario").value;
            fetch("/gerar_numero", {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({ tipo: tipo, usuario: usuario })
            })
            .then(response => response.json())
            .then(data => {
              var message = tipoComAcento(data.tipo) + " " + data.numero + " - Ofício: " + data.oficio;
              mostrarSuccess(message);
              document.getElementById("resultado").innerText = message;
              atualizarTabela();
            })

            .catch(error => {
              console.error("Erro:", error);
              mostrarError("Erro ao gerar documento: " + error);
            });
          }

          function gerarOficio() {
              let usuario = document.getElementById("usuario").value;
              fetch("/gerar_oficio", {
                  method: "POST",
                  headers: { "Content-Type": "application/json" },
                  body: JSON.stringify({ usuario: usuario })
              })
              .then(response => response.json())
              .then(data => {
                  var message = "OFÍCIO " + data.oficio + " - Usuário: " + data.usuario;
                  mostrarSuccess(message);
                  document.getElementById("resultado").innerText = message;
                  atualizarTabela();
              })
              .catch(error => {
                console.error("Erro:", error);
                mostrarError("Erro ao gerar ofício: " + error);
              });
          }

          function atualizarTabela() {
            fetch("/listar_registros")
              .then(response => response.json())
              .then(data => {
                const agora = new Date();
                const mes = agora.toLocaleString("pt-BR", { month: "long" });
                const ano = agora.getFullYear();
                document.getElementById("titulo-tabela").innerText = mes.toUpperCase() + " " + ano;
                // Agrupamento dos registros
                let registrosAgrupados = {};
                data.forEach(item => {
                  let chave;
                  if (item.tipo === "relatorio") {
                    chave = "relatorio_" + item.id;
                  } else {
                    chave = item.tipo + "_" + item.oficio;
                  }
                  registrosAgrupados[chave] = {
                    laudo:         item.tipo === "laudo"         ? item.numero : "",
                    informacao:    item.tipo === "informacao"    ? item.numero : "",
                    informacao_int: item.tipo === "informacao_int" ? item.numero : "",
                    relatorio:     item.tipo === "relatorio"     ? item.numero : "",
                    memorando:     item.tipo === "memorando"     ? item.numero : "",
                    usuario:       item.usuario,
                    data:          item.data,
                    id:            item.id,
                    observacao:    item.observacao,
                    invalido:      item.invalido,
                    oficio:        (item.tipo === "relatorio") ? "" : item.oficio,
                    tipo:          item.tipo
                  };
                });

                let arrayAgrupado = [];
                Object.keys(registrosAgrupados).forEach(key => {
                  arrayAgrupado.push(registrosAgrupados[key]);
                });

                groupedData = arrayAgrupado;
                // Calcula o número total de páginas e renderiza a última página
                let totalPages = Math.ceil(groupedData.length / itemsPerPage);
                renderPage(totalPages);
              });
          }


          function atualizarUsuarios() {
            fetch("/listar_papilos")
              .then(resp => resp.json())
              .then(lista => {
                let select = document.getElementById("usuario");
                select.innerHTML = ""; // limpa
                lista.forEach(pap => {
                  let opt = document.createElement("option");
                  opt.value = pap;
                  opt.innerText = pap[0] + pap.slice(1).toLowerCase(); // ex: "ALLAN" -> "Allan"
                  select.appendChild(opt);
                });
              })
              .catch(error => console.error("Erro ao carregar papiloscopistas:", error));
          }
          
          let contadorCliques = 0;
          function contarCliquesSecreto() {
            contadorCliques++;
            if (contadorCliques === 5) {
              carregarPapRemover();
              document.getElementById("secretModal").style.display = "block";
              contadorCliques = 0;
}

          }

          function fecharSecretModal() {
            document.getElementById("secretModal").style.display = "none";
            // reatualiza a lista
            atualizarUsuarios();
          }

          // Chama endpoint /adicionar_pap?nome=...
          function adicionarPap() {
            let nome = document.getElementById("novoPap").value.trim().toUpperCase();
            if (!nome) return;
            fetch("/adicionar_pap?nome=" + encodeURIComponent(nome))
              .then(resp => resp.json())
              .then(data => {
                mostrarSuccess("Papiloscopista adicionado: " + nome);
                fecharSecretModal();
              })
              .catch(err => mostrarError("Erro ao adicionar papiloscopista: " + err));
          }

          // Chama endpoint /remover_pap?nome=...
          function removerPap() {
            let select = document.getElementById("papRemover");
            let nome = select.value;
            fetch("/remover_pap?nome=" + encodeURIComponent(nome))
              .then(resp => resp.json())
              .then(data => {
                mostrarSuccess("Papiloscopista removido: " + nome);
                fecharSecretModal();
              })
              .catch(err => mostrarError("Erro ao remover papiloscopista: " + err));
          }

          // Carrega a lista no select "papRemover" quando abrir o modal
          function carregarPapRemover() {
            fetch("/listar_papilos")
              .then(resp => resp.json())
              .then(lista => {
                let sel = document.getElementById("papRemover");
                sel.innerHTML = "";
                lista.forEach(pap => {
                  let opt = document.createElement("option");
                  opt.value = pap;
                  opt.innerText = pap;
                  sel.appendChild(opt);
                });
              })
              .catch(error => console.error("Erro ao carregar papilos para remoção:", error));
          }
          // Coloque a declaração do TOKEN_SECRETO logo no início do script,
          // antes de qualquer função que o utilize.
          const TOKEN_SECRETO = "MEUSEGREDO";

          function renderPage(page) {
            let tabela = document.getElementById("tabela");
            tabela.innerHTML = `
              <tr>
                <th>Data</th>
                <th>Ofício</th>
                <th>Laudo</th>
                <th>Informação</th>
                <th>Informação Int.</th>
                <th>Relatório</th>
                <th>Memorando</th>
                <th>Papiloscopista</th>
                <th>Inválido</th>
                <th>Observação</th>
              </tr>
            `;
            
            let totalItems = groupedData.length;
            let totalPages = Math.ceil(totalItems / itemsPerPage);
            if (page < 1) page = 1;
            if (page > totalPages) page = totalPages;
            let startIndex = (page - 1) * itemsPerPage;
            let endIndex = startIndex + itemsPerPage;
            let pageData = groupedData.slice(startIndex, endIndex);
            
            pageData.forEach(item => {
              let rowClass = item.invalido ? "invalido" : item.usuario.toLowerCase();
              let invalidoHTML = item.invalido
                ? "Inválido"
                : `<a href="#" onclick="marcarInvalido(${item.id}); return false;">Inválido</a>`;


              let obsDisplay = (item.observacao && item.observacao.trim() !== "")
                ? "📝"
                : "Clique para anotar";
              let oficioDisplay = (item.tipo === "relatorio") ? "" : item.oficio;
                        
              let linha = `
                <tr class="${rowClass}">
                  <td>${item.data}</td>
                  <td>${oficioDisplay}</td>
                  <td>${item.laudo || ""}</td>
                  <td>${item.informacao || ""}</td>
                  <td>${item.informacao_int || ""}</td>
                  <td>${item.relatorio || ""}</td>
                  <td>${item.memorando || ""}</td>
                  <td>${item.usuario}</td>
                  <td>${invalidoHTML}</td>
                  <td onclick='abrirModal(${item.id}, ${JSON.stringify(item.observacao)})' style="cursor:pointer;">${obsDisplay}</td>
                </tr>
              `;
              tabela.innerHTML += linha;
            });
            
            // Resto do código (cálculo dos totais e paginação) permanece igual...
            let validRecords = groupedData.filter(item => !item.invalido);
            let uniqueDates = new Set(validRecords.map(item => item.data));
            let totalDias = uniqueDates.size;
            let totalOficios = validRecords.filter(item => item.tipo !== "relatorio").length;

            let totalLaudo = 0;
            let totalInformacao = 0;
            let totalInformacaoInt = 0;
            let totalRelatorio = 0;
            let totalMemorando = 0;
            
            validRecords.forEach(item => {
              if (item.laudo !== "") totalLaudo++;
              if (item.informacao !== "") totalInformacao++;
              if (item.informacao_int !== "") totalInformacaoInt++;
              if (item.relatorio !== "") totalRelatorio++;
              if (item.memorando !== "") totalMemorando++;
            });
            
            totalOficios += defaultOficio;
            totalLaudo += defaultNumeros.laudo;
            totalInformacao += defaultNumeros.informacao;
            totalInformacaoInt += defaultNumeros.informacao_int;
            totalRelatorio += defaultNumeros.relatorio;
            totalMemorando += defaultNumeros.memorando;
            
            tabela.innerHTML += `
              <tr class="totals">
                <td>Total de Dias: <span class="totals-number">${totalDias}</span></td>
                <td>Total de Ofícios: <span class="totals-number">${totalOficios}</span></td>
                <td>Total de Laudos: <span class="totals-number">${totalLaudo}</span></td>
                <td>Total de Informações: <span class="totals-number">${totalInformacao}</span></td>
                <td>Total de Informações Int.: <span class="totals-number">${totalInformacaoInt}</span></td>
                <td>Total de Relatórios: <span class="totals-number">${totalRelatorio}</span></td>
                <td>Total de Memorandos: <span class="totals-number">${totalMemorando}</span></td>
                <td></td>
                <td></td>
                <td></td>
              </tr>
            `;
            
            let paginationHTML = "";
            paginationHTML += `<button onclick="prevPage()">&laquo; Anterior</button> `;
            for (let i = 1; i <= totalPages; i++) {
              if (i === page) {
                paginationHTML += `<button class="pagina-ativa" onclick="renderPage(${i})">${i}</button> `;
              } else {
                paginationHTML += `<button onclick="renderPage(${i})">${i}</button> `;
              }
            }
            paginationHTML += `<button onclick="nextPage()">Próxima &raquo;</button>`;
            document.querySelector(".pagination-controls").innerHTML = paginationHTML;
            
            currentPage = page;
          }
            

          // Funções para Anterior / Próxima
          function prevPage() {
            if (currentPage > 1) {
              renderPage(currentPage - 1);
            }
          }
          function nextPage() {
            let totalItems = groupedData.length;
            let totalPages = Math.ceil(totalItems / itemsPerPage);
            if (currentPage < totalPages) {
              renderPage(currentPage + 1);
            }
          }

          function abrirModal(id, obs) {
            currentObsId = id;
            document.getElementById("obsTextarea").value = obs || "";
            if (obs && obs.trim() !== "") {
              document.getElementById("obsTextarea").readOnly = true;
              document.getElementById("saveObsButton").style.display = "none";
            } else {
              document.getElementById("obsTextarea").readOnly = false;
              document.getElementById("saveObsButton").style.display = "inline";
            }
            document.getElementById("obsModal").style.display = "block";
          }
          function fecharModal() {
            document.getElementById("obsModal").style.display = "none";
          }
          function salvarObservacao() {
            let novaObs = document.getElementById("obsTextarea").value;
            fetch("/update_observacao", {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({ id: currentObsId, observacao: novaObs })
            })
            .then(response => response.json())
            .then(data => {
              fecharModal();
              atualizarTabela();
              mostrarSuccess("Observação salva com sucesso!");
            })
            .catch(error => {
              console.error("Erro:", error);
              mostrarError("Erro ao salvar observação: " + error);
            });
          }

          function marcarInvalido(id) {
            if (!confirm('Deseja marcar este registro como inválido?')) {
              return;
            }
            fetch(`/marcar_invalido?id=${id}&token=${TOKEN_SECRETO}`)
              .then(response => response.json())
              .then(data => {
                // Após marcar inválido, atualize a tabela para a última página
                atualizarTabela();
              })
              .catch(error => {
                console.error("Erro:", error);
                mostrarError("Erro ao marcar como inválido: " + error);
              });
          }

          atualizarTabela();
          atualizarUsuarios();


         
          function renderCharts() {
              fetch("/dados_graficos")
              .then(response => response.json())
              .then(data => {
                  // Gráfico 1: Total de Laudos, Informações, Relatórios e Memorandos no mês
                  const ctx1 = document.getElementById('graficoTipos').getContext('2d');
                  new Chart(ctx1, {
                      type: 'bar',
                      data: {
                          labels: ['Laudo', 'Informação', 'Relatório', 'Memorando'],
                          datasets: [{
                              label: 'Total no Mês',
                              data: [
                                  data.documentos_por_tipo.laudo,
                                  data.documentos_por_tipo.informacao,
                                  data.documentos_por_tipo.informacao_int,
                                  data.documentos_por_tipo.relatorio,
                                  data.documentos_por_tipo.memorando
                              ],
                              backgroundColor: [
                                  'rgba(75, 192, 192, 0.6)',
                                  'rgba(54, 162, 235, 0.6)',
                                  'rgba(255, 206, 86, 0.6)',
                                  'rgba(153, 102, 255, 0.6)'
                              ],
                              borderColor: [
                                  'rgba(75, 192, 192, 1)',
                                  'rgba(54, 162, 235, 1)',
                                  'rgba(255, 206, 86, 1)',
                                  'rgba(153, 102, 255, 1)'
                              ],
                              borderWidth: 1
                          }]
                      },
                      options: {
                          scales: {
                              y: { beginAtZero: true }
                          }
                      }
                  });
                  
                  // Gráfico 2: Total de documentos gerados por cada papiloscopista
                  const ctx2 = document.getElementById('graficoUsuarios').getContext('2d');
                  const usuarios = data.documentos_por_usuario;
                  const labelsUsuarios = Object.keys(usuarios);
                  const dataUsuarios = Object.values(usuarios);
                  new Chart(ctx2, {
                      type: 'bar',
                      data: {
                          labels: labelsUsuarios,
                          datasets: [{
                              label: 'Documentos por Papiloscopista',
                              data: dataUsuarios,
                              backgroundColor: 'rgba(255, 99, 132, 0.6)',
                              borderColor: 'rgba(255, 99, 132, 1)',
                              borderWidth: 1
                          }]
                      },
                      options: {
                          scales: {
                              y: { beginAtZero: true }
                          }
                      }
                  });
              })
              .catch(error => console.error("Erro ao carregar dados para os gráficos:", error));
          }

          renderCharts();

        </script>
      </body>
    </html>
    """,
        defaultOficio=DEFAULT_OFICIO,
        defaultNumeros=DEFAULT_NUMEROS,
    )


@app.route("/gerar_numero", methods=["POST"])
def gerar_numero():
    data = carregar_dados()
    tipo = request.json.get("tipo")
    usuario = request.json.get("usuario")

    # Se não for um tipo válido, retorna erro
    allowed_types = ["laudo", "informacao", "informacao_int", "relatorio", "memorando"]
    if tipo not in allowed_types:
        return jsonify({"erro": "Tipo inválido"}), 400

    # Se for relatório, não gera ofício
    if tipo == "relatorio":
        numero_oficio = ""
    else:
        # Para todos os outros tipos, sempre faz data["oficio"] + 1
        numero_oficio = data["oficio"] + 1
        data["oficio"] += 1

    # Calcula o número do documento (laudo, info, etc.)
    registros_tipo = [reg for reg in data["registros"] if reg["tipo"] == tipo]
    if registros_tipo:
        max_num = max(reg["numero"] for reg in registros_tipo)
    else:
        max_num = DEFAULT_NUMEROS[tipo]
    next_num = max_num + 1

    data_registro = datetime.now().strftime("%d/%m/%Y")
    max_id = max((r["id"] for r in data["registros"]), default=0)
    new_id = max_id + 1

    novo_registro = {
        "id": new_id,
        "tipo": tipo,
        "numero": next_num,  # ex: 59 para laudo, etc.
        "oficio": numero_oficio,  # ex: 113
        "usuario": usuario,
        "data": data_registro,
        "observacao": "",
        "invalido": False,
    }

    data["registros"].append(novo_registro)
    salvar_dados(data)
    return jsonify(novo_registro)


@app.route("/gerar_oficio", methods=["POST"])
def gerar_oficio():
    data = carregar_dados()
    usuario = request.json.get("usuario")

    # Pega o valor atual do ofício e soma 1
    numero_oficio = data["oficio"] + 1
    data["oficio"] += 1

    data_registro = datetime.now().strftime("%d/%m/%Y")
    max_id = max((r["id"] for r in data["registros"]), default=0)
    new_id = max_id + 1

    novo_registro = {
        "id": new_id,
        "tipo": "oficio",
        "numero": numero_oficio,  # ou "numero": "", se quiser
        "oficio": numero_oficio,  # 113 no primeiro clique
        "usuario": usuario,
        "data": data_registro,
        "observacao": "",
        "invalido": False,
    }

    data["registros"].append(novo_registro)
    salvar_dados(data)
    return jsonify({"oficio": numero_oficio, "usuario": usuario})


@app.route("/listar_registros", methods=["GET"])
def listar_registros():
    return jsonify(carregar_dados()["registros"])


@app.route("/update_observacao", methods=["POST"])
def update_observacao():
    req = request.get_json()
    record_id = req.get("id")
    nova_obs = req.get("observacao")
    data = carregar_dados()

    for reg in data["registros"]:
        if reg["id"] == record_id:
            reg["observacao"] = nova_obs
            break

    salvar_dados(data)
    return jsonify({"status": "ok"})


@app.route("/marcar_invalido", methods=["GET"])
def marcar_invalido():
    token = request.args.get("token")
    if token != TOKEN_SECRETO:
        return jsonify({"error": "Acesso negado"}), 403

    record_id = request.args.get("id", type=int)
    data = carregar_dados()

    for reg in data["registros"]:
        if reg["id"] == record_id:
            reg["invalido"] = True
            break

    salvar_dados(data)
    return jsonify({"status": "ok"})


@app.route("/exportar_pdf", methods=["GET"])
def exportar_pdf():
    data = carregar_dados()["registros"]
    pdf = FPDF(orientation="L")  # Modo paisagem
    pdf.add_page()

    # Ajuste aqui conforme desejar
    header_height = 25

    # 1. Remova (ou comente) as linhas que desenham o retângulo cinza:
    # pdf.set_fill_color(160, 160, 160)
    # pdf.rect(0, 10, pdf.w, header_height, 'F')

    # 2. Ajuste o tamanho dos logos
    # Aumente ou diminua 'w' conforme necessidade
    pdf.image("imagens/pcpr.png", x=10, y=12, w=17)
    pdf.image("imagens/iipr.png", x=pdf.w - 60, y=12, w=40)

    # 3. Deixar o título em preto
    pdf.set_text_color(0, 0, 0)
    pdf.set_xy(0, 10)

    # 4. Fonte regular com tamanho reduzido
    pdf.set_font("Arial", "", 10)

    pdf.cell(
        pdf.w,
        header_height,
        "Registros do SETOR DE REPRESENTAÇÃO FACIAL HUMANA",
        0,
        1,
        "C",
    )
    pdf.ln(5)

    # Configuração das colunas com larguras ajustadas
    # Aqui, diminui a coluna "Observação" para 30 e deixo as demais com largura igual ou conforme desejado.
    headers = [
        "Data",
        "Ofício",
        "Laudo",
        "Informação",
        "Informação Int.",
        "Relatório",
        "Memorando",
        "Papiloscopista",
        "Inválido",
        "Observação",
    ]
    col_widths = [
        25,  # Data
        25,  # Ofício
        25,  # Laudo
        25,  # Informação
        25,  # Informação Int.
        25,  # Relatório
        25,  # Memorando
        35,  # Papiloscopista
        25,  # Inválido
        30,  # Observação (menor para liberar espaço)
    ]
    cell_height = 7

    # Cabeçalho da tabela
    pdf.set_fill_color(160, 160, 160)
    for header, width in zip(headers, col_widths):
        pdf.cell(width, cell_height, header, border=1, align="C", fill=True)
    pdf.ln()

    # Linhas de dados
    for i, reg in enumerate(data):
        obs_value = "OBS" if reg.get("observacao", "").strip() != "" else "***"
        row = [
            reg.get("data", ""),
            str(reg.get("oficio", "")),
            str(reg.get("numero", "")) if reg.get("tipo") == "laudo" else "",
            str(reg.get("numero", "")) if reg.get("tipo") == "informacao" else "",
            str(reg.get("numero", "")) if reg.get("tipo") == "informacao_int" else "",
            str(reg.get("numero", "")) if reg.get("tipo") == "relatorio" else "",
            str(reg.get("numero", "")) if reg.get("tipo") == "memorando" else "",
            reg.get("usuario", ""),
            "Inválido" if reg.get("invalido", False) else "",
            obs_value,
        ]

        # Fundo branco ou cinza clarinho para cada linha
        if i % 2 == 0:
            pdf.set_fill_color(255, 255, 255)
        else:
            pdf.set_fill_color(240, 240, 240)

        for cell_text, width in zip(row, col_widths):
            pdf.cell(width, cell_height, cell_text, border=1, align="C", fill=True)
        pdf.ln()

    # Linha de totais (somente números)
    valid_records = [reg for reg in data if not reg.get("invalido", False)]
    totalDias = len(set(r.get("data", "") for r in valid_records))
    totalOficios = len(valid_records)
    totalLaudo = sum(1 for r in valid_records if r.get("tipo") == "laudo")
    totalInformacao = sum(1 for r in valid_records if r.get("tipo") == "informacao")
    totalInformacaoInt = sum(
        1 for r in valid_records if r.get("tipo") == "informacao_int"
    )
    totalRelatorio = sum(1 for r in valid_records if r.get("tipo") == "relatorio")
    totalMemorando = sum(1 for r in valid_records if r.get("tipo") == "memorando")

    pdf.set_fill_color(200, 200, 200)
    pdf.cell(col_widths[0], cell_height, str(totalDias), border=1, align="C", fill=True)
    pdf.cell(
        col_widths[1], cell_height, str(totalOficios), border=1, align="C", fill=True
    )
    pdf.cell(
        col_widths[2], cell_height, str(totalLaudo), border=1, align="C", fill=True
    )
    pdf.cell(
        col_widths[3], cell_height, str(totalInformacao), border=1, align="C", fill=True
    )
    pdf.cell(
        col_widths[4],
        cell_height,
        str(totalInformacaoInt),
        border=1,
        align="C",
        fill=True,
    )  # Novo
    pdf.cell(
        col_widths[5], cell_height, str(totalRelatorio), border=1, align="C", fill=True
    )
    pdf.cell(
        col_widths[6], cell_height, str(totalMemorando), border=1, align="C", fill=True
    )
    pdf.cell(col_widths[7], cell_height, "", border=1, align="C", fill=True)
    pdf.cell(col_widths[8], cell_height, "", border=1, align="C", fill=True)
    pdf.cell(col_widths[9], cell_height, "", border=1, align="C", fill=True)
    pdf.ln()

    # Gera o PDF em memória e envia para download
    pdf_bytes = pdf.output(dest="S").encode("latin1")
    pdf_output = BytesIO(pdf_bytes)
    pdf_output.seek(0)
    return send_file(
        pdf_output,
        download_name="registros.pdf",
        as_attachment=True,
        mimetype="application/pdf",
    )


@app.route("/dados_graficos", methods=["GET"])
def dados_graficos():
    from datetime import datetime

    data = carregar_dados()["registros"]
    now = datetime.now()
    current_month = now.strftime("%m")
    current_year = now.strftime("%Y")

    # Contagem global por tipo (apenas registros do mês atual)
    tipos = {
        "laudo": 0,
        "informacao": 0,
        "informacao_int": 0,  # Adicionado
        "relatorio": 0,
        "memorando": 0,
    }

    for reg in data:
        if reg.get("invalido", False):
            continue
        reg_date = reg.get("data", "")
        try:
            day, month, year = reg_date.split("/")
        except:
            continue
        tipo = reg.get("tipo")
        if tipo in tipos and month == current_month and year == current_year:
            tipos[tipo] += 1

    # Contagem global por papiloscopista (todos os registros válidos)
    usuarios = {}
    for reg in data:
        if reg.get("invalido", False):
            continue
        usuario = reg.get("usuario", "Desconhecido")
        if usuario not in usuarios:
            usuarios[usuario] = 0
        usuarios[usuario] += 1

    # Contagem por papiloscopista e por tipo (apenas registros do mês atual)
    pap_names = ["ALLAN", "ANDERSON", "CLAUDIONOR", "BERTUOL", "ELISA"]
    documentos_por_papiloscopista = {}
    for pap in pap_names:
        documentos_por_papiloscopista[pap] = {
            "laudo": 0,
            "informacao": 0,
            "informacao_int": 0,
            "relatorio": 0,
            "memorando": 0,
        }

    for reg in data:
        if reg.get("invalido", False):
            continue
        reg_date = reg.get("data", "")
        try:
            day, month, year = reg_date.split("/")
        except:
            continue
        if month != current_month or year != current_year:
            continue
        pap = reg.get("usuario", "Desconhecido").upper()
        if pap in documentos_por_papiloscopista and reg.get("tipo") in [
            "laudo",
            "informacao",
            "informacao_int",
            "relatorio",
            "memorando",
        ]:
            documentos_por_papiloscopista[pap][reg.get("tipo")] += 1

    return jsonify(
        {
            "documentos_por_tipo": tipos,
            "documentos_por_usuario": usuarios,
            "documentos_por_papiloscopista": documentos_por_papiloscopista,
        }
    )


@app.route("/listar_papilos", methods=["GET"])
def listar_papilos():
    data = carregar_dados()
    return jsonify(data["papiloscopistas"])


@app.route("/adicionar_pap", methods=["GET"])
def adicionar_pap():
    nome = request.args.get("nome", "").strip().upper()
    data = carregar_dados()
    if nome and nome not in data["papiloscopistas"]:
        data["papiloscopistas"].append(nome)
        salvar_dados(data)
        return jsonify({"status": "ok", "nome": nome})
    return jsonify({"status": "erro", "msg": "Nome inválido ou já existe"})


@app.route("/remover_pap", methods=["GET"])
def remover_pap():
    nome = request.args.get("nome", "").strip().upper()
    data = carregar_dados()
    if nome in data["papiloscopistas"]:
        data["papiloscopistas"].remove(nome)
        salvar_dados(data)
        return jsonify({"status": "ok", "nome": nome})
    return jsonify({"status": "erro", "msg": "Nome não encontrado"})


@app.route("/graficos", methods=["GET"])
def graficos():
    return render_template_string(
        """
<html>
  <head>
    <title>Gráficos do App</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-datalabels@2"></script>
    <style>
      body {
        font-family: Arial, sans-serif; 
        margin: 0; 
        padding: 0;
      }
      header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 10px 20px;
        background-color: #fff;
      }
      header .logo-left { 
        height: 90px; 
        margin-left: 50px; 
        margin-right: 10px; 
      }
      header .logo-right { 
        height: 90px; 
        margin-right: 50px; 
        margin-left: 10px; 
      }
      header h1 { 
        flex: 1; 
        margin: 0; 
        text-align: center; 
      }
      .container { 
        padding: 20px; 
      }
      /* Gráfico principal */
      .global-chart-box {
        padding: 20px;
        margin: 0 auto 40px auto;
        width: 600px;
        text-align: center;
      }
      .global-chart-title {
        font-weight: bold;
        margin-bottom: 10px;
        font-size: 18px;
      }
      /* Legenda inferior do gráfico principal */
      .global-bottom-legend {
        text-align: left;
        margin-top: 10px;
      }
      .global-bottom-legend ul {
        list-style: none;
        padding: 0;
        margin: 0 auto;
        width: fit-content;
      }
      .global-bottom-legend li {
        margin-bottom: 5px;
      }
      .global-bottom-legend li span {
        display: inline-block;
        width: 15px;
        height: 15px;
        margin-right: 5px;
        vertical-align: middle;
      }
      /* Gráficos dos papiloscopistas */
      .pap-charts-container {
        display: flex;
        flex-wrap: nowrap;
        justify-content: center;
        gap: 20px;
      }
      .pap-chart-box {
        width: 350px;
        text-align: center;
        border: 1px solid #ddd;
        padding: 10px;
      }
      .pap-chart-title {
        font-weight: bold;
        margin-bottom: 10px;
      }
      /* Legenda inferior dos papiloscopistas */
      .pap-bottom-legend {
        text-align: left;
        margin-top: 10px;
      }
      .pap-bottom-legend ul {
        list-style: none;
        padding: 0;
        margin: 0 auto;
        width: fit-content;
      }
      .pap-bottom-legend li {
        margin-bottom: 5px;
      }
      .pap-bottom-legend li span {
        display: inline-block;
        width: 15px;
        height: 15px;
        margin-right: 5px;
        vertical-align: middle;
      }

    </style>
  </head>
  <body>
    <header>
      <img src="{{ url_for('serve_image', filename='pcpr.png') }}" alt="PCPR Logo" class="logo-left">
      <h1>SETOR DE REPRESENTAÇÃO FACIAL HUMANA</h1>
      <img src="{{ url_for('serve_image', filename='iipr.png') }}" alt="IIPR Logo" class="logo-right">
    </header>
    <div class="container">
      <!-- Gráfico Principal -->
      <div class="global-chart-box">
        <div class="global-chart-title">DOCUMENTOS</div>
        <canvas id="graficoTipos" width="550" height="550"></canvas>
        <!-- Legenda inferior do gráfico principal -->
        <div class="global-bottom-legend" id="globalBottomLegend"></div>
      </div>
      <!-- Gráficos dos Papiloscopistas -->
      <div class="pap-charts-container" id="papChartsContainer">
        <!-- Cada gráfico será inserido aqui -->
      </div>
    </div>
    <script>
      // Cores para o gráfico principal
      var globalChartColors = {
        "Laudo": 'rgba(0, 0, 0, 0.8)',
        "Informação": 'rgba(50, 50, 50, 0.8)',
        "Informação Int.": 'rgba(80, 80, 80, 0.8)',  // nova cor para Informação Int.
        "Relatório": 'rgba(100, 100, 100, 0.8)',
        "Memorando": 'rgba(150, 150, 150, 0.8)'
      };
      var docLabels = ["Laudo", "Informação", "Informação Int.", "Relatório", "Memorando"];


    // Papiloscopistas em ordem alfabética
    var papNames = ["ALLAN", "ANDERSON", "BERTUOL", "CLAUDIONOR", "ELISA"];

    // Cores base e variações para cada papiloscopista (agora com 5 cores)
    var papColors = {
      "ALLAN": {
        variants: [
          'rgba(99, 157, 99, 1)',
          'rgba(99, 157, 99, 0.9)',
          'rgba(99, 157, 99, 0.8)',
          'rgba(99, 157, 99, 0.7)',
          'rgba(99, 157, 99, 0.6)' // 5º item
        ]
      },
      "ANDERSON": {
        variants: [
          'rgba(128, 128, 254, 1)',
          'rgba(128, 128, 254, 0.9)',
          'rgba(128, 128, 254, 0.8)',
          'rgba(128, 128, 254, 0.7)',
          'rgba(128, 128, 254, 0.6)'
        ]
      },
      "BERTUOL": {
        variants: [
          'rgba(251, 207, 125, 1)',
          'rgba(251, 207, 125, 0.9)',
          'rgba(251, 207, 125, 0.8)',
          'rgba(251, 207, 125, 0.7)',
          'rgba(251, 207, 125, 0.6)'
        ]
      },
      "CLAUDIONOR": {
        variants: [
          'rgba(252, 126, 126, 1)',
          'rgba(252, 126, 126, 0.9)',
          'rgba(252, 126, 126, 0.8)',
          'rgba(252, 126, 126, 0.7)',
          'rgba(252, 126, 126, 0.6)'
        ]
      },
      "ELISA": {
        variants: [
          'rgba(184, 129, 207, 1)',
          'rgba(184, 129, 207, 0.9)',
          'rgba(184, 129, 207, 0.8)',
          'rgba(184, 129, 207, 0.7)',
          'rgba(184, 129, 207, 0.6)'
        ]
      }
    };


      // Dimensões dos gráficos dos papiloscopistas
      var papChartWidth = 350;
      var papChartHeight = 350;

      function renderCharts() {
        fetch("/dados_graficos")
          .then(response => response.json())
          .then(data => {
            // ========== GRÁFICO PRINCIPAL ==========
            var ctxGlobal = document.getElementById('graficoTipos').getContext('2d');
            new Chart(ctxGlobal, {
              type: 'pie',
              data: {
                labels: docLabels,
                datasets: [{
                  data: [
                    data.documentos_por_tipo.laudo,
                    data.documentos_por_tipo.informacao,
                    data.documentos_por_tipo.informacao_int,
                    data.documentos_por_tipo.relatorio,
                    data.documentos_por_tipo.memorando
                  ],
                  backgroundColor: [
                    globalChartColors["Laudo"],
                    globalChartColors["Informação"],
                    globalChartColors["Informação Int."],
                    globalChartColors["Relatório"],
                    globalChartColors["Memorando"]
                  ],
                  borderColor: [
                    globalChartColors["Laudo"],
                    globalChartColors["Informação"],
                    globalChartColors["Informação Int."],
                    globalChartColors["Relatório"],
                    globalChartColors["Memorando"]
                  ],

                  borderWidth: 1
                }]
              },
              options: {
                responsive: false,
                maintainAspectRatio: false,
                plugins: {
                  legend: {
                    display: false  // aqui desativamos a legenda superior
                  },
                  datalabels: {
                    color: '#000',
                    formatter: function(value) { return value; },
                    font: { weight: 'bold' }
                  }
                }
              },
              plugins: [ChartDataLabels]
            });

            // Legenda inferior do gráfico principal (lista vertical)
            var globalBottomLegendHTML = "<ul>";
            docLabels.forEach(function(label) {
              var count;
              switch(label) {
                case "Laudo":
                  count = data.documentos_por_tipo.laudo;
                  break;
                case "Informação":
                  count = data.documentos_por_tipo.informacao;
                  break;
                case "Informação Int.":
                  count = data.documentos_por_tipo.informacao_int;
                  break;
                case "Relatório":
                  count = data.documentos_por_tipo.relatorio;
                  break;
                case "Memorando":
                  count = data.documentos_por_tipo.memorando;
                  break;
              }
              globalBottomLegendHTML += "<li><span style='background-color:" + globalChartColors[label] + ";'></span> " + label + ": " + count + "</li>";
            });

            globalBottomLegendHTML += "</ul>";
            document.getElementById("globalBottomLegend").innerHTML = globalBottomLegendHTML;

            // ========== GRÁFICOS DOS PAPILOSCOPISTAS ==========
            var papContainer = document.getElementById("papChartsContainer");
            papContainer.innerHTML = "";
            papNames.forEach(function(pap) {
              // Estrutura HTML para cada papiloscopista (sem legenda superior)
              var box = document.createElement("div");
              box.className = "pap-chart-box";
              box.innerHTML = "<div class='pap-chart-title'>" + pap + "</div>" +
                              "<canvas id='graficoPap_" + pap + "' width='" + papChartWidth + "' height='" + papChartHeight + "'></canvas>" +
                              "<div class='pap-bottom-legend' id='papBottomLegend_" + pap + "'></div>";
              papContainer.appendChild(box);

              // Dados do papiloscopista
              var papDataObj = data.documentos_por_papiloscopista[pap];
              var papData = [
                papDataObj.laudo,
                papDataObj.informacao,
                papDataObj.informacao_int,
                papDataObj.relatorio,
                papDataObj.memorando
              ];

              // Cria o gráfico de pizza para cada papiloscopista
              var ctxPap = document.getElementById("graficoPap_" + pap).getContext('2d');
              new Chart(ctxPap, {
                type: 'pie',
                data: {
                  labels: docLabels,
                  datasets: [{
                    data: papData,
                    backgroundColor: papColors[pap].variants,
                    borderColor: papColors[pap].variants,
                    borderWidth: 1
                  }]
                  },
                  options: {
                    responsive: false,
                    maintainAspectRatio: false,
                    plugins: {
                      legend: {
                        display: false
                      },
                      datalabels: {
                        color: '#000',
                        formatter: function(value) { return value; },
                        font: { weight: 'bold' }
                      }
                    }
                  },
                  plugins: [ChartDataLabels]
                });

              // Legenda inferior do papiloscopista
              var papBottomLegendHTML = "<ul>";
              docLabels.forEach(function(label, i) {
                papBottomLegendHTML += "<li><span style='background-color:" + papColors[pap].variants[i] + ";'></span> " + label + ": " + papData[i] + "</li>";
              });
              papBottomLegendHTML += "</ul>";
              document.getElementById("papBottomLegend_" + pap).innerHTML = papBottomLegendHTML;
            });
          })
          .catch(error => console.error("Erro ao carregar dados para os gráficos:", error));
      }
      renderCharts();
    </script>
  </body>
</html>
        """
    )


if __name__ == "__main__":
    app.run(debug=True)
