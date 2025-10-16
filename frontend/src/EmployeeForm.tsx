import React, { useState } from "react";
import { Employee } from "./types/Employee";

interface Props {
  initial?: Partial<Employee>;
  onSubmit: (employee: Omit<Employee, "id"> | Employee) => void;
  loading?: boolean;
}

const EmployeeForm: React.FC<Props> = ({ initial = {}, onSubmit, loading }) => {
  const [firstName, setFirstName] = useState(initial.firstName || "");
  const [lastName, setLastName] = useState(initial.lastName || "");
  const [email, setEmail] = useState(initial.email || "");
  const [position, setPosition] = useState(initial.position || "");
  const [error, setError] = useState<string | null>(null);

  function validate() {
    if (!firstName || !lastName || !email || !position) {
      setError("All fields are required.");
      return false;
    }
    if (!/^\S+@\S+\.\S+$/.test(email)) {
      setError("Invalid email format.");
      return false;
    }
    setError(null);
    return true;
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!validate()) return;
    onSubmit({ firstName, lastName, email, position });
  }

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="text"
        placeholder="First Name"
        value={firstName}
        onChange={(e) => setFirstName(e.target.value)}
        required
      />
      <input
        type="text"
        placeholder="Last Name"
        value={lastName}
        onChange={(e) => setLastName(e.target.value)}
        required
      />
      <input
        type="email"
        placeholder="Email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        required
      />
      <input
        type="text"
        placeholder="Position"
        value={position}
        onChange={(e) => setPosition(e.target.value)}
        required
      />
      {error && <p style={{ color: "red" }}>{error}</p>}
      <button type="submit" disabled={loading}>Submit</button>
    </form>
  );
};

export default EmployeeForm;
