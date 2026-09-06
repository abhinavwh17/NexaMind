import { useEffect, useRef, useState } from "react";
import * as XLSX from "xlsx";
import jsPDF from "jspdf";
import autoTable from "jspdf-autotable";
import "./App.css";
import GeminiSetup from "./components/GeminiSetup";

const API_BASE_URL = import.meta.env.DEV
  ? "http://127.0.0.1:8000"
  : window.location.origin;


const SettingsIcon = () => (
  <svg
    className="ui-icon"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="1.9"
    strokeLinecap="round"
    strokeLinejoin="round"
    aria-hidden="true"
  >
    <circle cx="12" cy="12" r="3" />
    <path d="M19.4 15a1.7 1.7 0 0 0 .34 1.88l.06.06-2.86 2.86-.06-.06A1.7 1.7 0 0 0 15 19.4a1.7 1.7 0 0 0-1 .6 1.7 1.7 0 0 0-.4 1.1V21H9.6v-.1a1.7 1.7 0 0 0-.4-1.1 1.7 1.7 0 0 0-1-.6 1.7 1.7 0 0 0-1.88.34l-.06.06L3.4 16.74l.06-.06A1.7 1.7 0 0 0 3.8 14.8a1.7 1.7 0 0 0-.6-1 1.7 1.7 0 0 0-1.1-.4H2V9.4h.1a1.7 1.7 0 0 0 1.1-.4 1.7 1.7 0 0 0 .6-1 1.7 1.7 0 0 0-.34-1.88l-.06-.06L6.26 3.2l.06.06A1.7 1.7 0 0 0 8.2 3.6a1.7 1.7 0 0 0 1-.6 1.7 1.7 0 0 0 .4-1.1V2h4v.1a1.7 1.7 0 0 0 .4 1.1 1.7 1.7 0 0 0 1 .6 1.7 1.7 0 0 0 1.88-.34l.06-.06 2.86 2.86-.06.06A1.7 1.7 0 0 0 19.4 8.2a1.7 1.7 0 0 0 .6 1 1.7 1.7 0 0 0 1.1.4h.1v4h-.1a1.7 1.7 0 0 0-1.1.4 1.7 1.7 0 0 0-.6 1Z" />
  </svg>
);

const ExcelIcon = () => (
  <svg
    className="export-icon"
    viewBox="0 0 24 24"
    aria-hidden="true"
  >
    <rect x="3" y="3" width="18" height="18" rx="4" fill="currentColor" />
    <path d="M8 8.2h2.2l1.8 2.7 1.8-2.7H16l-2.8 3.9 3 4.2H14l-2-3-2 3H7.8l3-4.2L8 8.2Z" fill="white" />
  </svg>
);

const PdfIcon = () => (
  <svg
    className="export-icon"
    viewBox="0 0 24 24"
    aria-hidden="true"
  >
    <path d="M6 2.8h8.2L19 7.6V21H6V2.8Z" fill="currentColor" />
    <path d="M14 2.8v5h5" fill="none" stroke="white" strokeWidth="1.4" strokeLinejoin="round" />
    <path d="M8.2 15.8v-4.4h1.5c1 0 1.7.5 1.7 1.4 0 .9-.7 1.4-1.7 1.4H9.2v1.6h-1Zm1-2.4h.4c.5 0 .8-.2.8-.6s-.3-.6-.8-.6h-.4v1.2Zm3 2.4v-4.4h1.4c1.4 0 2.3.8 2.3 2.2s-.9 2.2-2.3 2.2h-1.4Zm1-.8h.4c.8 0 1.3-.5 1.3-1.4s-.5-1.4-1.3-1.4h-.4V15Zm3.4.8v-4.4h2.8v.8h-1.8v1h1.6v.8h-1.6v1.8h-1Z" fill="white" />
  </svg>
);

