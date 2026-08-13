import { useRef, useState } from "react";
import "./App.css";

const API_BASE_URL = "http://127.0.0.1:8000";

function App() {
  const fileInputRef = useRef(null);

  const [files, setFiles] = useState([]);
  const [datasetId, setDatasetId] = useState(null);

  const [question, setQuestion] = useState("");
  const [answers, setAnswers] = useState([]);

  const [uploading, setUploading] = useState(false);
  const [asking, setAsking] = useState(false);

  const [error, setError] = useState("");

  // --------------------------------------------------
  // File selection
  // --------------------------------------------------

  const handleFileSelect = async (event) => {
    const selectedFiles = Array.from(event.target.files);

    if (!selectedFiles.length) {
      return;
    }

    setError("");

    setFiles((currentFiles) => [
      ...currentFiles,
      ...selectedFiles,
    ]);

    event.target.value = "";

    // Upload the first selected file to backend
    // Multiple files can be added to the UI.
    // We can extend backend support for multiple files later.
    const file = selectedFiles[0];

    await uploadFile(file);
  };

  // --------------------------------------------------
  // Upload file
  // --------------------------------------------------

  const uploadFile = async (file) => {
    setUploading(true);
    setError("");

    try {
      const formData = new FormData();

      formData.append("file", file);

      const response = await fetch(
        `${API_BASE_URL}/files/upload`,
        {
          method: "POST",
          body: formData,
        }
      );

      if (!response.ok) {
        throw new Error("Failed to upload file");
      }

      const data = await response.json();

      console.log("Upload response:", data);

      if (data.dataset_id) {
        setDatasetId(data.dataset_id);
      } else {
        throw new Error(
          "Dataset ID was not returned by the server"
        );
      }
    } catch (err) {
      console.error(err);

      setError(
        "Something went wrong while uploading your file."
      );
    } finally {
      setUploading(false);
    }
  };

  // --------------------------------------------------
  // Remove file
  // --------------------------------------------------

  const removeFile = (indexToRemove) => {
    setFiles((currentFiles) =>
      currentFiles.filter(
        (_, index) => index !== indexToRemove
      )
    );

    // For now, clear analysis history when files change.
    setAnswers([]);
    setDatasetId(null);
  };

  // --------------------------------------------------
  // File picker
  // --------------------------------------------------

  const openFilePicker = () => {
    fileInputRef.current?.click();
  };

  // --------------------------------------------------
  // Ask NexaMind
  // --------------------------------------------------

  const askNexaMind = async () => {
    if (!question.trim()) {
      return;
    }

    if (!datasetId) {
      setError(
        "Please upload a financial file first."
      );

      return;
    }

    setAsking(true);
    setError("");

    try {
      const response = await fetch(
        `${API_BASE_URL}/ask`,
        {
          method: "POST",

          headers: {
            "Content-Type": "application/json",
          },

          body: JSON.stringify({
            dataset_id: datasetId,
            question: question.trim(),
          }),
        }
      );

      if (!response.ok) {
        throw new Error(
          "Failed to get answer"
        );
      }

      const data = await response.json();

      console.log("Ask response:", data);

      setAnswers((currentAnswers) => [
        ...currentAnswers,
        data,
      ]);

      setQuestion("");
    } catch (err) {
      console.error(err);

      setError(
        "Something went wrong while analysing your data."
      );
    } finally {
      setAsking(false);
    }
  };

  // --------------------------------------------------
  // Example question
  // --------------------------------------------------

  const askExample = (exampleQuestion) => {
    setQuestion(exampleQuestion);
  };

  // --------------------------------------------------
  // Enter key
  // --------------------------------------------------

  const handleQuestionKeyDown = (event) => {
    if (
      event.key === "Enter" &&
      !event.shiftKey
    ) {
      event.preventDefault();

      askNexaMind();
    }
  };

  // --------------------------------------------------
  // Render result
  // --------------------------------------------------

  const renderAnswerResult = (answer) => {
    if (
      answer.operation === "GROUP_BY" &&
      Array.isArray(answer.result)
    ) {
      return (
        <div className="grouped-result">
          {answer.result.map(
            (row, index) => (
              <div
                className="grouped-result-row"
                key={index}
              >
                <div className="grouped-result-name">
                  {row[answer.group_by]}
                </div>

                <div className="grouped-result-value">
                  {Number(
                    row[answer.column]
                  ).toLocaleString(
                    undefined,
                    {
                      minimumFractionDigits: 2,
                      maximumFractionDigits: 2,
                    }
                  )}
                </div>
              </div>
            )
          )}
        </div>
      );
    }

    if (
      answer.result !== undefined &&
      answer.result !== null
    ) {
      const numericResult =
        Number(answer.result);

      if (!Number.isNaN(numericResult)) {
        return (
          <div className="answer-result">
            {numericResult.toLocaleString(
              undefined,
              {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2,
              }
            )}
          </div>
        );
      }
    }

    return (
      <div className="answer-message">
        {answer.message ||
          "NexaMind could not calculate this result."}
      </div>
    );
  };

  // --------------------------------------------------
  // Render
  // --------------------------------------------------

  return (
    <div className="app">

      {/* Header */}

      <header className="header">

        <div className="brand">

          <div className="brand-icon">
            N
          </div>

          <div>
            <div className="brand-name">
              NexaMind
            </div>

            <div className="brand-tagline">
              Financial Intelligence
            </div>
          </div>

        </div>

        <div className="header-right">

          <span className="status-dot"></span>

          AI Copilot

        </div>

      </header>

      <main className="main">

        {/* Hero */}

        <section className="hero">

          <div className="eyebrow">
            FINANCIAL AI COPILOT
          </div>

          <h1>
            Understand your financial data
            <br />
            <span>
              with intelligence.
            </span>
          </h1>

          <p>
            Upload your financial documents,
            ask questions,
            <br />
            and get clear answers backed by
            your data.
          </p>

        </section>

        {/* Workspace */}

        <section className="workspace">

          {/* Upload Card */}

          <div className="card upload-card">

            <div className="card-header">

              <div>

                <h2>
                  Financial documents
                </h2>

                <p>
                  Upload one or more files
                  to get started.
                </p>

              </div>

              {files.length > 0 && (
                <span className="file-count">
                  {files.length}{" "}
                  {files.length === 1
                    ? "file"
                    : "files"}
                </span>
              )}

            </div>

            <div
              className="drop-zone"
              onClick={openFilePicker}
            >

              <div className="upload-circle">
                ↑
              </div>

              <h3>
                Drop your files here
              </h3>

              <p>
                or{" "}
                <span>
                  browse from your computer
                </span>
              </p>

              <div className="supported-files">
                XLSX &nbsp;•&nbsp; XLS &nbsp;•&nbsp; PDF
              </div>

              <input
                ref={fileInputRef}
                type="file"
                multiple
                accept=".xlsx,.xls,.pdf"
                onChange={handleFileSelect}
                hidden
              />

            </div>

            {/* Upload status */}

            {uploading && (
              <div className="upload-status">
                Uploading and analysing your
                financial data...
              </div>
            )}

            {/* Files */}

            {files.length > 0 && (
              <div className="file-list">

                {files.map(
                  (file, index) => (
                    <div
                      className="file-item"
                      key={`${file.name}-${index}`}
                    >

                      <div className="file-left">

                        <div className="file-type-icon">
                          {file.name
                            .toLowerCase()
                            .endsWith(".pdf")
                            ? "PDF"
                            : "XLS"}
                        </div>

                        <div>

                          <div className="file-name">
                            {file.name}
                          </div>

                          <div className="file-meta">
                            {(
                              file.size / 1024
                            ).toFixed(1)}{" "}
                            KB
                          </div>

                        </div>

                      </div>

                      <div className="file-right">

                        <span className="ready">
                          ✓ Ready
                        </span>

                        <button
                          className="remove-button"
                          onClick={(
                            event
                          ) => {
                            event.stopPropagation();

                            removeFile(
                              index
                            );
                          }}
                        >
                          ×
                        </button>

                      </div>

                    </div>
                  )
                )}

              </div>
            )}

          </div>

          {/* Ask Card */}

          <div className="card question-card">

            <div className="question-heading">

              <div className="ai-icon">
                ✦
              </div>

              <div>

                <h2>
                  Ask NexaMind
                </h2>

                <p>
                  Ask questions about your
                  uploaded data.
                </p>

              </div>

            </div>

            <div className="question-input">

              <textarea
                value={question}
                onChange={(event) =>
                  setQuestion(
                    event.target.value
                  )
                }
                onKeyDown={
                  handleQuestionKeyDown
                }
                placeholder="e.g. Which region generated the highest profit?"
                rows="4"
              />

              <div className="question-footer">

                <span>
                  {datasetId
                    ? "NexaMind will analyse your uploaded files"
                    : "Upload a file to start analysing"}
                </span>

                <button
                  className="ask-button"
                  onClick={askNexaMind}
                  disabled={
                    asking ||
                    !question.trim() ||
                    !datasetId
                  }
                >
                  {asking
                    ? "Analysing..."
                    : "Ask NexaMind"}

                  {!asking && (
                    <span>
                      →
                    </span>
                  )}
                </button>

              </div>

            </div>

          </div>

        </section>

        {/* Error */}

        {error && (
          <div className="error-message">
            {error}
          </div>
        )}

        {/* Answers */}

        {answers.length > 0 && (
          <section className="answers-section">

            <div className="answers-header">
              <div>
                <h2>
                  Analysis
                </h2>

                <p>
                  Your questions and NexaMind
                  results.
                </p>
              </div>

              <span className="answer-count">
                {answers.length}{" "}
                {answers.length === 1
                  ? "answer"
                  : "answers"}
              </span>
            </div>

            {answers.map(
              (answer, index) => (
                <div
                  className="card answer-card"
                  key={index}
                >

                  {/* Answer header */}

                  <div className="answer-card-header">

                    <div className="answer-number">
                      {index + 1}
                    </div>

                    <div>

                      <div className="answer-card-title">
                        NexaMind's answer
                      </div>

                      <div className="answer-card-subtitle">
                        Analysis based on your
                        financial data
                      </div>

                    </div>

                  </div>

                  {/* Question */}

                  <div className="asked-question">

                    <div className="asked-question-label">
                      You asked
                    </div>

                    <div className="asked-question-text">
                      {answer.question}
                    </div>

                  </div>

                  {/* Result */}

                  <div className="answer-content">

                    <div className="answer-label">
                      Result
                    </div>

                    {renderAnswerResult(
                      answer
                    )}

                    {answer.operation && (
                      <div className="answer-details">

                        {answer.operation}

                        {answer.column && (
                          <>
                            {" "}of{" "}

                            <strong>
                              {answer.column}
                            </strong>
                          </>
                        )}

                        {answer.operation ===
                          "GROUP_BY" &&
                          answer.group_by && (
                            <>
                              {" "}
                              grouped by{" "}

                              <strong>
                                {answer.group_by}
                              </strong>
                            </>
                          )}

                        {answer.sheet && (
                          <>
                            {" "}from{" "}

                            <strong>
                              {answer.sheet}
                            </strong>
                          </>
                        )}

                      </div>
                    )}

                  </div>

                </div>
              )
            )}

          </section>
        )}

        {/* Example questions */}

        <section className="examples">

          <div className="examples-title">
            Try asking
          </div>

          <div className="example-list">

            <button
              className="example-card"
              onClick={() =>
                askExample(
                  "Which country generated the highest profit?"
                )
              }
            >
              <span>
                ↗
              </span>

              Which country generated the
              highest profit?
            </button>

            <button
              className="example-card"
              onClick={() =>
                askExample(
                  "Calculate the total profit."
                )
              }
            >
              <span>
                ↗
              </span>

              Calculate the total profit.
            </button>

            <button
              className="example-card"
              onClick={() =>
                askExample(
                  "Which product generated the highest profit?"
                )
              }
            >
              <span>
                ↗
              </span>

              Which product generated the
              highest profit?
            </button>

          </div>

        </section>

      </main>

      <footer className="footer">

        <span>
          NexaMind
        </span>

        <span>
          Financial AI Copilot
        </span>

      </footer>

    </div>
  );
}

export default App;