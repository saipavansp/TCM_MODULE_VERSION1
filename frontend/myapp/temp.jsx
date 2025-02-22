import React, { useState } from "react";
import HomeScreen from "./HomeScreen";
import CallScreen from "./CallScreen";

function App() {
  const [inCall, setInCall] = useState(false);
  const [selectedScenario, setSelectedScenario] = useState("");

  return (
    <div style={{ width: "100%", height: "100vh" }}>
      {!inCall ? (
        <HomeScreen
          selectedScenario={selectedScenario}
          setSelectedScenario={setSelectedScenario}
          setInCall={setInCall}
        />
      ) : (
        <CallScreen
          scenario={selectedScenario}
          endCall={() => {
            setInCall(false);
            setSelectedScenario("");
          }}
        />
      )}
    </div>
  );
}

export default App;
