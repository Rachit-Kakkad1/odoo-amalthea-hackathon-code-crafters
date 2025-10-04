import React, { useState, useEffect } from "react";

const ROLES = {
  ADMIN: "ADMIN",
  MANAGER: "MANAGER",
  EMPLOYEE: "EMPLOYEE",
};

const APPROVAL_STATUSES = {
  PENDING: "PENDING",
  APPROVED: "APPROVED",
  REJECTED: "REJECTED",
};

const defaultCompany = {
  id: 1,
  name: "AutoCreated Inc.",
  currency: "USD",
};

function App() {
  // Simulated state for company and users
  const [company] = useState(defaultCompany);
  const [users, setUsers] = useState([
    { id: 1, name: "Admin User", role: ROLES.ADMIN, managerId: null },
  ]);
  const [currentUser, setCurrentUser] = useState(users[0]);
  const [expenses, setExpenses] = useState([]);
  const [nextUserId, setNextUserId] = useState(2);
  const [newUser, setNewUser] = useState({ name: "", role: ROLES.EMPLOYEE, managerId: null });
  const [newExpense, setNewExpense] = useState({ amount: "", currency: company.currency, category: "", description: "", date: "" });

  // Approval sequence default (admin can configure)
  const [approvalSequence, setApprovalSequence] = useState([ROLES.MANAGER, "FINANCE", "DIRECTOR"]);
  
  // Add user (Admin only)
  const addUser = () => {
    if (newUser.name.trim() === "") return;
    const user = { id: nextUserId, ...newUser };
    setUsers((u) => [...u, user]);
    setNextUserId(nextUserId + 1);
    setNewUser({ name: "", role: ROLES.EMPLOYEE, managerId: null });
  };

  // Filter user lists
  const managers = users.filter(u => u.role === ROLES.MANAGER);
  const employees = users.filter(u => u.role === ROLES.EMPLOYEE);

  // Submit expense (Employees only)
  const submitExpense = () => {
    if (!newExpense.amount || !newExpense.description || !newExpense.date) return alert("Fill all required fields");
    const expense = {
      id: expenses.length + 1,
      employeeId: currentUser.id,
      amount: parseFloat(newExpense.amount),
      currency: newExpense.currency,
      category: newExpense.category,
      description: newExpense.description,
      date: newExpense.date,
      status: APPROVAL_STATUSES.PENDING,
      currentApproverIndex: 0,
      approvalHistory: [],
    };
    setExpenses([...expenses, expense]);
    setNewExpense({ amount: "", currency: company.currency, category: "", description: "", date: "" });
  };

  // Get current user's expenses (employees)
  const myExpenses = expenses.filter(exp => exp.employeeId === currentUser.id);

  // Get approvals required for manager/admin
  const approvalsForUser = expenses.filter(exp => {
    if (currentUser.role === ROLES.MANAGER) {
      // Manager approves employees who report to them and are currently at step 0 (Manager step)
      if (approvalSequence[0] === ROLES.MANAGER) {
        return exp.status === APPROVAL_STATUSES.PENDING && exp.currentApproverIndex === 0 &&
               users.find(u => u.id === exp.employeeId)?.managerId === currentUser.id;
      }
      return false;
    } else if (currentUser.role === ROLES.ADMIN) {
      // Admin can approve after others, or all if sequence allows
      let stepRole = approvalSequence[exp.currentApproverIndex];
      return exp.status === APPROVAL_STATUSES.PENDING && stepRole !== ROLES.MANAGER;
    }
    return false;
  });

  // Approve or reject expense
  const handleApproval = (expenseId, approved) => {
    setExpenses(exps =>
      exps.map(exp => {
        if (exp.id !== expenseId) return exp;
        const historyEntry = { approverId: currentUser.id, approved, date: new Date().toISOString() };
        if (approved) {
          if (exp.currentApproverIndex + 1 >= approvalSequence.length) {
            return { ...exp, status: APPROVAL_STATUSES.APPROVED, approvalHistory: [...exp.approvalHistory, historyEntry], currentApproverIndex: exp.currentApproverIndex + 1 };
          } else {
            return { ...exp, currentApproverIndex: exp.currentApproverIndex + 1, approvalHistory: [...exp.approvalHistory, historyEntry] };
          }
        } else {
          return { ...exp, status: APPROVAL_STATUSES.REJECTED, approvalHistory: [...exp.approvalHistory, historyEntry] };
        }
      })
    );
  };

  return (
    <div style={{ padding: 20, fontFamily: "Arial, sans-serif", backgroundColor: "#121212", color: "#eee" }}>
      <h1>Expense Management System</h1>
      <p>Company: {company.name} (Currency: {company.currency})</p>
      <p>Logged in as: {currentUser.name} ({currentUser.role})</p>
      <hr />

      {/* User switcher */}
      <div>
        <label>Switch User: </label>
        <select onChange={e => setCurrentUser(users.find(u => u.id === +e.target.value))} value={currentUser.id}>
          {users.map(u => <option key={u.id} value={u.id}>{u.name} ({u.role})</option>)}
        </select>
      </div>
      <hr />

      {/* Admin Section */}
      {currentUser.role === ROLES.ADMIN && (
        <div style={{ background: "#222", padding: 10, marginBottom: 20 }}>
          <h2>Admin Panel - Create User</h2>
          <input
            placeholder="Name"
            value={newUser.name}
            onChange={e => setNewUser({...newUser, name: e.target.value})}
          />
          <select value={newUser.role} onChange={e => setNewUser({...newUser, role: e.target.value})}>
            <option value={ROLES.EMPLOYEE}>Employee</option>
            <option value={ROLES.MANAGER}>Manager</option>
          </select>
          <select
            value={newUser.managerId || ""}
            onChange={e => setNewUser({...newUser, managerId: e.target.value === "" ? null : +e.target.value})}
          >
            <option value="">No Manager</option>
            {managers.map(m => <option key={m.id} value={m.id}>{m.name}</option>)}
          </select>
          <button onClick={addUser}>Add User</button>

          <h3>All Users</h3>
          {users.map(u => (
            <div key={u.id}>
              {u.name} - {u.role} {u.managerId && `(Manager: ${users.find(x => x.id === u.managerId)?.name || "N/A"})`}
            </div>
          ))}
        </div>
      )}

      {/* Employee Expense Submission */}
      {currentUser.role === ROLES.EMPLOYEE && (
        <div style={{ background: "#222", padding: 10, marginBottom: 20 }}>
          <h2>Submit Expense</h2>
          <input
            type="number"
            placeholder="Amount"
            value={newExpense.amount}
            onChange={e => setNewExpense({...newExpense, amount: e.target.value})}
          />
          <input
            placeholder="Currency"
            value={newExpense.currency}
            onChange={e => setNewExpense({...newExpense, currency: e.target.value})}
          />
          <input
            placeholder="Category"
            value={newExpense.category}
            onChange={e => setNewExpense({...newExpense, category: e.target.value})}
          />
          <input
            placeholder="Description"
            value={newExpense.description}
            onChange={e => setNewExpense({...newExpense, description: e.target.value})}
          />
          <input
            type="date"
            value={newExpense.date}
            onChange={e => setNewExpense({...newExpense, date: e.target.value})}
          />
          <button onClick={submitExpense}>Submit Expense</button>

          <h3>My Expense History</h3>
          {myExpenses.map(exp => (
            <div key={exp.id} style={{ marginBottom: 10, borderBottom: "1px solid #444" }}>
              <div>{exp.date} - {exp.category} - {exp.description}</div>
              <div>Amount: {exp.amount} {exp.currency}</div>
              <div>Status: {exp.status}</div>
            </div>
          ))}
        </div>
      )}

      {/* Approvals for Manager/Admin */}
      {(currentUser.role === ROLES.MANAGER || currentUser.role === ROLES.ADMIN) && (
        <div style={{ background: "#222", padding: 10, marginBottom: 20 }}>
          <h2>Expenses to Approve</h2>
          {approvalsForUser.length === 0 && <div>No expenses awaiting your approval.</div>}
          {approvalsForUser.map(exp => (
            <div key={exp.id} style={{ borderBottom: "1px solid #444", marginBottom: 10 }}>
              <div>
                <b>{users.find(u => u.id === exp.employeeId)?.name || "Unknown"}'s Expense</b>
                <div>{exp.date} - {exp.category} - {exp.description}</div>
                <div>Amount: {exp.amount} {exp.currency}</div>
              </div>
              <button style={{ marginRight: 10 }} onClick={() => handleApproval(exp.id, true)}>Approve</button>
              <button onClick={() => handleApproval(exp.id, false)}>Reject</button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default App;
    