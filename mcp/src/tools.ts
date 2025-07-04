import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";
import { HedgeFundAIClient } from "./client.js";
import {
  GenerateAnalysisTool,
  GetHealthTool,
  GetSystemStatusTool,
  SearchTickersTool,
} from "./types.js";



export class HedgeFundAITools {
  private server: Server;
  private client: HedgeFundAIClient;

  constructor() {
    this.server = new Server({
      name: "hedge-fund-ai-tools",
      version: "1.0.0",
      capabilities: {
        tools: {},
      },
    });

    this.client = new HedgeFundAIClient();

    this.setupToolHandlers();
  }

  private setupToolHandlers() {
    this.server.setRequestHandler(ListToolsRequestSchema, async () => {
      return {
        tools: [
          {
            name: "generate_analysis",
            description:
              "Generate comprehensive hedge fund analysis using multiple AI analysts",
            inputSchema: {
              type: "object",
              properties: {
                tickers: {
                  type: "array",
                  items: { type: "string" },
                  description: "List of stock tickers to analyze"
                },
                start_date: {
                  type: "string",
                  description: "Start date for analysis (YYYY-MM-DD)"
                },
                end_date: {
                  type: "string",
                  description: "End date for analysis (YYYY-MM-DD)"
                },
                initial_cash: {
                  type: "number",
                  description: "Initial cash amount for portfolio"
                },
                margin_requirement: {
                  type: "number",
                  description: "Margin requirement percentage"
                },
                show_reasoning: {
                  type: "boolean",
                  description: "Whether to show detailed reasoning"
                },
                selected_analysts: {
                  type: "array",
                  items: { type: "string" },
                  description: "List of analyst names to use"
                },
                model_name: {
                  type: "string",
                  description: "LLM model name to use"
                },
                model_provider: {
                  type: "string",
                  description: "LLM provider (OpenAI, etc.)"
                }
              },
              required: ["tickers"]
            },
          },
          {
            name: "get_health",
            description: "Check the health status of the hedge fund AI server",
            inputSchema: {
              type: "object",
              properties: {},
              required: []
            },
          },
          {
            name: "get_system_status",
            description:
              "Get comprehensive system status and available endpoints",
            inputSchema: {
              type: "object",
              properties: {},
              required: []
            },
          },
          {
            name: "get_available_analysts",
            description: "Get list of available AI analysts for analysis",
            inputSchema: {
              type: "object",
              properties: {},
              required: []
            },
          },
          {
            name: "search_tickers",
            description: "Search for stock ticker symbols",
            inputSchema: {
              type: "object",
              properties: {
                query: {
                  type: "string",
                  description: "Search query for ticker symbols"
                }
              },
              required: ["query"]
            },
          },
        ],
      };
    });

    this.server.setRequestHandler(
      CallToolRequestSchema,
      async (request: any) => {
        const { name, arguments: args } = request.params;

        switch (name) {
          case "generate_analysis":
            return this.handleGenerateAnalysis(args as GenerateAnalysisTool);

          case "get_health":
            return this.handleGetHealth(args as GetHealthTool);

          case "get_system_status":
            return this.handleGetSystemStatus(args as GetSystemStatusTool);

          case "get_available_analysts":
            return this.handleGetAvailableAnalysts();

          case "search_tickers":
            return this.handleSearchTickers(args as SearchTickersTool);

          default:
            throw new Error(`Unknown tool: ${name}`);
        }
      },
    );
  }

  private async handleGenerateAnalysis(args: GenerateAnalysisTool) {
    try {
      const analysisGenerator = await this.client.generateAnalysis({
        tickers: args.tickers,
        start_date: args.start_date,
        end_date: args.end_date,
        initial_cash: args.initial_cash ?? 100000.0,
        margin_requirement: args.margin_requirement ?? 0.0,
        show_reasoning: args.show_reasoning ?? false,
        selected_analysts: args.selected_analysts,
        model_name: args.model_name ?? "gpt-4o",
        model_provider: args.model_provider ?? "OpenAI",
      });

      const results: any[] = [];
      for await (const response of analysisGenerator) {
        results.push(response);
      }

      return {
        content: [
          {
            type: "text",
            text: JSON.stringify(results, null, 2),
          },
        ],
      };
    } catch (error) {
      return {
        content: [
          {
            type: "text",
            text: `Error generating analysis: ${error instanceof Error ? error.message : "Unknown error"}`,
          },
        ],
      };
    }
  }

  private async handleGetHealth(args: GetHealthTool) {
    try {
      const health = await this.client.getHealth();
      return {
        content: [
          {
            type: "text",
            text: JSON.stringify(health, null, 2),
          },
        ],
      };
    } catch (error) {
      return {
        content: [
          {
            type: "text",
            text: `Error getting health status: ${error instanceof Error ? error.message : "Unknown error"}`,
          },
        ],
      };
    }
  }

  private async handleGetSystemStatus(args: GetSystemStatusTool) {
    try {
      const status = await this.client.getSystemStatus();
      return {
        content: [
          {
            type: "text",
            text: JSON.stringify(status, null, 2),
          },
        ],
      };
    } catch (error) {
      return {
        content: [
          {
            type: "text",
            text: `Error getting system status: ${error instanceof Error ? error.message : "Unknown error"}`,
          },
        ],
      };
    }
  }

  private async handleGetAvailableAnalysts() {
    try {
      const analysts = await this.client.getAvailableAnalysts();
      return {
        content: [
          {
            type: "text",
            text: JSON.stringify(analysts, null, 2),
          },
        ],
      };
    } catch (error) {
      return {
        content: [
          {
            type: "text",
            text: `Error getting available analysts: ${error instanceof Error ? error.message : "Unknown error"}`,
          },
        ],
      };
    }
  }

  private async handleSearchTickers(args: SearchTickersTool) {
    try {
      const tickers = await this.client.searchTickers(args.query);
      // Validate the response using the schema
      const { TickerSearchResultsSchema } = await import("./types.js");
      const validated = TickerSearchResultsSchema.parse(tickers);
      return {
        content: [
          {
            type: "text",
            text: JSON.stringify(validated, null, 2),
          },
        ],
      };
    } catch (error) {
      return {
        content: [
          {
            type: "text",
            text: `Error searching tickers: ${error instanceof Error ? error.message : "Unknown error"}`,
          },
        ],
      };
    }
  }

  async run() {
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
    console.error("Hedge Fund AI MCP server started");
  }
}

// Start the server if this file is run directly
if (import.meta.url === `file://${process.argv[1]}`) {
  const tools = new HedgeFundAITools();
  tools.run().catch(console.error);
}
