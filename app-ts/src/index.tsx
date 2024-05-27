import React from "react";
import ReactDOM from "react-dom/client";
import { Slider } from "./Slider";
import { JS_VALUE, jsFunc } from "./isJs";
// import "./index.css";

ReactDOM.createRoot(document.getElementById("root")!)
  .render(
    <React.StrictMode>
      <App />
    </React.StrictMode>
  );

export function App() {
  jsFunc(JS_VALUE);
  // jsFunc("HAY"); // 型エラー

  return (
    <div>
      <h1>INDEX</h1>

      <Slider />
    </div>
  );
}
