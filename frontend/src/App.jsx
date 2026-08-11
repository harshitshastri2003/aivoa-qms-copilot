import ComplaintForm from "./components/ComplaintForm";
import ChatPanel from "./components/ChatPanel";
import "./App.css";

export default function App() {
  return (
    <div className="app-shell">
      <div className="form-pane">
        <ComplaintForm />
      </div>
      <div className="chat-pane">
        <ChatPanel />
      </div>
    </div>
  );
}
