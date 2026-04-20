import { Navigate } from "react-router-dom";

import PropTypes from "prop-types";

ProtectedRoute.propTypes = {
  children: PropTypes.node.isRequired
};

export default function ProtectedRoute({ children }) {
  const token = localStorage.getItem("access_token");

  if (!token) {
    return <Navigate to="/login" replace />;
  }

  return children;
}