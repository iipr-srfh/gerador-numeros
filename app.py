from flask import Flask, request, jsonify, redirect, send_from_directory
import json
import os
from datetime import datetime

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "numeros_gerados.json")
print("Diretório atual:", os.getcwd())
TOKEN_SECRETO = "MEUSEGREDO"  # Altere se necessário

def carregar_dados():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
    else:
        data = {"oficio": 1, "registros": []}

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

# Rota para servir arquivos da pasta 'imagem'
@app.route("/imagem/<path:filename>")
def serve_image(filename):
    return send_from_directory(os.path.join(BASE_DIR, "imagem"), filename)

@app.route("/")
def index():
    return """
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
            flex: 1; /* faz o h1 ocupar o espaço central */
            margin: 0;
          }

          /* Container principal */
          .container {
            width: 95%;
            margin: 0 auto;
            padding: 0;
            margin-top: 10px; /* espaço abaixo do header */
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
            padding: 4px;
            text-align: center;
          }

          /* Larguras fixas para as colunas */
          th:nth-child(1), td:nth-child(1) { width: 8%; }   /* Data */
          th:nth-child(2), td:nth-child(2) { width: 8%; }   /* Ofício */
          th:nth-child(3), td:nth-child(3) { width: 10%; }  /* Laudo */
          th:nth-child(4), td:nth-child(4) { width: 10%; }  /* Informação */
          th:nth-child(5), td:nth-child(5) { width: 10%; }  /* Relatório */
          th:nth-child(6), td:nth-child(6) { width: 10%; }  /* Memorando */
          th:nth-child(7), td:nth-child(7) { width: 10%; }  /* Papiloscopista */
          th:nth-child(8), td:nth-child(8) { width: 10%; }  /* Inválido */
          /* A coluna Observação ocupa o restante */

          /* Cores para cada usuário */
          .elisa { background-color: purple; color: white; }
          .allan { background-color: green; color: white; }
          .claudionor { background-color: red; color: white; }
          .bertuol { background-color: orange; color: black; }
          .anderson { background-color: darkblue; color: white; }

          /* Linha inválida */
          .invalido { background-color: #aaa !important; }

          /* Paginação */
          .pagination-controls {
            margin: 2px 0;
          }
          .pagination-controls button {
            background-color: #66B2FF;
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
            background-color: #3399FF;
          }

          footer {
            font-size: 11px;
            padding: 2px;
            text-align: center;
            background-color: #f4f4f4;
          }

          /* Totais (rodapé da tabela) */
          .totals {
            background-color: #ccc;
            font-weight: bold;
            font-size: 12px;
            padding: 4px;
            text-align: center;
          }

          /* Modal para Observação */
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
            background-color: #007BFF;
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
        </style>
      </head>
      <body>

        <!-- Cabeçalho com logos e título -->
        <header>
          <img src="/imagem/pcpr.png" alt="PCPR Logo" class="logo-left">
          <h1>SETOR DE REPRESENTAÇÃO FACIAL HUMANA</h1>
          <img src="/imagem/iipr.png" alt="IIPR Logo" class="logo-right">
        </header>

        <div class="container">
          <div class="box usuario-box">
            <label for="usuario">Examinador Facial:</label>
            <select id="usuario">
              <option value="ELISA">Elisa</option>
              <option value="ALLAN">Allan</option>
              <option value="CLAUDIONOR">Claudionor</option>
              <option value="BERTUOL">Bertuol</option>
              <option value="ANDERSON">Anderson</option>
            </select>
          </div>

          <div class="box botao-box">
            <button onclick="gerarNumero('laudo')">Laudo</button>
            <button onclick="gerarNumero('informacao')">Informação</button>
            <button onclick="gerarNumero('relatorio')">Relatório</button>
            <button onclick="gerarNumero('memorando')">Memorando</button>
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
                <th>Relatório</th>
                <th>Memorando</th>
                <th>Papiloscopista</th>
                <th>Inválido</th>
                <th>Observação</th>
              </tr>
            </table>
            <div class="pagination-controls">
              <button onclick="prevPage()">&laquo; Anterior</button>
              <span id="pagination-info"></span>
              <button onclick="nextPage()">Próxima &raquo;</button>
            </div>
          </div>
        </div>

        <footer>
          Desenvolvido com Python e Tkinter por pp_elisapinna - Versão 1.3 - 2025
        </footer>

        <!-- Modal para Observação -->
        <div id="obsModal" class="modal">
          <div class="modal-content">
            <h3>Observação</h3>
            <textarea id="obsTextarea" rows="10" style="width: 100%;"></textarea>
            <br>
            <button id="saveObsButton" onclick="salvarObservacao()">Salvar</button>
            <button onclick="fecharModal()">Fechar</button>
          </div>
        </div>

        <script>
          function tipoComAcento(tipo) {
            switch (tipo) {
              case "laudo":       return "LAUDO";
              case "informacao":  return "INFORMAÇÃO";
              case "relatorio":   return "RELATÓRIO";
              case "memorando":   return "MEMORANDO";
              default:            return tipo.toUpperCase();
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
              // Troca a vírgula por um traço: "INFORMAÇÃO 3 - Ofício: 3"
              document.getElementById("resultado").innerText =
                tipoComAcento(data.tipo) + " " + data.numero + " - Ofício: " + data.oficio;
              atualizarTabela();
            })
            .catch(error => console.error("Erro:", error));
          }

          function atualizarTabela() {
            fetch("/listar_registros")
            .then(response => response.json())
            .then(data => {
              const agora = new Date();
              const mes = agora.toLocaleString("pt-BR", { month: "long" });
              const ano = agora.getFullYear();
              document.getElementById("titulo-tabela").innerText = mes.toUpperCase() + " " + ano;

              let registrosAgrupados = {};
              data.forEach(item => {
                registrosAgrupados[item.oficio] = {
                  laudo:       item.tipo === "laudo"       ? item.numero : "",
                  informacao:  item.tipo === "informacao"  ? item.numero : "",
                  relatorio:   item.tipo === "relatorio"   ? item.numero : "",
                  memorando:   item.tipo === "memorando"   ? item.numero : "",
                  usuario:     item.usuario,
                  data:        item.data,
                  id:          item.id,
                  observacao:  item.observacao,
                  invalido:    item.invalido
                };
              });

              let arrayAgrupado = [];
              Object.keys(registrosAgrupados).forEach(oficio => {
                let obj = registrosAgrupados[oficio];
                obj["oficio"] = oficio;
                arrayAgrupado.push(obj);
              });

              groupedData = arrayAgrupado;
              renderPage(currentPage = Math.ceil(groupedData.length / itemsPerPage) || 1);
            });
          }

          function renderPage(page) {
            let tabela = document.getElementById("tabela");
            tabela.innerHTML = `
              <tr>
                <th>Data</th>
                <th>Ofício</th>
                <th>Laudo</th>
                <th>Informação</th>
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
                : `<a href="/marcar_invalido?id=${item.id}&token=${TOKEN_SECRETO}"
                     onclick="return confirm('Deseja marcar este registro como inválido?')">
                     Inválido</a>`;

              // Observação
              let obsDisplay = (item.observacao && item.observacao.trim() !== "")
                ? "📝"
                : "Clique para anotar";

              let linha = `
                <tr class="${rowClass}">
                  <td>${item.data}</td>
                  <td>${item.oficio}</td>
                  <td>${item.laudo || ""}</td>
                  <td>${item.informacao || ""}</td>
                  <td>${item.relatorio || ""}</td>
                  <td>${item.memorando || ""}</td>
                  <td>${item.usuario}</td>
                  <td>${invalidoHTML}</td>
                  <td onclick='abrirModal(${item.id}, ${JSON.stringify(item.observacao)})'
                      style="cursor:pointer;">${obsDisplay}</td>
                </tr>
              `;
              tabela.innerHTML += linha;
            });

            // Totais (apenas registros válidos)
            let validRecords = groupedData.filter(item => !item.invalido);
            let uniqueDates = new Set(validRecords.map(item => item.data));
            let totalDias = uniqueDates.size;
            let totalOficios = validRecords.length;
            let totalLaudo = 0;
            let totalInformacao = 0;
            let totalRelatorio = 0;
            let totalMemorando = 0;

            validRecords.forEach(item => {
              if (item.laudo !== "")       totalLaudo++;
              if (item.informacao !== "") totalInformacao++;
              if (item.relatorio !== "")  totalRelatorio++;
              if (item.memorando !== "")  totalMemorando++;
            });

            tabela.innerHTML += `
              <tr class="totals">
                <td>Total de Dias: ${totalDias}</td>
                <td>Total de Ofícios: ${totalOficios}</td>
                <td>Total de Laudos: ${totalLaudo}</td>
                <td>Total de Informações: ${totalInformacao}</td>
                <td>Total de Relatórios: ${totalRelatorio}</td>
                <td>Total de Memorandos: ${totalMemorando}</td>
                <td></td>
                <td></td>
                <td></td>
              </tr>
            `;

            document.getElementById("pagination-info").innerText =
              "Página " + page + " de " + totalPages;
            currentPage = page;
          }

          function prevPage() {
            if (currentPage > 1) renderPage(currentPage - 1);
          }

          function nextPage() {
            let totalItems = groupedData.length;
            let totalPages = Math.ceil(totalItems / itemsPerPage);
            if (currentPage < totalPages) renderPage(currentPage + 1);
          }

          // Modal de Observação
          function abrirModal(id, obs) {
            currentObsId = id;
            document.getElementById("obsTextarea").value = obs || "";
            // Se já houver anotação, deixa somente leitura
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
            })
            .catch(error => console.error("Erro:", error));
          }

          // Carrega a tabela ao abrir a página
          atualizarTabela();

          // Token secreto para uso na URL
          const TOKEN_SECRETO = "MEUSEGREDO";
        </script>
      </body>
    </html>
    """

