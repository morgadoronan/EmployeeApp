

import React, { useState } from "react";
import EmployeeList from "./EmployeeList";
import EmployeeForm from "./EmployeeForm";
import { Employee } from "./types/Employee";
import { EmployeeApi } from "./api/EmployeeApi";

function App() {
  const [editing, setEditing] = useState<Employee | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleEdit = (employee: Employee) => setEditing(employee);
  const handleDelete = async (id: number) => {
    setLoading(true);
    setError(null);
    try {
      await EmployeeApi.deleteEmployee(id);
      window.location.reload();
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (data: Omit<Employee, "id">) => {
    setLoading(true);
    setError(null);
    try {
      if (editing) {
        await EmployeeApi.updateEmployee({ ...editing, ...data });
      } else {
        await EmployeeApi.createEmployee(data);
      }
      setEditing(null);
      window.location.reload();
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="App">
      <header style={{marginBottom: 24}}>
        <h1 style={{fontWeight: 700, fontSize: '2.2rem', letterSpacing: '.01em'}}>👩‍💼 Employee Management</h1>
        <p style={{color: '#4f8cff', fontSize: '1.1rem', margin: 0}}>
          Add, edit, and manage your team easily
        </p>
      </header>
      <section style={{marginBottom: 32, background: '#f7faff', borderRadius: 8, padding: 18, boxShadow: '0 1px 4px #e3eafc'}}> 
        <h2 style={{fontSize: '1.2rem', color: '#2d3a4b', margin: '0 0 10px 0', fontWeight: 600}}>
          {editing ? 'Edit Employee' : 'Add New Employee'}
        </h2>
        <EmployeeForm
          initial={editing ?? undefined}
          onSubmit={handleSubmit}
          loading={loading}
        />
      </section>
      <section>
        <h2 style={{fontSize: '1.2rem', color: '#2d3a4b', margin: '0 0 10px 0', fontWeight: 600}}>Employee List</h2>
        {error && <p style={{ color: "red" }}>{error}</p>}
        <EmployeeList onEdit={handleEdit} onDelete={handleDelete} />
      </section>
      <footer style={{marginTop: 32, color: '#b6c6e3', fontSize: '.95rem', textAlign: 'center'}}>
        <span>Made with <span style={{color: '#4f8cff'}}>React &amp; .NET</span></span>
      </footer>
    </main>
  );
}

export default App;
