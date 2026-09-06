import { useState } from "react";
import "./GeminiSetup.css";

function GeminiSetup({ apiBaseUrl, onConnected, onCancel, isSettings = false }) {
  const [apiKey, setApiKey] = useState("");
  const [showKey, setShowKey] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  const saveKey = async () => {
    if (!apiKey.trim()) {
      setError("Please enter your Gemini API key.");
      return;
    }

    try {
      setSaving(true);
      setError("");

      const response = await fetch(
        `${apiBaseUrl}/settings/gemini-key`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            api_key: apiKey.trim(),
          }),
        }
      );

      const data = await response.json();

      if (!response.ok || !data.success) {
        throw new Error(
          data.message || "Failed to save Gemini API key."
        );
      }

      onConnected();
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="gemini-setup-page">
      <div className="gemini-setup-card">
        {isSettings && onCancel && (
          <button
            type="button"
            className="gemini-back-button"
            onClick={onCancel}
          >
            <span aria-hidden="true">←</span>
            Back to chat
          </button>
        )}

        <div className="gemini-setup-logo">
          ✦
        </div>

        <h1>NexaMind</h1>

        <h2>{isSettings ? "Gemini Settings" : "Connect Gemini"}</h2>

        <p className="gemini-setup-description">
          {isSettings
            ? "Update your Gemini API key, or return to your chat without making any changes."
            : "Add your Gemini API key to start asking questions about your uploaded workbook."}
        </p>

        <label className="gemini-key-label">
          Gemini API Key
        </label>

        <div className="gemini-key-input-wrapper">
          <input
            type={showKey ? "text" : "password"}
            value={apiKey}
            onChange={(event) =>
              setApiKey(event.target.value)
            }
            placeholder="Enter your Gemini API key"
            onKeyDown={(event) => {
              if (event.key === "Enter") {
                saveKey();
              }
            }}
          />

          <button
            type="button"
            className="gemini-key-toggle"
            onClick={() => setShowKey(!showKey)}
          >
            {showKey ? "Hide" : "Show"}
          </button>
        </div>

        {error && (
          <div className="gemini-setup-error">
            {error}
          </div>
        )}

        <button
          type="button"
          className="gemini-connect-button"
          onClick={saveKey}
          disabled={saving}
        >
          {saving
            ? (isSettings ? "Updating..." : "Connecting...")
            : (isSettings ? "Update API Key" : "Connect & Continue")}
        </button>

        <div className="gemini-setup-security">
          🔒 Your API key is stored securely on this device.
        </div>
      </div>
    </div>
  );
}

export default GeminiSetup;