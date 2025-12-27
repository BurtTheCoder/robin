"use client";

import { SubAgentBadge, AgentType, AgentStatus } from "./SubAgentBadge";

export interface SubAgentResult {
  id: string;
  agentType: AgentType;
  status: AgentStatus;
  analysis?: string;
  startedAt: Date;
  completedAt?: Date;
}

interface SubAgentResultsProps {
  results: SubAgentResult[];
}

export function SubAgentResults({ results }: SubAgentResultsProps) {
  if (results.length === 0) {
    return (
      <div className="text-center py-4">
        <p className="text-sm text-muted-foreground">No sub-agent analysis yet</p>
      </div>
    );
  }

  // Sort by startedAt, most recent first
  const sortedResults = [...results].sort(
    (a, b) => new Date(b.startedAt).getTime() - new Date(a.startedAt).getTime()
  );

  return (
    <div className="space-y-2">
      {sortedResults.map((result) => (
        <SubAgentBadge
          key={result.id}
          agentType={result.agentType}
          status={result.status}
          analysis={result.analysis}
        />
      ))}
    </div>
  );
}
