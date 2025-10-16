import React, { useEffect, useState } from "react";
import { Employee } from "./types/Employee";
import { EmployeeApi } from "./api/EmployeeApi";

const EmployeeList: React.FC<{
  onEdit: (employee: Employee) => void;
  onDelete: (id: number) => void;
}> = ({ onEdit, onDelete }) => {
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    EmployeeApi.fetchEmployees()
      .then(setEmployees)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <p>Loading...</p>;
  if (error) return <p>Error: {error}</p>;

  return (
    <table>
      <thead>
        <tr>
          <th>First Name</th>
          <th>Last Name</th>
          <th>Email</th>
          <th>Position</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        {employees.map((emp) => (
          <tr key={emp.id}>
            <td>{emp.firstName}</td>
            <td>{emp.lastName}</td>
            <td>{emp.email}</td>
            <td>{emp.position}</td>
            <td>
              <button onClick={() => onEdit(emp)}>Edit</button>
              <button onClick={() => onDelete(emp.id)}>Delete</button>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
};

export default EmployeeList;
