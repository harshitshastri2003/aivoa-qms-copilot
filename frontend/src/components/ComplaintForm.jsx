import { useDispatch, useSelector } from "react-redux";
import { setCommitted } from "../store/complaintSlice";
import { commitComplaint } from "../api/api";

function Field({ label, value }) {
  return (
    <div className="field">
      <label>{label}</label>
      <div className="field-value">{value || "—"}</div>
    </div>
  );
}

export default function ComplaintForm() {
  const dispatch = useDispatch();
  const { threadId, form, riskAssessment, status } = useSelector(
    (s) => s.complaint
  );

  async function handleCommit() {
    await commitComplaint(threadId);
    dispatch(setCommitted());
  }

  return (
    <div className="complaint-form">
      <div className="form-header">
        <h2>Log Customer Complaint</h2>
        <span className={`status-badge ${status === "Ready to Commit" ? "ready" : "pending"}`}>
          {status}
        </span>
      </div>

      <section>
        <h3>Origin & Customer Details</h3>
        <Field label="Customer Name" value={form.customer_name} />
        <Field label="Complaint Source" value={form.complaint_source} />
      </section>

      <section>
        <h3>Product & Batch Identification</h3>
        <Field label="Product Name" value={form.product_name} />
        <Field label="Strength" value={form.strength} />
        <Field label="Batch / Lot Number" value={form.batch_number} />
        <Field label="Manufacturing Date" value={form.manufacturing_date} />
        <Field label="Expiry Date" value={form.expiry_date} />
      </section>

      <section>
        <h3>Facility & Material Impact</h3>
        <Field label="Facility Name" value={form.facility_name} />
        <Field label="Affected Quantity" value={form.affected_quantity} />
      </section>

      <section>
        <h3>Defect Analysis</h3>
        <Field label="Defect Description" value={form.defect_description} />

        <div className="risk-subsection">
          <h4>AI Copilot Risk Assessment</h4>
          <Field label="Severity" value={riskAssessment.severity} />
          <Field label="Suggested Next Action" value={riskAssessment.suggested_next_action} />
          <Field label="Initial Risk Assessment" value={riskAssessment.risk_summary} />
        </div>
      </section>

      <button className="commit-btn" onClick={handleCommit}>
        Commit to QMS Ledger
      </button>
    </div>
  );
}
