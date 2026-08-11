import { createSlice } from "@reduxjs/toolkit";

const initialState = {
  threadId: crypto.randomUUID(),
  form: {},
  riskAssessment: {},
  status: "Pending Triage",
  messages: [],
  loading: false,
};

const complaintSlice = createSlice({
  name: "complaint",
  initialState,
  reducers: {
    addUserMessage(state, action) {
      state.messages.push({ role: "user", content: action.payload });
    },
    setLoading(state, action) {
      state.loading = action.payload;
    },
    applyAgentResponse(state, action) {
      const { reply, form, risk_assessment, status } = action.payload;
      state.messages.push({ role: "assistant", content: reply });
      state.form = { ...state.form, ...form };
      state.riskAssessment = { ...state.riskAssessment, ...risk_assessment };
      state.status = status;
      state.loading = false;
    },
    setCommitted(state) {
      state.status = "Ready to Commit";
    },
    resetComplaint(state) {
      state.threadId = crypto.randomUUID();
      state.form = {};
      state.riskAssessment = {};
      state.status = "Pending Triage";
      state.messages = [];
    },
  },
});

export const {
  addUserMessage,
  setLoading,
  applyAgentResponse,
  setCommitted,
  resetComplaint,
} = complaintSlice.actions;

export default complaintSlice.reducer;
