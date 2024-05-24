import { useState } from "react";

export function App() {
  const [value, setValue] = useState(10);

  return (
    <div>
      <div>
        Value: {value}
      </div>

      <input type="range"
        value={value}
        onChange={e => setValue(+e.target.value)} />
    </div>
  );
}
