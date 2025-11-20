import React from 'react';

interface AgentStatusProps {
    agent: string;
    status: string;
    step: string;
    isVisible: boolean;
}

const AgentStatus: React.FC<AgentStatusProps> = ({ agent, status, step, isVisible }) => {
    if (!isVisible) return null;

    return (
        <div className="fixed bottom-24 left-1/2 transform -translate-x-1/2 z-50" data-step={step}>
            <div className="bg-white/90 backdrop-blur-md border border-gray-200 shadow-lg rounded-full px-6 py-3 flex items-center gap-3 animate-fade-in-up">
                <div className="relative">
                    <div className="w-3 h-3 bg-blue-500 rounded-full animate-pulse"></div>
                    <div className="absolute top-0 left-0 w-3 h-3 bg-blue-500 rounded-full animate-ping opacity-75"></div>
                </div>
                <div className="flex flex-col">
                    <span className="text-xs font-semibold text-blue-600 uppercase tracking-wider">{agent}</span>
                    <span className="text-sm text-gray-700 font-medium">{status}</span>
                </div>
            </div>
        </div>
    );
};

export default AgentStatus;
