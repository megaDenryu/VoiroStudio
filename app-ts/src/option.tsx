import React from "react";
import ReactDOM from "react-dom/client";
import { Slider } from "./Slider";
// import "./index.css";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <Option />
  </React.StrictMode>
);

function Option() {
  return (
    <div>
      <h1>オプション</h1>

      <Slider />
    </div>
  );
}