@app.route("/gerar_numero", methods=["POST"])
def gerar_numero():
    data = carregar_dados()
    tipo = request.json.get("tipo")
    usuario = request.json.get("usuario")

    cores = {
        "ELISA": "elisa",
        "ALLAN": "allan",
        "CLAUDIONOR": "claudionor",
        "BERTUOL": "bertuol",
        "ANDERSON": "anderson"
    }

    if tipo not in ["laudo", "informacao", "relatorio", "memorando"]:
        return jsonify({"erro": "Tipo inválido"}), 400

    numero_doc = sum(1 for reg in data["registros"] if reg["tipo"] == tipo) + 1
    numero_oficio = data["oficio"]
    data["oficio"] += 1
    data_registro = datetime.now().strftime("%d/%m/%Y")

    max_id = max((r["id"] for r in data["registros"]), default=0)
    new_id = max_id + 1

    novo_registro = {
        "id": new_id,
        "tipo": tipo,
        "numero": numero_doc,
        "oficio": numero_oficio,
        "usuario": usuario,
        "cor": cores.get(usuario.upper(), "black"),
        "data": data_registro,
        "observacao": "",
        "invalido": False
    }

    data["registros"].append(novo_registro)
    salvar_dados(data)
    return jsonify(novo_registro)

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
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