function App() {
  const fileInputRef = useRef(null);
  const [conversations, setConversations] = useState([]);
  const [conversationId, setConversationId] = useState(null);
  const [conversationTitle, setConversationTitle] = useState("New analysis");
  const [files, setFiles] = useState([]);
  const [datasetId, setDatasetId] = useState(null);
  const [answers, setAnswers] = useState([]);
  const [question, setQuestion] = useState("");
  const [geminiConfigured, setGeminiConfigured] = useState(null);
  const [showSettings, setShowSettings] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [asking, setAsking] = useState(false);
  const [loadingChat, setLoadingChat] = useState(true);
  const [error, setError] = useState("");

  const checkGeminiConfiguration = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/settings/gemini-status`);
      const data = await response.json();
      setGeminiConfigured(Boolean(data.configured));
    } catch (err) {
      console.error(err);
      setGeminiConfigured(false);
    }
  };

  const refreshConversations = async () => {
    const response = await fetch(`${API_BASE_URL}/conversations`);
    if (!response.ok) throw new Error("Failed to load chat history");
    const data = await response.json();
    setConversations(data.conversations || []);
    return data.conversations || [];
  };

  const applyConversation = (data) => {
    setConversationId(data.id);
    setConversationTitle(data.title || "New analysis");
    setDatasetId(data.dataset_id || null);
    setFiles((data.workbooks || []).map((workbook) => ({
      name: workbook.filename,
      workbookId: workbook.workbook_id,
      persisted: true,
    })));
    const restoredAnswers = (data.messages || [])
      .filter((message) => message.role === "assistant" && message.payload)
      .map((message) => message.payload);
    setAnswers(restoredAnswers);
    setQuestion("");
    setError("");
    localStorage.setItem("nexamind.activeConversationId", data.id);
  };

  const openConversation = async (id) => {
    setLoadingChat(true);
    try {
      const response = await fetch(`${API_BASE_URL}/conversations/${id}`);
      if (!response.ok) throw new Error("Failed to open conversation");
      applyConversation(await response.json());
    } catch (err) {
      setError(err.message);
    } finally {
      setLoadingChat(false);
    }
  };

  const newChat = () => {
    setConversationId(null);
    setConversationTitle("New analysis");
    setDatasetId(null);
    setFiles([]);
    setAnswers([]);
    setQuestion("");
    setError("");
    localStorage.removeItem("nexamind.activeConversationId");
  };

  const bootstrap = async () => {
    try {
      await checkGeminiConfiguration();
      const items = await refreshConversations();
      const remembered = localStorage.getItem("nexamind.activeConversationId");
      const target = items.find((item) => item.id === remembered) || items[0];
      if (target) await openConversation(target.id);
      else setLoadingChat(false);
    } catch (err) {
      console.error(err);
      setError("Could not restore NexaMind history.");
      setLoadingChat(false);
    }
  };

  useEffect(() => { bootstrap(); }, []);

  const handleFileSelect = async (event) => {
    const selectedFiles = Array.from(event.target.files || []);
    event.target.value = "";
    if (!selectedFiles.length) return;
    setUploading(true);
    setError("");
    try {
      const formData = new FormData();
      selectedFiles.forEach((file) => formData.append("files", file));
      if (conversationId) formData.append("conversation_id", conversationId);
      if (datasetId) formData.append("dataset_id", datasetId);
      formData.append("append", conversationId ? "true" : "false");
      const response = await fetch(`${API_BASE_URL}/files/upload-multiple`, { method: "POST", body: formData });
      const data = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(data.detail || "Failed to upload files");
      setConversationId(data.conversation_id);
      setDatasetId(data.dataset_id);
      setFiles((data.workbooks || []).map((workbook) => ({
        name: workbook.filename,
        workbookId: workbook.workbook_id,
        persisted: true,
      })));
      localStorage.setItem("nexamind.activeConversationId", data.conversation_id);
      await refreshConversations();
      const detail = await fetch(`${API_BASE_URL}/conversations/${data.conversation_id}`);
      if (detail.ok) {
        const chat = await detail.json();
        setConversationTitle(chat.title || "New analysis");
      }
    } catch (err) {
      console.error(err);
      setError(err.message || "Something went wrong while uploading your files.");
    } finally { setUploading(false); }
  };

  const removeFile = async (file) => {
    if (!conversationId || !file.workbookId) return;
    setError("");
    try {
      const response = await fetch(`${API_BASE_URL}/files/${conversationId}/${file.workbookId}`, { method: "DELETE" });
      const data = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(data.detail || "Failed to remove workbook");
      setFiles((data.workbooks || []).map((workbook) => ({ name: workbook.filename, workbookId: workbook.workbook_id, persisted: true })));
      await refreshConversations();
    } catch (err) { setError(err.message); }
  };

  const askNexaMind = async () => {
    if (!question.trim() || !datasetId) return;
    setAsking(true);
    setError("");
    try {
      const response = await fetch(`${API_BASE_URL}/ask`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ dataset_id: datasetId, conversation_id: conversationId, question: question.trim() }),
      });
      const data = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(data.detail || "Failed to get answer");
      setAnswers((current) => [...current, data]);
      setQuestion("");
      const items = await refreshConversations();
      const current = items.find((item) => item.id === conversationId);
      if (current) setConversationTitle(current.title);
    } catch (err) {
      console.error(err);
      setError(err.message || "Something went wrong while analysing your data.");
    } finally { setAsking(false); }
  };

  const deleteChat = async (event, id) => {
    event.stopPropagation();
    if (!window.confirm("Delete this chat and its locally stored workbooks?")) return;
    const response = await fetch(`${API_BASE_URL}/conversations/${id}`, { method: "DELETE" });
    if (!response.ok) return;
    if (id === conversationId) newChat();
    await refreshConversations();
  };

  const renameChat = async () => {
    if (!conversationId) return;
    const title = window.prompt("Rename chat", conversationTitle);
    if (!title?.trim()) return;
    const response = await fetch(`${API_BASE_URL}/conversations/${conversationId}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title: title.trim() }),
    });
    if (response.ok) {
      const data = await response.json();
      setConversationTitle(data.title);
      await refreshConversations();
    }
  };

  const handleQuestionKeyDown = (event) => {
    if (event.key === "Enter" && !event.shiftKey) { event.preventDefault(); askNexaMind(); }
  };

  const openFilePicker = () => fileInputRef.current?.click();

