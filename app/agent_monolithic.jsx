import React, { useState } from 'react';

const MomentumDashboard = () => {
  const [schedulerEnabled, setSchedulerEnabled] = useState(true);
  const [facilitatorEnabled, setFacilitatorEnabled] = useState(false);
  const [transcriberEnabled, setTranscriberEnabled] = useState(false);
  const [showTranscript, setShowTranscript] = useState(false);

  const agents = [
    {
      id: 'scheduler',
      label: 'Scheduler',
      icon: (
        <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-gray-800" viewBox="0 0 24 24" fill="currentColor">
          <path d="M19 4h-1V2h-2v2H8V2H6v2H5c-1.11 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 16H5V10h14v10zM5 8V6h14v2H5zm5.5 8.5L9.17 15.17l-1.42 1.41L10.5 19 16.5 13l-1.41-1.42L10.5 16.5z" />
        </svg>
      ),
      enabled: schedulerEnabled,
      setEnabled: setSchedulerEnabled,
    },
    {
      id: 'facilitator',
      label: 'Facilitator',
      icon: (
        <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-gray-800" viewBox="0 0 24 24" fill="currentColor">
          <path d="M12 1a9 9 0 0 0-9 9v7c0 1.66 1.34 3 3 3h1v-8H5v-2a7 7 0 0 1 14 0v2h-2v8h1c1.66 0 3-1.34 3-3v-7a9 9 0 0 0-9-9z" />
        </svg>
      ),
      enabled: facilitatorEnabled,
      setEnabled: setFacilitatorEnabled,
    },
    {
      id: 'transcriber',
      label: 'Transcriber',
      icon: (
        <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-gray-800" viewBox="0 0 24 24" fill="currentColor">
          <path d="M14 2H6c-1.1 0-2 .9-2 2v16c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V8l-6-6zm-1 9H8v2h5v-2zm-5 6h5v-2H8v2zm9 1h-3v2h3v1l3-2-3-2v1zM13 9V3.5L18.5 9H13z" />
        </svg>
      ),
      enabled: transcriberEnabled,
      setEnabled: setTranscriberEnabled,
    },
  ];

  const handleToggleAll = () => {
    const anyEnabled = agents.some(agent => agent.enabled);
    const allEnabled = !anyEnabled;
    setSchedulerEnabled(allEnabled);
    setFacilitatorEnabled(allEnabled);
    setTranscriberEnabled(allEnabled);
  };

  const ToggleSwitch = ({ enabled, onChange }) => (
    <button
      type="button"
      role="switch"
      aria-checked={enabled}
      onClick={onChange}
      className={`${
        enabled ? 'bg-[#5887E8]' : 'bg-gray-200'
      } relative inline-flex h-8 w-14 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none`}
    >
      <span
        aria-hidden="true"
        className={`${
          enabled ? 'translate-x-6' : 'translate-x-0'
        } pointer-events-none inline-block h-7 w-7 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out`}
      />
    </button>
  );

  return (
    <div className="bg-[#f8f9fa] flex items-center justify-center min-h-screen font-sans">
      <div className="w-full max-w-sm p-4">
        <h1 className="text-5xl font-bold text-center text-gray-800 mb-8">
          Momentum
        </h1>
        <div className="space-y-3">
          {agents.map((agent) => (
            <div key={agent.id} className="bg-white p-4 rounded-xl border border-gray-200/75 shadow-sm flex justify-between items-center">
              <div className="flex items-center space-x-4">
                {agent.icon}
                <span className="text-xl font-medium text-gray-800">{agent.label}</span>
              </div>
              <ToggleSwitch enabled={agent.enabled} onChange={() => agent.setEnabled(!agent.enabled)} />
            </div>
          ))}
        </div>
        <div className="mt-6 space-y-3">
          <button
            onClick={handleToggleAll}
            className="w-full py-3 px-4 bg-white border border-gray-300 rounded-lg text-gray-800 text-lg font-semibold hover:bg-gray-100 transition-colors"
          >
            Enable/disable all
          </button>
          <button
            onClick={() => setShowTranscript(!showTranscript)}
            className="w-full py-3 px-4 bg-[#5887E8] text-white rounded-lg text-lg font-semibold hover:bg-opacity-90 transition-colors"
          >
            {showTranscript ? 'Hide live transcript' : 'Show live transcript'}
          </button>
        </div>
        {showTranscript && (
          <div className="mt-6 p-4 bg-white rounded-xl border border-gray-200/75 shadow-sm space-y-3 text-sm text-gray-700 animate-fade-in">
            <h3 className="font-semibold text-gray-800 text-base">Live Transcript</h3>
            <p><span className="font-semibold text-[#5887E8]">Alex:</span> Okay, so for the next quarter, we need to focus on user acquisition.</p>
            <p><span className="font-semibold text-green-600">Brenda:</span> I agree. Our current CAC is too high. I've prepared a deck with some ideas on organic growth.</p>
            <p><span className="font-semibold text-[#5887E8]">Alex:</span> Great, let's hear them. The floor is yours, Brenda.</p>
          </div>
        )}
      </div>
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
};