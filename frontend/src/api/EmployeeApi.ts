import { Employee } from "../types/Employee";

const API_URL = "http://localhost:5201/api/employees";
const AUTH_TOKEN = "Bearer mysecrettoken";

async function fetchEmployees(): Promise<Employee[]> {
  const res = await fetch(API_URL, {
    headers: { Authorization: AUTH_TOKEN },
  });
  if (!res.ok) throw new Error("Failed to fetch employees");
  return res.json();
}

async function fetchEmployee(id: number): Promise<Employee> {
  const res = await fetch(`${API_URL}/${id}`, {
    headers: { Authorization: AUTH_TOKEN },
  });
  if (!res.ok) throw new Error("Failed to fetch employee");
  return res.json();
}

async function createEmployee(employee: Omit<Employee, "id">): Promise<Employee> {
  const res = await fetch(API_URL, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: AUTH_TOKEN,
    },
    body: JSON.stringify(employee),
  });
  if (!res.ok) throw new Error("Failed to create employee");
  return res.json();
}

async function updateEmployee(employee: Employee): Promise<void> {
  const res = await fetch(`${API_URL}/${employee.id}`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
      Authorization: AUTH_TOKEN,
    },
    body: JSON.stringify(employee),
  });
  if (!res.ok) throw new Error("Failed to update employee");
}

async function deleteEmployee(id: number): Promise<void> {
  const res = await fetch(`${API_URL}/${id}`, {
    method: "DELETE",
    headers: { Authorization: AUTH_TOKEN },
  });
  if (!res.ok) throw new Error("Failed to delete employee");
}

export const EmployeeApi = {
  fetchEmployees,
  fetchEmployee,
  createEmployee,
  updateEmployee,
  deleteEmployee,
};