// --------------------------------------------------
// Format table values
// --------------------------------------------------

const formatResultValue = (value) => {
  if (value === null || value === undefined) {
    return "-";
  }

  if (typeof value === "number") {
    return value.toLocaleString(undefined, {
      maximumFractionDigits: 2,
    });
  }

  return String(value);
};


// --------------------------------------------------
// Export table to Excel
// --------------------------------------------------

const exportTableToExcel = (calculation) => {
  if (
    !Array.isArray(calculation.rows) ||
    calculation.rows.length === 0
  ) {
    return;
  }

  const worksheet = XLSX.utils.json_to_sheet(
    calculation.rows
  );

  const workbook = XLSX.utils.book_new();

  XLSX.utils.book_append_sheet(
    workbook,
    worksheet,
    "NexaMind Analysis"
  );

  XLSX.writeFile(
    workbook,
    `nexamind-${calculation.id}.xlsx`
  );
};


// --------------------------------------------------
// Export table to PDF
// --------------------------------------------------

const exportTableToPdf = (calculation) => {
  if (
    !Array.isArray(calculation.rows) ||
    calculation.rows.length === 0
  ) {
    return;
  }

  const document = new jsPDF({
    orientation: "landscape",
  });

  const columns = Object.keys(
    calculation.rows[0]
  );

  const body = calculation.rows.map(
    (row) =>
      columns.map(
        (column) =>
          formatResultValue(
            row[column]
          )
      )
  );

  document.text(
    "NexaMind Analysis",
    14,
    15
  );

  autoTable(document, {
    head: [columns],
    body,
    startY: 22,
    styles: {
      fontSize: 8,
    },
    headStyles: {
      fontStyle: "bold",
    },
  });

  document.save(
    `nexamind-${calculation.id}.pdf`
  );
};


// --------------------------------------------------
// Render calculation table
// --------------------------------------------------

