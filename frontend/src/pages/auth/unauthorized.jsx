import { useNavigate } from "react-router-dom";

function Unauthorized() {
  const navigate = useNavigate();

  return (
    <div className="login-page">
      <div className="login-card">
        <h1>Access Denied</h1>

        <p>
          You do not have permission to access this page.
        </p>

        <button onClick={() => navigate("/")}>
          Go Home
        </button>
      </div>
    </div>
  );
}

export default Unauthorized;