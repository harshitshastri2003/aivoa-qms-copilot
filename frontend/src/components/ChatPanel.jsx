import { useState, useRef } from "react";
import { useDispatch, useSelector } from "react-redux";
import {
  addUserMessage,
  setLoading,
  applyAgentResponse,
} from "../store/complaintSlice";
import { sendChatMessage, uploadDocument } from "../api/api";

export default function ChatPanel() {
  const dispatch = useDispatch();
  const { threadId, messages, loading } = useSelector((s) => s.complaint);
  const [input, setInput] = useState("");
  const fileInputRef = useRef(null);

  async function handleSend() {
    if (!input.trim() || loading) return;
    const text = input;
    setInput("");
    dispatch(addUserMessage(text));
    dispatch(setLoading(true));
    try {
      const result = await sendChatMessage(threadId, text);
      dispatch(applyAgentResponse(result));
    } catch (err) {
      dispatch(setLoading(false));
      alert(err.message);
    }
  }

  async function handleFileChange(e) {
    const file = e.target.files[0];
    if (!file) return;
    dispatch(addUserMessage(`Uploaded document: ${file.name}`));
    dispatch(setLoading(true));
    try {
      const result = await uploadDocument(threadId, file);
      dispatch(applyAgentResponse(result));
    } catch (err) {
      dispatch(setLoading(false));
      alert(err.message);
    }
    e.target.value = "";
  }

  function handleKeyDown(e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }

  return (
    <div className="chat-panel">
      <div className="chat-header">AIVOA Copilot</div>

      <div className="chat-messages">
        {messages.map((m, i) => (
          <div key={i} className={`chat-bubble ${m.role}`}>
            {m.content}
          </div>
        ))}
        {loading && <div className="chat-bubble assistant typing">Thinking...</div>}
      </div>

      <div className="chat-input-row">
        <button
          className="attach-btn"
          onClick={() => fileInputRef.current.click()}
          title="Upload complaint document"
        >
          +
        </button>
        <input
          type="file"
          ref={fileInputRef}
          style={{ display: "none" }}
          accept=".pdf,.txt"
          onChange={handleFileChange}
        />
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Describe the complaint, or send a correction..."
          rows={2}
        />
        <button className="send-btn" onClick={handleSend} disabled={loading}>
          Send
        </button>
      </div>
      <div className="powered-by">Powered by LangGraph</div>
    </div>
  );
}
