import { useState } from "react";

export function Slider() {
  const [value, setValue] = useState(10);

  return (
    <>
      <div>
        Value: {value}
      </div>

      <input type="range"
        value={value}
        onChange={e => setValue(+e.target.value)} />
    </>
  );
}
