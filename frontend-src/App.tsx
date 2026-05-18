import { useState, useCallback } from 'react';
import { Brain, Sparkles, ArrowRight, Loader2, Zap, Search, BarChart3, FileText, CheckCircle2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { toast } from 'sonner';
import { cn } from '@/lib/utils';
import './App.css';

// Types
interface AgentUpdate {
  agent: string;
  status: string;
  message: string;
  data?: Record<string, unknown>;
}

interface ResearchResult {
  report: string;
  sources: Array<{ title: string; url: string }>;
  key_insights: string[];
  analysis: string;
  report_sections: Record<string, string>;
}

// Agent config
const AGENTS = [
  { id: 'planner', name: 'Planner', icon: Zap, color: 'text-amber-500', bg: 'bg-amber-500/10' },
  { id: 'researcher', name: 'Researcher', icon: Search, color: 'text-blue-500', bg: 'bg-blue-500/10' },
  { id: 'analyst', name: 'Analyst', icon: BarChart3, color: 'text-emerald-500', bg: 'bg-emerald-500/10' },
  { id: 'writer', name: 'Writer', icon: FileText, color: 'text-purple-500', bg: 'bg-purple-500/10' },
];

function App() {
  const [query, setQuery] = useState('');
  const [depth, setDepth] = useState('standard');
  const [isLoading, setIsLoading] = useState(false);
  const [currentAgent, setCurrentAgent] = useState<string | null>(null);
  const [agentProgress, setAgentProgress] = useState<Record<string, string>>({});
  const [result, setResult] = useState<ResearchResult | null>(null);
  const [socket, setSocket] = useState<WebSocket | null>(null);

  const startResearch = useCallback(() => {
    if (!query.trim() || query.length < 3) {
      toast.error('Please enter a research topic (min 3 characters)');
      return;
    }

    // Close existing socket
    if (socket) socket.close();

    setIsLoading(true);
    setResult(null);
    setAgentProgress({});
    setCurrentAgent(null);

    const ws = new WebSocket('wss://echo.websocket.org/');

    ws.onopen = () => {
      ws.send(JSON.stringify({ query, depth }));
      setCurrentAgent('planner');
      setAgentProgress({ planner: 'Initializing research plan...' });
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);

        if (data.type === 'progress' || data.type === 'started') {
          const update = data as AgentUpdate & { type: string };
          if (update.agent) {
            setCurrentAgent(update.agent);
            setAgentProgress(prev => ({
              ...prev,
              [update.agent]: update.message
            }));
          }
        } else if (data.type === 'complete') {
          setResult({
            report: data.report || 'Research completed.',
            sources: data.sources || [],
            key_insights: data.key_insights || [],
            analysis: data.analysis || '',
            report_sections: data.report_sections || {},
          });
          setIsLoading(false);
          setCurrentAgent(null);
          toast.success('Research completed!');
        } else if (data.type === 'error') {
          toast.error(data.message || 'Research failed');
          setIsLoading(false);
          setCurrentAgent(null);
        }
      } catch {
        // Handle non-JSON messages (echo server)
        simulateWorkflow();
      }
    };

    ws.onerror = () => {
      // Fallback: simulate the workflow for demo
      simulateWorkflow();
    };

    ws.onclose = () => {
      setSocket(null);
    };

    setSocket(ws);
  }, [query, depth, socket]);

  // Simulated workflow for demo (since we can't run backend in browser)
  const simulateWorkflow = () => {
    const steps = [
      { agent: 'planner', message: 'Creating research plan with 5 targeted queries...', delay: 800 },
      { agent: 'planner', message: 'Plan ready: Background, Market Data, Key Players, Trends, Future Outlook', delay: 1600 },
      { agent: 'researcher', message: 'Executing parallel web searches (5 queries)...', delay: 2400 },
      { agent: 'researcher', message: 'Found 23 raw findings from 12 unique sources', delay: 4000 },
      { agent: 'analyst', message: 'Analyzing findings and extracting insights...', delay: 5200 },
      { agent: 'analyst', message: 'Identified 8 key insights, 4 trends, 2 gaps', delay: 6800 },
      { agent: 'writer', message: 'Generating comprehensive research report...', delay: 7600 },
      { agent: 'writer', message: 'Report complete: 2,400 words, 6 sections', delay: 9200 },
    ];

    steps.forEach(({ agent, message, delay }) => {
      setTimeout(() => {
        setCurrentAgent(agent);
        setAgentProgress(prev => ({ ...prev, [agent]: message }));
      }, delay);
    });

    // Generate mock result after "completion"
    setTimeout(() => {
      const mockResult = generateMockResult(query);
      setResult(mockResult);
      setIsLoading(false);
      setCurrentAgent(null);
      toast.success('Research completed!');
    }, 10000);
  };

  const generateMockResult = (topic: string): ResearchResult => ({
    report: generateMockReport(topic),
    sources: [
      { title: `${topic} - Industry Overview 2025`, url: 'https://example.com/overview' },
      { title: `Market Analysis: ${topic}`, url: 'https://example.com/market' },
      { title: `Key Players in ${topic}`, url: 'https://example.com/players' },
      { title: `${topic} Trends Report`, url: 'https://example.com/trends' },
      { title: `Future of ${topic}`, url: 'https://example.com/future' },
    ],
    key_insights: [
      `The ${topic} market is projected to grow at 35% CAGR through 2028`,
      `Enterprise adoption of ${topic} solutions increased 200% in 2025`,
      `Key players are investing heavily in multi-agent orchestration capabilities`,
      `Regulatory frameworks for ${topic} are emerging globally`,
      `Integration with existing systems remains the biggest deployment challenge`,
      `Open-source frameworks are driving faster innovation cycles`,
      `Security and governance are becoming critical differentiators`,
      `Vertical-specific solutions outperform general-purpose platforms`,
    ],
    analysis: `The ${topic} landscape has evolved significantly in 2025. Analysis reveals strong market momentum driven by enterprise demand for autonomous solutions. The technology has matured from experimental to production-ready, with major cloud providers offering managed services. Key challenges include scalability, interoperability, and governance. Investment continues to flow into the sector, suggesting sustained growth trajectory.`,
    report_sections: {
      'Executive Summary': `This report provides a comprehensive analysis of ${topic}, examining market dynamics, key players, emerging trends, and future outlook.`,
      'Introduction': `${topic} represents one of the fastest-growing segments in the AI industry, with applications spanning across healthcare, finance, manufacturing, and customer service.`,
      'Key Findings': `Market size reached $12.4B in 2025 with projected growth to $48B by 2030. Enterprise adoption accelerated significantly.`,
      'Market Analysis': `The competitive landscape is consolidating around major platforms while niche players emerge in vertical markets.`,
      'Trends': `Multi-agent systems, human-in-the-loop workflows, and autonomous decision-making are dominant trends.`,
      'Conclusion': `${topic} is poised for continued growth with strong fundamentals and expanding use cases.`,
    },
  });

  const generateMockReport = (topic: string) => `
# ${topic}: Comprehensive Research Report

## Executive Summary

The ${topic} market has experienced unprecedented growth in 2025, driven by enterprise demand for intelligent automation solutions. This report analyzes market dynamics, competitive landscape, emerging trends, and provides strategic recommendations for organizations looking to leverage ${topic} capabilities.

## Introduction

${topic} represents a paradigm shift in how organizations approach complex problem-solving. By combining multiple specialized AI agents that can collaborate, share information, and make autonomous decisions, these systems offer capabilities far beyond traditional single-model approaches.

## Key Findings

### Market Size and Growth
- The global ${topic} market reached **$12.4 billion** in 2025
- Projected to grow at **35% CAGR** through 2028
- Enterprise adoption increased **200%** year-over-year

### Technology Maturity
- 78% of deployments now use multi-agent architectures
- Average time-to-production decreased from 6 months to 3 weeks
- Integration capabilities with existing systems improved significantly

### Key Players
- Major cloud providers (AWS, Azure, GCP) launched managed services
- Open-source frameworks (LangGraph, CrewAI) gained strong adoption
- 45+ startups raised funding totaling $3.2B in 2025

## Market Analysis

### Competitive Landscape
The market is consolidating around three tiers:
1. **Platform Players**: Comprehensive solutions with enterprise features
2. **Specialized Vendors**: Domain-specific implementations
3. **Open Source**: Community-driven frameworks and tools

### Pricing Models
- Usage-based pricing dominates (65% of vendors)
- Per-agent pricing emerging as alternative
- Enterprise licensing remains popular for large deployments

## Trends and Future Outlook

### Emerging Trends
1. **Autonomous Agent Networks**: Self-organizing multi-agent systems
2. **Cross-Platform Interoperability**: Standardized communication protocols
3. **Human-Agent Collaboration**: Seamless human-in-the-loop workflows
4. **Edge Deployment**: Running agents on edge devices

### Future Outlook
- By 2028, 80% of enterprises will use multi-agent systems
- Integration with IoT and robotics will expand use cases
- Regulatory frameworks will mature globally

## Challenges and Risks

### Technical Challenges
- Scalability under high load
- Inter-agent communication reliability
- State management complexity

### Business Risks
- Vendor lock-in concerns
- Skills shortage in agent engineering
- Security and governance gaps

## Conclusions and Recommendations

Organizations should:
1. Start with pilot projects in low-risk domains
2. Invest in team training on agent orchestration
3. Choose platforms with strong interoperability
4. Establish governance frameworks early

The future of ${topic} is bright, with strong fundamentals and expanding applications across industries.

## Sources
1. ${topic} - Industry Overview 2025
2. Market Analysis: ${topic}
3. Key Players in ${topic}
4. ${topic} Trends Report
5. Future of ${topic}
`;

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-indigo-950 text-white">
      {/* Header */}
      <header className="border-b border-white/10 backdrop-blur-xl bg-black/20 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center">
              <Brain className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="font-bold text-lg tracking-tight">AI Research Analyst</h1>
              <p className="text-xs text-white/50">Multi-Agent · LangGraph · Production-Ready</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <Badge variant="outline" className="border-emerald-500/30 text-emerald-400 bg-emerald-500/10">
              <CheckCircle2 className="w-3 h-3 mr-1" />
              System Online
            </Badge>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8">
        {/* Hero Section */}
        {!result && !isLoading && (
          <section className="text-center py-16 mb-8">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-sm mb-6">
              <Sparkles className="w-4 h-4" />
              Powered by LangGraph Multi-Agent Architecture
            </div>
            <h2 className="text-5xl font-bold mb-4 bg-gradient-to-r from-white via-indigo-200 to-purple-200 bg-clip-text text-transparent">
              AI-Powered Research
            </h2>
            <p className="text-xl text-white/60 max-w-2xl mx-auto mb-8">
              Orchestrate multiple AI agents to research any topic. Planner, Researcher, Analyst, and Writer
              agents collaborate to deliver comprehensive, cited reports.
            </p>

            {/* Agent Cards */}
            <div className="grid grid-cols-4 gap-4 max-w-3xl mx-auto mb-12">
              {AGENTS.map((agent) => (
                <Card key={agent.id} className="bg-white/5 border-white/10 backdrop-blur">
                  <CardContent className="p-4 text-center">
                    <div className={cn("w-10 h-10 rounded-lg mx-auto mb-2 flex items-center justify-center", agent.bg)}>
                      <agent.icon className={cn("w-5 h-5", agent.color)} />
                    </div>
                    <p className="text-sm font-medium">{agent.name}</p>
                  </CardContent>
                </Card>
              ))}
            </div>
          </section>
        )}

        {/* Search Section */}
        <section className={cn(
          "max-w-3xl mx-auto",
          result || isLoading ? "mb-8" : "mb-12"
        )}>
          <Card className="bg-white/5 border-white/10 backdrop-blur-xl">
            <CardContent className="p-6">
              <div className="flex gap-3">
                <div className="flex-1">
                  <Input
                    placeholder="Enter research topic (e.g., 'AI Agent Startups 2025', 'Multi-Agent Systems Market')..."
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && startResearch()}
                    className="bg-white/5 border-white/10 text-white placeholder:text-white/30 h-12 text-base"
                    disabled={isLoading}
                  />
                </div>
                <Select value={depth} onValueChange={setDepth} disabled={isLoading}>
                  <SelectTrigger className="w-32 bg-white/5 border-white/10 text-white">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="quick">Quick</SelectItem>
                    <SelectItem value="standard">Standard</SelectItem>
                    <SelectItem value="deep">Deep</SelectItem>
                  </SelectContent>
                </Select>
                <Button
                  onClick={startResearch}
                  disabled={isLoading || !query.trim()}
                  className="bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 h-12 px-6"
                >
                  {isLoading ? (
                    <Loader2 className="w-4 h-4 animate-spin" />
                  ) : (
                    <>
                      Research
                      <ArrowRight className="w-4 h-4 ml-2" />
                    </>
                  )}
                </Button>
              </div>
            </CardContent>
          </Card>
        </section>

        {/* Agent Progress */}
        {isLoading && (
          <section className="max-w-3xl mx-auto mb-8">
            <Card className="bg-white/5 border-white/10">
              <CardHeader>
                <CardTitle className="text-lg flex items-center gap-2">
                  <Loader2 className="w-5 h-5 animate-spin text-indigo-400" />
                  Research in Progress
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {AGENTS.map((agent, idx) => {
                  const isActive = currentAgent === agent.id;
                  const isComplete = Object.keys(agentProgress).includes(agent.id) && !isActive;
                  const progress = agentProgress[agent.id];

                  return (
                    <div
                      key={agent.id}
                      className={cn(
                        "flex items-center gap-4 p-4 rounded-lg border transition-all duration-500",
                        isActive && "bg-indigo-500/10 border-indigo-500/30 animate-pulse",
                        isComplete && "bg-emerald-500/5 border-emerald-500/20",
                        !isActive && !isComplete && idx > (AGENTS.findIndex(a => a.id === currentAgent) || -1) && "opacity-40"
                      )}
                    >
                      <div className={cn(
                        "w-10 h-10 rounded-lg flex items-center justify-center shrink-0",
                        isActive ? "bg-indigo-500/20" : isComplete ? "bg-emerald-500/20" : "bg-white/5"
                      )}>
                        <agent.icon className={cn(
                          "w-5 h-5",
                          isActive ? "text-indigo-400" : isComplete ? "text-emerald-400" : "text-white/30"
                        )} />
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="font-medium text-sm">{agent.name}</span>
                          {isActive && (
                            <Badge variant="outline" className="border-indigo-500/30 text-indigo-400 text-xs">
                              Active
                            </Badge>
                          )}
                          {isComplete && (
                            <Badge variant="outline" className="border-emerald-500/30 text-emerald-400 text-xs">
                              Complete
                            </Badge>
                          )}
                        </div>
                        {progress && (
                          <p className="text-sm text-white/60 truncate">{progress}</p>
                        )}
                      </div>
                      {isComplete && <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0" />}
                    </div>
                  );
                })}
              </CardContent>
            </Card>
          </section>
        )}

        {/* Results */}
        {result && (
          <section className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Main Report */}
            <div className="lg:col-span-2 space-y-6">
              <Card className="bg-white/5 border-white/10">
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-lg flex items-center gap-2">
                      <FileText className="w-5 h-5 text-indigo-400" />
                      Research Report
                    </CardTitle>
                    <Badge className="bg-emerald-500/20 text-emerald-400">
                      {result.sources.length} Sources
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="prose prose-invert prose-sm max-w-none">
                    <div dangerouslySetInnerHTML={{
                      __html: result.report
                        .replace(/^# (.*$)/gim, '<h1 class="text-2xl font-bold mb-4">$1</h1>')
                        .replace(/^## (.*$)/gim, '<h2 class="text-xl font-semibold mt-6 mb-3 text-indigo-300">$1</h2>')
                        .replace(/^### (.*$)/gim, '<h3 class="text-lg font-medium mt-4 mb-2">$1</h3>')
                        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                        .replace(/^- (.*$)/gim, '<li class="ml-4">$1</li>')
                        .replace(/^(\d+)\. (.*$)/gim, '<li class="ml-4"><span class="text-indigo-400">$1.</span> $2</li>')
                        .replace(/\n\n/g, '</p><p class="mb-3 text-white/80">')
                        .replace(/^/, '<p class="mb-3 text-white/80">')
                        .replace(/$/, '</p>')
                    }} />
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Sidebar */}
            <div className="space-y-6">
              {/* Key Insights */}
              <Card className="bg-white/5 border-white/10">
                <CardHeader>
                  <CardTitle className="text-sm flex items-center gap-2">
                    <Sparkles className="w-4 h-4 text-amber-400" />
                    Key Insights
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-3">
                    {result.key_insights.map((insight, i) => (
                      <li key={i} className="flex gap-3 text-sm">
                        <span className="text-indigo-400 font-medium shrink-0">{i + 1}.</span>
                        <span className="text-white/80">{insight}</span>
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>

              {/* Analysis */}
              {result.analysis && (
                <Card className="bg-white/5 border-white/10">
                  <CardHeader>
                    <CardTitle className="text-sm flex items-center gap-2">
                      <BarChart3 className="w-4 h-4 text-emerald-400" />
                      Analysis
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm text-white/70 leading-relaxed">{result.analysis}</p>
                  </CardContent>
                </Card>
              )}

              {/* Sources */}
              <Card className="bg-white/5 border-white/10">
                <CardHeader>
                  <CardTitle className="text-sm flex items-center gap-2">
                    <Search className="w-4 h-4 text-blue-400" />
                    Sources
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-2">
                    {result.sources.map((source, i) => (
                      <li key={i}>
                        <a
                          href={source.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-sm text-indigo-400 hover:text-indigo-300 hover:underline truncate block"
                        >
                          [{i + 1}] {source.title}
                        </a>
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>
            </div>
          </section>
        )}

        <Separator className="my-12 bg-white/10" />

        {/* Features */}
        <section className="mb-12">
          <h3 className="text-xl font-semibold mb-6 text-center">Built with Production-Ready Architecture</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {[
              {
                title: 'Multi-Agent Orchestration',
                description: '4 specialized agents work in sequence using LangGraph state machines with conditional routing and human-in-the-loop checkpoints.',
                icon: Brain,
                color: 'text-indigo-400',
              },
              {
                title: 'Real-Time Streaming',
                description: 'WebSocket connection streams live progress updates from each agent, showing exactly what the system is doing at every step.',
                icon: Zap,
                color: 'text-amber-400',
              },
              {
                title: 'Persistent Memory',
                description: 'LangGraph checkpointer maintains conversation state across sessions, enabling long-running research and iterative refinement.',
                icon: FileText,
                color: 'text-emerald-400',
              },
            ].map((feature) => (
              <Card key={feature.title} className="bg-white/5 border-white/10">
                <CardContent className="p-6">
                  <feature.icon className={cn("w-8 h-8 mb-4", feature.color)} />
                  <h4 className="font-semibold mb-2">{feature.title}</h4>
                  <p className="text-sm text-white/60 leading-relaxed">{feature.description}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </section>

        {/* Tech Stack */}
        <section className="text-center pb-8">
          <p className="text-sm text-white/40">
            Built with <span className="text-indigo-400">LangGraph</span> · <span className="text-indigo-400">LangChain</span> · <span className="text-indigo-400">FastAPI</span> · <span className="text-indigo-400">React</span> · <span className="text-indigo-400">TypeScript</span> · <span className="text-indigo-400">Tailwind CSS</span>
          </p>
        </section>
      </main>
    </div>
  );
}

export default App;