const renderCalculationTable = (calculation) => {
  if (
    !Array.isArray(calculation.rows) ||
    calculation.rows.length === 0
  ) {
    return null;
  }

  const columns = Object.keys(
    calculation.rows[0]
  );

  return (
    <div
      className="result-table-container"
      key={`table-${calculation.id}`}
    >
      <div className="result-table-header">
        <div className="result-table-title-section">
          <div>
            Detailed breakdown
          </div>

          <div className="result-table-count">
            {calculation.rows.length}{" "}
            {calculation.rows.length === 1
              ? "row"
              : "rows"}
          </div>
        </div>

        <div className="result-export-actions">
          <button
            type="button"
            className="result-export-button"
            onClick={() =>
              exportTableToExcel(
                calculation
              )
            }
          >
            <ExcelIcon />
            <span>Export Excel</span>
          </button>

          <button
            type="button"
            className="result-export-button"
            onClick={() =>
              exportTableToPdf(
                calculation
              )
            }
          >
            <PdfIcon />
            <span>Export PDF</span>
          </button>
        </div>
      </div>

      <div className="result-table-scroll">
        <table className="result-table">
          <thead>
            <tr>
              {columns.map((column) => (
                <th key={column}>
                  {column}
                </th>
              ))}
            </tr>
          </thead>

          <tbody>
            {calculation.rows.map(
              (row, rowIndex) => (
                <tr
                  key={`${calculation.id}-${rowIndex}`}
                >
                  {columns.map((column) => (
                    <td key={column}>
                      {formatResultValue(
                        row[column]
                      )}
                    </td>
                  ))}
                </tr>
              )
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};


// --------------------------------------------------
// Render answer
// --------------------------------------------------

const renderAnswerResult = (answer) => {
  const calculations = Array.isArray(
    answer.calculations
  )
    ? answer.calculations
    : [];

  const tableCalculations =
    calculations.filter(
      (calculation) =>
        Array.isArray(calculation.rows) &&
        calculation.rows.length > 0 &&
        (
          calculation.operation ===
            "GROUP_BY_METRICS" ||
          calculation.rows.length > 1
        )
    );

  const hasAnswer =
    answer.answer &&
    answer.answer.trim().length > 0;

  if (
    !hasAnswer &&
    tableCalculations.length === 0
  ) {
    return (
      <div className="answer-message">
        NexaMind could not calculate this result.
      </div>
    );
  }

  return (
    <>
      {/* Inline / natural-language answer */}

      {hasAnswer && (
        <div className="answer-result">
          {answer.answer}
        </div>
      )}

      {/* Table result */}

      {tableCalculations.map(
        (calculation) =>
          renderCalculationTable(
            calculation
          )
      )}
    </>
  );
};




  if (geminiConfigured === null) {
    return <div className="app loading-screen">Loading NexaMind...</div>;
  }

  if (!geminiConfigured || showSettings) {
    return (
      <GeminiSetup
        apiBaseUrl={API_BASE_URL}
        isSettings={showSettings}
        onConnected={() => { setGeminiConfigured(true); setShowSettings(false); }}
        onCancel={geminiConfigured ? () => setShowSettings(false) : undefined}
      />
    );
  }

  return (
    <div className="chat-app">
      <aside className="chat-sidebar">
        <div className="sidebar-brand">
          <div className="brand-icon">N</div>
          <div>
            <strong>NexaMind</strong>
            <span>Financial Intelligence</span>
          </div>
        </div>

        <button className="new-chat-button" onClick={newChat}>
          <span className="new-chat-plus">＋</span>
          <span>New chat</span>
        </button>

        <div className="history-label">RECENT</div>

        <div className="history-list">
          {conversations.map((chat) => (
            <button
              key={chat.id}
              className={`history-item ${chat.id === conversationId ? "active" : ""}`}
              onClick={() => openConversation(chat.id)}
            >
              <span className="history-icon" aria-hidden="true">▤</span>
              <div className="history-copy">
                <strong>{chat.title}</strong>
                <span>
                  {chat.file_count} {chat.file_count === 1 ? "file" : "files"}
                </span>
              </div>
              <span
                className="history-delete"
                onClick={(event) => deleteChat(event, chat.id)}
                title="Delete chat"
              >
                ×
              </span>
            </button>
          ))}

          {conversations.length === 0 && (
            <div className="history-empty">
              Your chats will appear here.
            </div>
          )}
        </div>

        <button
          className="sidebar-settings"
          onClick={() => setShowSettings(true)}
        >
          <span className="settings-icon-wrap">
            <SettingsIcon />
          </span>
          <span>Settings</span>
          <span className="settings-chevron">›</span>
        </button>
      </aside>

      <section className="chat-main">
        <header className="chat-header">
          <div className="chat-title-block">
            <h1>{conversationTitle}</h1>
            <p>
              {files.length
                ? `${files.length} workbook${files.length === 1 ? "" : "s"} in this chat`
                : "Start a new financial analysis"}
            </p>
          </div>

          <div className="chat-header-actions">
            {conversationId && (
              <button className="rename-button" onClick={renameChat}>
                <span aria-hidden="true">✎</span>
                Rename
              </button>
            )}
          </div>
        </header>

        <div className="chat-scroll">
          {loadingChat ? (
            <div className="chat-empty">Restoring your workspace...</div>
          ) : (
            <>
              <div className="workspace-files">
                <div className="workspace-files-head">
                  <div className="workspace-heading">
                    <div className="workspace-heading-icon" aria-hidden="true">▰</div>
                    <div>
                      <strong>Files for this chat</strong>
                      <span>These workbooks stay attached to this conversation.</span>
                    </div>
                  </div>

                  <button
                    className="add-files-button"
                    onClick={openFilePicker}
                    disabled={uploading}
                  >
                    {uploading ? "Uploading..." : "＋ Add files"}
                  </button>
                </div>

                <input
                  ref={fileInputRef}
                  type="file"
                  multiple
                  accept=".xlsx,.xls"
                  onChange={handleFileSelect}
                  hidden
                />

                {files.length > 0 ? (
                  <div className="file-chips">
                    {files.map((file) => (
                      <div className="file-chip" key={file.workbookId || file.name}>
                        <span className="file-type-icon">XLS</span>
                        <span className="file-chip-name">{file.name}</span>
                        <button
                          className="file-chip-remove"
                          onClick={() => removeFile(file)}
                          title={`Remove ${file.name}`}
                        >
                          ×
                        </button>
                      </div>
                    ))}
                  </div>
                ) : (
                  <button className="empty-upload" onClick={openFilePicker}>
                    <span className="empty-upload-icon" aria-hidden="true">↑</span>
                    <span>Upload one or more Excel workbooks</span>
                  </button>
                )}
              </div>

              {answers.length === 0 && files.length === 0 && (
                <div className="chat-empty welcome-state">
                  <div className="empty-logo">N</div>
                  <h2>What would you like to analyse?</h2>
                  <p>
                    Upload financial workbooks to this chat, then ask NexaMind
                    questions about them.
                  </p>
                </div>
              )}

              <div className="message-list">
                {answers.map((answer, index) => (
                  <div
                    className="conversation-turn"
                    key={`${answer.question}-${index}`}
                  >
                    <div className="user-message">
                      <div className="message-avatar user">You</div>
                      <div className="user-message-bubble">{answer.question}</div>
                    </div>

                    <div className="assistant-message">
                      <div className="message-avatar ai">N</div>
                      <div className="assistant-body">
                        {renderAnswerResult(answer)}
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              {error && <div className="error-message">{error}</div>}
            </>
          )}
        </div>

        <div className="composer-wrap">
          <div className="composer">
            <button
              type="button"
              className="composer-attach"
              onClick={openFilePicker}
              disabled={uploading}
              title="Add workbooks"
              aria-label="Add workbooks"
            >
              ＋
            </button>

            <textarea
              value={question}
              onChange={(event) => setQuestion(event.target.value)}
              onKeyDown={handleQuestionKeyDown}
              placeholder={
                datasetId
                  ? "Ask about these workbooks..."
                  : "Upload files to start analysing..."
              }
              rows="2"
              disabled={!datasetId || asking}
            />

            <button
              type="button"
              className="composer-send"
              onClick={askNexaMind}
              disabled={asking || !question.trim() || !datasetId}
              aria-label="Send question"
              title="Send"
            >
              {asking ? "…" : "↑"}
            </button>
          </div>

          <div className="privacy-note">
            <span aria-hidden="true">◉</span>
            Workbook row data is analysed locally. NexaMind sends schema metadata
            and your question to the configured AI planner.
          </div>
        </div>
      </section>
    </div>
  );
}

export default App;
