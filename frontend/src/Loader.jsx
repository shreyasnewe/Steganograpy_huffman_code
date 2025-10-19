// Loader.jsx
import React from "react";
import { Loader2 } from "lucide-react"; // optional spinner icon
import "./loader.css";

export default function Loader() {
  return (
    <div className="loader-overlay">
      <div className="loader-content">
        <img
          herf="D:\MyWokSpace\Stegnography_main\frontend\src\assets\logo.png" // use the relative path from public
          alt="Logo"
          className="loader-logo"
        />
        <Loader2 className="spinner text-white" />
      </div>
    </div>
  );
}
