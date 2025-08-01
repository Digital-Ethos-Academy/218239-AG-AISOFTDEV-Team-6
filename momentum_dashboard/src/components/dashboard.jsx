import React, { useState } from 'react';

// ============================================================================
// 1. Icon Components
// ============================================================================
// Isolating SVGs into their own components makes them reusable and cleans up configuration arrays.

const SchedulerIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-blue-800" viewBox="0 0 24 24" fill="currentColor">
    <path d="M19 4h-1V2h-2v2H8V2H6v2H5c-1.11 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 16H5V10h14v10zM5 8V6h14v2H5zm5.5 8.5L9.17 15.17l-1.42 1.41L10.5 19 16.5 13l-1.41-1.42L10.5 16.5z" />
  </svg>
);

const FacilitatorIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-gray-800" viewBox="0 0 24 24" fill="currentColor">
    <path d="M12 1a9 9 0 0 0-9 9v7c0 1.66 1.34 3 3 3h1v-8H5v-2a7 7 0 0 1 14 0v2h-2v8h1c1.66 0 3-1.34 3-3v-7a9 9 0 0 0-9-9z" />
  </svg>
);

const TranscriberIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-gray-800" viewBox="0 0 24 24" fill="currentColor">
    <path d="M14 2H6c-1.1 0-2 .9-2 2v16c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V8l-6-6zm-1 9H8v2h5v-2zm-5 6h5v-2H8v2zm9 1h-3v2h3v1l3-2-3-2v1zM13 9V3.5L18.5 9H13z" />
  </svg>
);

// ============================================================================
// 2. Data Configuration
// ============================================================================
// Agent data is now a static configuration array, separating data from state logic.
const AGENTS_CONFIG = [
  { id: 'scheduler', label: 'Scheduler', Icon: SchedulerIcon },
  { id: 'facilitator', label: 'Facilitator', Icon: FacilitatorIcon },
  { id: 'transcriber', label: 'Transcriber', Icon: TranscriberIcon },
];


// ============================================================================
// 3. Reusable UI Components
// ============================================================================

/**
 * A reusable toggle switch component.
 * @param {{ enabled: boolean, onChange: () => void }} props
 */
const ToggleSwitch = ({ enabled, onChange }) => (
  <button
    type="button"
    role="switch"
    aria-checked={enabled}
    onClick={onChange}
    className={`relative inline-flex h-8 w-14 flex-shrink-0 cursor-pointer rounded-full border-2 border-black transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-blue-500 ${
      enabled ? 'bg-blue-500' : 'bg-gray-300'
    }`}
  >
    <span
      aria-hidden="true"
      className={`absolute left-1 top-1 h-6 w-6 rounded-full bg-white shadow-md transform transition-transform duration-200 ease-in-out ${
        enabled ? 'translate-x-6' : ''
      }`}
    />
  </button>
);

/**
 * A reusable action button with different visual styles.
 * @param {{ 
 *   onClick: () => void, 
 *   children: React.ReactNode, 
 *   variant?: 'primary' | 'secondary' 
 * }} props
 */
const ActionButton = ({ onClick, children, variant = 'secondary' }) => {
  const baseClasses = "w-full py-3 px-4 rounded-lg text-lg font-semibold transition-colors";
  const variantClasses = {
    primary: "bg-white border border-gray-300 text-gray-800 hover:bg-gray-100",
    secondary: "bg-white border border-gray-300 text-gray-800 hover:bg-gray-100",
  };
  // primary: "bg-[#5887E8] text-white hover:bg-opacity-90",
    // secondary: "bg-white border border-gray-300 text-gray-800 hover:bg-gray-100",
  
  return (
    <button onClick={onClick} className={`${baseClasses} ${variantClasses[variant]}`}>
      {children}
    </button>
  );
};

/**
 * Displays a single agent card with its icon, label, and toggle switch.
 * @param {{ 
 *   Icon: React.ElementType, 
 *   label: string, 
 *   enabled: boolean, 
 *   onToggle: () => void 
 * }} props
 */
const AgentCard = ({ Icon, label, enabled, onToggle }) => (
  <div className="bg-white p-4 rounded-xl border border-gray-200/75 shadow-sm flex justify-between items-center">
    <div className="flex items-center space-x-4">
      <Icon />
      <span className="text-xl font-medium text-gray-800">{label}</span>
    </div>
    <ToggleSwitch enabled={enabled} onChange={onToggle} />
  </div>
);

/**
 * Displays the live transcript panel when visible.
 */
const LiveTranscript = () => (
  <div className="mt-6 p-4 bg-white rounded-xl border border-gray-200/75 shadow-sm space-y-3 text-sm text-gray-700 animate-fade-in">
    <h3 className="font-semibold text-gray-800 text-base">Live Transcript</h3>
    <p><span className="font-semibold text-[#5887E8]">Alex:</span> Okay, so for the next quarter, we need to focus on user acquisition.</p>
    <p><span className="font-semibold text-green-600">Brenda:</span> I agree. Our current CAC is too high. I've prepared a deck with some ideas on organic growth.</p>
    <p><span className="font-semibold text-[#5887E8]">Alex:</span> Great, let's hear them. The floor is yours, Brenda.</p>
    <style>{`
      @keyframes fade-in {
        from { opacity: 0; transform: translateY(-10px); }
        to { opacity: 1; transform: translateY(0); }
      }
      .animate-fade-in {
        animation: fade-in 0.3s ease-out forwards;
      }
    `}</style>
  </div>
);


// ============================================================================
// 4. Main Application Component (Container)
// ============================================================================
// The MomentumDashboard component is now a "container" that manages state
// and composes the smaller, presentational components.

const MomentumDashboard = () => {
  // Centralized state for all agents for easier management
  const [agentStates, setAgentStates] = useState({
    scheduler: true,
    facilitator: false,
    transcriber: false,
  });
  const [showTranscript, setShowTranscript] = useState(false);

  // Handler to toggle a single agent's state
  const handleToggleAgent = (agentId) => {
    setAgentStates(prevStates => ({
      ...prevStates,
      [agentId]: !prevStates[agentId],
    }));
  };
  
  // Handler to enable or disable all agents at once
  const handleToggleAll = () => {
    const anyEnabled = Object.values(agentStates).some(isEnabled => isEnabled);
    const targetState = !anyEnabled;
    const newStates = {};
    Object.keys(agentStates).forEach(key => {
      newStates[key] = targetState;
    });
    setAgentStates(newStates);
  };
  
  return (
    <div className="bg-[#f8f9fa] flex items-center justify-center min-h-screen font-sans">
      <div className="w-full max-w-sm p-4">
        <h1 className="text-5xl font-bold text-center text-gray-800 mb-8">
          Momentum
        </h1>
        
        <div className="space-y-3">
          {AGENTS_CONFIG.map((agent) => (
            <AgentCard
              key={agent.id}
              Icon={agent.Icon}
              label={agent.label}
              enabled={agentStates[agent.id]}
              onToggle={() => handleToggleAgent(agent.id)}
            />
          ))}
        </div>
        
        <div className="mt-6 space-y-3">
          <ActionButton onClick={handleToggleAll}>
            Enable/disable all
          </ActionButton>
          <ActionButton
            onClick={() => setShowTranscript(!showTranscript)}
            variant="primary"
          >
            {showTranscript ? 'Hide live transcript' : 'Show live transcript'}
          </ActionButton>
        </div>
        
        {showTranscript && <LiveTranscript />}
      </div>
    </div>
  );
};

export default MomentumDashboard;