/*******************************************************************************
 * CONFIGURAÇÃO
 *******************************************************************************/
const JIRA_PROJECT_KEY = "SCRUMRAFA";
const SHEET_NAME = "Backlog";
const JIRA_ISSUE_TYPE_TASK = "Task";
const JIRA_ISSUE_TYPE_EPIC = "Epic";

const SCRIPT_PROPERTIES = PropertiesService.getScriptProperties();
const JIRA_URL = SCRIPT_PROPERTIES.getProperty("JIRA_URL");
const JIRA_EMAIL = SCRIPT_PROPERTIES.getProperty("JIRA_EMAIL");
const JIRA_API_TOKEN = SCRIPT_PROPERTIES.getProperty("JIRA_API_TOKEN");

/*******************************************************************************
 * CLIENTE DO JIRA
 *******************************************************************************/
class JiraClient {
  constructor(baseUrl, email, apiToken, projectKey) {
    if (!baseUrl || !email || !apiToken) throw new Error("Credenciais Jira não configuradas!");
    this.baseUrl = `https://${baseUrl.replace(/^https?:\/\//, '')}/rest/api/3`;
    this.projectKey = projectKey;
    this.headers = {
      "Authorization": "Basic " + Utilities.base64Encode(email + ":" + apiToken),
      "Accept": "application/json",
      "Content-Type": "application/json"
    };
    this.teamManaged = null; // Será detectado
  }

  execute(endpoint, options) {
    options.muteHttpExceptions = true;
    const resp = UrlFetchApp.fetch(this.baseUrl + endpoint, options);
    const code = resp.getResponseCode();
    const body = resp.getContentText();
    if (code >= 300) {
      Logger.log(`Jira Error ${code}: ${body}`);
      let msg = `Erro Jira [${code}]`;
      try { msg = JSON.parse(body).errorMessages?.join(",") || msg } catch(e) {}
      throw new Error(msg);
    }
    return body ? JSON.parse(body) : null;
  }

  async detectProjectType() {
    if (this.teamManaged !== null) return this.teamManaged;
    const proj = this.execute(`/project/${this.projectKey}`, { method: "get", headers: this.headers });
    this.teamManaged = proj.simplified === true; // true = Team-managed
    return this.teamManaged;
  }

  findEpic(name) {
    const jql = `project = "${this.projectKey}" AND issuetype = Epic AND summary ~ "${name.replace(/"/g,'\\"')}"`;
    const resp = this.execute(`/search?jql=${encodeURIComponent(jql)}`, { method: "get", headers: this.headers });
    return resp.issues?.[0] || null;
  }

  createEpic(name) {
    const payload = { fields: { project: { key: this.projectKey }, summary: name, issuetype: { name: JIRA_ISSUE_TYPE_EPIC } } };
    Logger.log(`Criando Epic: ${name}`);
    return this.execute("/issue", { method: "post", headers: this.headers, payload: JSON.stringify(payload) });
  }

  createOrUpdateIssue(issueKey, data) {
    const payload = { fields: { project: { key: this.projectKey }, summary: data.title, issuetype: { name: JIRA_ISSUE_TYPE_TASK }, description: data.descriptionAdf } };
    if (data.priority) payload.fields.priority = { name: data.priority };
    if (data.epicKey && this.teamManaged) payload.fields.parent = { key: data.epicKey }; // Team-managed usa parent
    if (issueKey) return this.execute(`/issue/${issueKey}`, { method: "put", headers: this.headers, payload: JSON.stringify(payload) });
    return this.execute("/issue", { method: "post", headers: this.headers, payload: JSON.stringify(payload) });
  }
}

/*******************************************************************************
 * GERENCIADOR DA PLANILHA
 *******************************************************************************/
class SpreadsheetManager {
  constructor(sheetName) {
    this.sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(sheetName);
    if (!this.sheet) throw new Error(`Planilha "${sheetName}" não encontrada`);
    this.STATUS_COLUMN = 8;
    this.JIRA_KEY_COLUMN = 9;
  }

  readRows() {
    const lastRow = this.sheet.getLastRow();
    if (lastRow < 2) return [];
    return this.sheet.getRange(2, 1, lastRow - 1, 9).getValues().map((row, i) => ({
      rowNumber: i + 2,
      id: row[0],
      theme: row[1],
      epicName: row[2],
      priority: row[3],
      title: row[4],
      description: row[5],
      acceptanceCriteria: row[6],
      status: row[7],
      jiraIssueKey: row[8]
    }));
  }

  writeResults(results) {
    if (!results.length) return;
    const statusUpdates = results.map(r => [r.status]);
    const keyUpdates = results.map(r => [r.jiraIssueKey]);
    const firstRow = results[0].rowNumber;
    this.sheet.getRange(firstRow, this.STATUS_COLUMN, results.length, 1).setValues(statusUpdates);
    this.sheet.getRange(firstRow, this.JIRA_KEY_COLUMN, results.length, 1).setValues(keyUpdates);
  }
}

/*******************************************************************************
 * AUXILIAR: Formata ADF
 *******************************************************************************/
function createAdf(description, acceptanceCriteria) {
  return {
    type: "doc",
    version: 1,
    content: [
      { type: "paragraph", content: [{ type: "text", text: description || " " }] },
      { type: "heading", attrs: { level: 3 }, content: [{ type: "text", text: "Critérios de Aceite" }] },
      { type: "paragraph", content: [{ type: "text", text: acceptanceCriteria || "N/A" }] }
    ]
  };
}

/*******************************************************************************
 * FUNÇÃO PRINCIPAL
 *******************************************************************************/
function runSynchronization() {
  try {
    const jira = new JiraClient(JIRA_URL, JIRA_EMAIL, JIRA_API_TOKEN, JIRA_PROJECT_KEY);
    jira.detectProjectType();
    const sheetManager = new SpreadsheetManager(SHEET_NAME);
    const rows = sheetManager.readRows();
    const results = [];
    const epicCache = {};

    for (const row of rows) {
      try {
        if (!row.title?.trim()) { row.status="Ignorado: Título vazio"; results.push(row); continue; }

        let epicKey = null;
        if (row.epicName?.trim()) {
          if (epicCache[row.epicName]) epicKey = epicCache[row.epicName];
          else {
            const epic = jira.findEpic(row.epicName) || jira.createEpic(row.epicName);
            epicKey = epic.key;
            epicCache[row.epicName] = epicKey;
          }
        }

        const issueData = {
          title: row.title,
          descriptionAdf: createAdf(row.description, row.acceptanceCriteria),
          priority: row.priority,
          epicKey: epicKey
        };

        const resp = jira.createOrUpdateIssue(row.jiraIssueKey, issueData);
        row.jiraIssueKey = resp.key;
        row.status = "Sincronizado";

      } catch(e) {
        row.status = `Erro: ${e.message}`;
        Logger.log(`Linha ${row.rowNumber} falhou: ${e.message}`);
      }
      results.push(row);
    }

    sheetManager.writeResults(results);
    SpreadsheetApp.getUi().alert(`Sincronização concluída: ${results.length} linhas processadas.`);

  } catch(e) {
    Logger.log(`Erro fatal: ${e.message}\n${e.stack}`);
    SpreadsheetApp.getUi().alert(`Falha na Sincronização: ${e.message}`);
  }
}

/*******************************************************************************
 * MENU
 *******************************************************************************/
function onOpen() {
  SpreadsheetApp.getUi().createMenu('Sincronizar Jira')
    .addItem('Executar Sincronização', 'runSynchronization')
    .addToUi();
}

