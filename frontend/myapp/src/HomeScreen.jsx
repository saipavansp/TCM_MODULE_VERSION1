import React, { useState } from "react";

const HomeScreen = ({ selectedScenario, setSelectedScenario, setInCall }) => {
  // scenario list
  const scenarios = [
    "Prompt 1: Silent",
    "Prompt 2: Busy Customer",
    "Prompt 3: Complaining Customer",
    "Prompt 4: Angry Customer",
    "Prompt 5: diverting",
    "Prompt 6: confused",
    "Prompt 7: Flirting Customers",
    "Prompt 8: Existing Customer",
    "Prompt 9: Handling Customers Expecting a Call for a Previous Process",
    "Prompt 10: Delaying Customer"
  ];

  const handleMakeCall = () => {
    if (!selectedScenario) {
      alert("Please select a scenario first.");
      return;
    }

    // Play ring sound
    const ringAudio = new Audio("/phone-pick-up.mp3");
    ringAudio.play().catch(err => console.error("Failed to play ring:", err));

    setTimeout(() => {

      ringAudio.pause();
      ringAudio.currentTime = 0; // reset playback

//        Navigate to the call screen
      setInCall(true);
    }, 3000);
  };

  return (
    <div style={{ padding: "20px" }}>
      <h2>Select a Scenario</h2>
      <select
        value={selectedScenario}
        onChange={(e) => setSelectedScenario(e.target.value)}
        style={{ fontSize: "16px", padding: "5px" }}
      >
        <option value="">-- Select Scenario --</option>
        {scenarios.map((scenario, index) => (
          <option key={index} value={scenario}>
            {scenario}
          </option>
        ))}
      </select>
      <br />
      <br />
      <button onClick={handleMakeCall} style={{ fontSize: "16px", padding: "10px 20px" }}>
        Make Call
      </button>
    </div>
  );
};

export default HomeScreen;
