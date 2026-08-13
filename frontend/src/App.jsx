import { useRef, useState } from "react";
import "./App.css";

const API_BASE_URL = "http://127.0.0.1:8000";

function App() {
  const fileInputRef = useRef(null);

  const [files, setFiles] = useState([]);
  const [datasetId, setDatasetId] = useState(null);

  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState(null);

  const [uploading, setUploading] = useState(false);
  const [asking, setAsking] = useState(false);
  const [error, setError] = useState("");

  const handleFileSelect = async (event) => {
    const selectedFiles = Array.from(event.target.files);

    event.target.value = "";

    if (selectedFiles.length === 0) {
      return;
    }

    setError("");

    for (const file of selectedFiles) {
      await uploadFile(file);
    }
  };

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

      setFiles((currentFiles) => [
        ...currentFiles,
        file,
      ]);

      // Store the dataset ID returned by FastAPI
      setDatasetId(data.dataset_id);

    } catch (err) {
      console.error(err);

      setError(
        `Failed to upload ${file.name}`
      );
    } finally {
      setUploading(false);
    }
  };

  const removeFile = (indexToRemove) => {
    setFiles((currentFiles) =>
      currentFiles.filter(
        (_, index) => index !== indexToRemove
      )
    );

    // For now, reset dataset when a file is removed.
    setDatasetId(null);
    setAnswer(null);
  };

  const openFilePicker = () => {
    fileInputRef.current?.click();
  };

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
    setAnswer(null);

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
            question: question,
          }),
        }
      );

      if (!response.ok) {
        throw new Error("Failed to get answer");
      }

      const data = await response.json();

      console.log("Ask response:", data);

      setAnswer(data);

    } catch (err) {
      console.error(err);

      setError(
        "Something went wrong while analysing your data."
      );
    } finally {
      setAsking(false);
    }
  };

  const useExampleQuestion = (example) => {
    setQuestion(example);
  };

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
            Upload your financial documents, ask questions,
            <br />
            and get clear answers backed by your data.
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
                  Upload one or more files to get started.
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
                {uploading
                  ? "Uploading..."
                  : "Drop your files here"}
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


            {/* Files */}
            {files.length > 0 && (

              <div className="file-list">

                {files.map((file, index) => (

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

                          {(file.size / 1024).toFixed(1)}
                          {" KB"}

                        </div>

                      </div>

                    </div>


                    <div className="file-right">

                      <span className="ready">
                        ✓ Ready
                      </span>

                      <button
                        className="remove-button"
                        onClick={(event) => {

                          event.stopPropagation();

                          removeFile(index);

                        }}
                      >
                        ×
                      </button>

                    </div>

                  </div>

                ))}

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
                  Ask questions about your uploaded data.
                </p>

              </div>

            </div>


            <div className="question-input">

              <textarea
                placeholder="e.g. Calculate the total profit"
                rows="4"
                value={question}
                onChange={(event) =>
                  setQuestion(event.target.value)
                }
              />


              <div className="question-footer">

                <span>
                  NexaMind will analyse your uploaded files
                </span>


                <button
                  className="ask-button"
                  onClick={askNexaMind}
                  disabled={asking}
                >

                  {asking
                    ? "Analysing..."
                    : "Ask NexaMind"}

                  {!asking && (
                    <span>→</span>
                  )}

                </button>

              </div>

            </div>

          </div>


          {/* Answer */}
          {answer && (

            <div className="card answer-card">

              <div className="question-heading">

                <div className="ai-icon">
                  ✦
                </div>

                <div>

                  <h2>
                    NexaMind's answer
                  </h2>

                  <p>
                    Based on your uploaded financial data.
                  </p>

                </div>

              </div>


              <div className="answer-content">

                {answer.result !== undefined ? (

                  <>
                    <div className="answer-label">
                      Result
                    </div>

                    <div className="answer-result">

                      {Number(answer.result).toLocaleString(
                        undefined,
                        {
                          minimumFractionDigits: 2,
                          maximumFractionDigits: 2,
                        }
                      )}

                    </div>

                    <div className="answer-details">

                      {answer.operation} of{" "}
                      <strong>
                        {answer.column}
                      </strong>

                      {" "}from{" "}

                      <strong>
                        {answer.sheet}
                      </strong>

                    </div>

                  </>

                ) : (

                  <div>
                    {answer.message}
                  </div>

                )}

              </div>

            </div>

          )}


          {/* Error */}
          {error && (

            <div className="error-message">
              {error}
            </div>

          )}

        </section>


        {/* Example questions */}
        <section className="examples">

          <div className="examples-title">
            Try asking
          </div>


          <div className="example-list">

            <button
              className="example-card"
              onClick={() =>
                useExampleQuestion(
                  "Calculate the total profit"
                )
              }
            >

              <span>↗</span>

              Calculate the total profit.

            </button>


            <button
              className="example-card"
              onClick={() =>
                useExampleQuestion(
                  "Calculate the total sales"
                )
              }
            >

              <span>↗</span>

              Calculate the total sales.

            </button>


            <button
              className="example-card"
              onClick={() =>
                useExampleQuestion(
                  "Calculate the total profit"
                )
              }
            >

              <span>↗</span>

              What is the total profit?

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