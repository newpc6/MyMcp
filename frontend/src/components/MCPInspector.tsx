import React, { useState, useEffect } from 'react';
import { Card, CardContent } from './ui/card';
import { Tabs, TabsList, TabsTrigger, TabsContent } from './ui/tabs';
import { Input } from './ui/input';
import { Button } from './ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';

interface Tool {
  name: string;
  description: string;
  inputSchema: any;
}

interface ConnectionConfig {
  url: string;
  transportType: 'sse' | 'stdio';
  bearerToken?: string;
}

const MCPInspector: React.FC = () => {
  const [connected, setConnected] = useState(false);
  const [tools, setTools] = useState<Tool[]>([]);
  const [selectedTool, setSelectedTool] = useState<Tool | null>(null);
  const [config, setConfig] = useState<ConnectionConfig>({
    url: 'http://localhost:3000/sse',
    transportType: 'sse'
  });
  const [history, setHistory] = useState<any[]>([]);

  const handleConnect = async () => {
    try {
      // 实现连接逻辑
      const response = await fetch(config.url);
      if (response.ok) {
        setConnected(true);
        // 获取工具列表
        const toolsResponse = await fetch(`${config.url}/tools/list`);
        const toolsData = await toolsResponse.json();
        setTools(toolsData.tools || []);
      }
    } catch (error) {
      console.error('Connection failed:', error);
    }
  };

  const handleDisconnect = () => {
    setConnected(false);
    setTools([]);
    setSelectedTool(null);
  };

  const handleToolCall = async (toolName: string, params: any) => {
    try {
      const response = await fetch(`${config.url}/tools/call`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(config.bearerToken && { 'Authorization': `Bearer ${config.bearerToken}` })
        },
        body: JSON.stringify({
          method: 'tools/call',
          params: {
            name: toolName,
            arguments: params
          },
          jsonrpc: '2.0',
          id: Date.now()
        })
      });

      const result = await response.json();
      setHistory(prev => [...prev, { type: 'tool-call', tool: toolName, params, result }]);
      return result;
    } catch (error) {
      console.error('Tool call failed:', error);
    }
  };

  return (
    <div className="p-4">
      <Card>
        <CardContent className="p-4">
          <h2 className="text-xl font-bold mb-4">MCP Inspector</h2>
          
          <div className="mb-6">
            <h3 className="text-lg font-semibold mb-2">Connection</h3>
            <div className="space-y-4">
              <div className="flex items-center gap-4">
                <Select
                  value={config.transportType}
                  onValueChange={(value: 'sse' | 'stdio') => 
                    setConfig(prev => ({ ...prev, transportType: value }))}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Transport Type" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="sse">SSE</SelectItem>
                    <SelectItem value="stdio">STDIO</SelectItem>
                  </SelectContent>
                </Select>

                <Input
                  placeholder="Server URL"
                  value={config.url}
                  onChange={(e) => setConfig(prev => ({ ...prev, url: e.target.value }))}
                />

                <Input
                  placeholder="Bearer Token (Optional)"
                  type="password"
                  value={config.bearerToken}
                  onChange={(e) => setConfig(prev => ({ ...prev, bearerToken: e.target.value }))}
                />

                <Button
                  onClick={connected ? handleDisconnect : handleConnect}
                  variant={connected ? "destructive" : "default"}
                >
                  {connected ? 'Disconnect' : 'Connect'}
                </Button>
              </div>
            </div>
          </div>

          <Tabs defaultValue="tools" className="w-full">
            <TabsList>
              <TabsTrigger value="tools">Tools</TabsTrigger>
              <TabsTrigger value="history">History</TabsTrigger>
            </TabsList>

            <TabsContent value="tools">
              <div className="grid grid-cols-2 gap-4">
                <div className="border rounded p-4">
                  <h4 className="font-semibold mb-2">Available Tools</h4>
                  <div className="space-y-2">
                    {tools.map(tool => (
                      <div
                        key={tool.name}
                        className={`p-2 border rounded cursor-pointer ${
                          selectedTool?.name === tool.name ? 'bg-blue-100' : ''
                        }`}
                        onClick={() => setSelectedTool(tool)}
                      >
                        <div className="font-medium">{tool.name}</div>
                        <div className="text-sm text-gray-600">{tool.description}</div>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="border rounded p-4">
                  <h4 className="font-semibold mb-2">Tool Inspector</h4>
                  {selectedTool ? (
                    <div>
                      <h5 className="font-medium">{selectedTool.name}</h5>
                      <p className="text-sm text-gray-600 mb-4">{selectedTool.description}</p>
                      {/* 这里可以添加工具参数输入表单 */}
                    </div>
                  ) : (
                    <p className="text-gray-500">Select a tool to inspect</p>
                  )}
                </div>
              </div>
            </TabsContent>

            <TabsContent value="history">
              <div className="border rounded p-4">
                <h4 className="font-semibold mb-2">Request History</h4>
                <div className="space-y-2">
                  {history.map((item, index) => (
                    <div key={index} className="border rounded p-2">
                      <div className="font-medium">{item.type}</div>
                      <pre className="text-sm bg-gray-50 p-2 mt-1 rounded">
                        {JSON.stringify(item, null, 2)}
                      </pre>
                    </div>
                  ))}
                </div>
              </div>
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>
    </div>
  );
};

export default MCPInspector; 