import React, { useState } from "react";

const CallScreen = ({ scenario, endCall }) => {
  // Example conversation state
  const [messages, setMessages] = useState([
    { sender: "Customer", text: "Hello, this is the customer." }
  ]);
  const [agentInput, setAgentInput] = useState("");

  //handleSend
  const handleSend = () => {
    if (agentInput.trim()) {
      // Add agent message
      setMessages((prev) => [...prev, { sender: "Agent", text: agentInput }]);
      // Clear input
      setAgentInput("");
      // Simulate a short customer reply
      setTimeout(() => {
        setMessages((prev) => [
          ...prev,
          { sender: "Customer", text: "Sure, let’s talk about it." }
        ]);
      }, 1000);
    }
  };

  return (
    <div style={{ width: "100%", height: "100%", display: "flex", flexDirection: "column" }}>
      {/* Top bar  */}
      <div
        style={{
          height: "60px",
          backgroundColor: "#f2f2f2",
          display: "flex",
          alignItems: "center",
          padding: "0 20px",
          justifyContent: "space-between"
        }}
      >
        <h3>{scenario}</h3>
        <h3>Interview on python - SAMUEL RAJ P</h3>
      </div>

      {/* Main content area */}
      <div style={{ flex: 1, display: "flex" }}>
        {/* Left area: conversation */}
        <div style={{ flex: 2, backgroundColor: "#ffffff", padding: "20px" }}>
          <div style={{ height: "100%", overflowY: "auto", border: "1px solid #ccc" }}>
            {messages.map((msg, index) => (
              <div key={index} style={{ margin: "10px" }}>
                <strong>{msg.sender}:</strong> {msg.text}
              </div>
            ))}
          </div>
        </div>

        {/* Right area: user image + details */}
        <div style={{ flex: 1, display: "flex", flexDirection: "column" }}>
          {/* User image (top) */}
          <div
            style={{
              flex: 1,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              borderBottom: "1px solid #ccc"
            }}
          >
            <img
              src="https://via.placeholder.com/150"
              alt="User"
              style={{ width: "150px", height: "150px", borderRadius: "50%" }}
            />
          </div>
          {/* Additional info (bottom) */}
          <div style={{ flex: 1, display: "flex", flexDirection: "column" }}>
            <div style={{ flex: 1, borderBottom: "1px solid #ccc", padding: "10px" }}>
              <h4>Connection</h4>
              <p>Connection status: Good</p>
            </div>
            <div style={{ flex: 1, padding: "10px" }}>
              <h4>Interview details</h4>
              <p>Scenario: {scenario}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Bottom bar */}
      <div
        style={{
          height: "60px",
          backgroundColor: "#f2f2f2",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          padding: "0 20px"
        }}
      >
        {/* Input & Controls */}
        <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
          <input
            type="text"
            placeholder="Type your answer here..."
            value={agentInput}
            onChange={(e) => setAgentInput(e.target.value)}
            style={{ width: "400px", padding: "8px" }}
          />
          <button onClick={handleSend}>Send</button>
        </div>
        {/* End Call */}
        <button
          style={{
            backgroundColor: "red",
            color: "white",
            padding: "10px 20px",
            border: "none",
            borderRadius: "4px"
          }}
          onClick={endCall}
        >
          End Call
        </button>
      </div>
    </div>
  );
};

export default CallScreen;
