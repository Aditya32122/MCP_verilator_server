from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client

# Create server parameters for stdio connection
server_params = StdioServerParameters(
    command="python",  # Executable
    args=["verilog_compilation_server.py"], 
    env=None  # Optional environment variables
)

# Optional sampling callback (can be customized or left as a placeholder)
async def handle_sampling_message(
    message: types.CreateMessageRequestParams,
) -> types.CreateMessageResult:
    return types.CreateMessageResult(
        role="assistant",
        content=types.TextContent(
            type="text",
            text="Verilog Compilation Server",
        ),
        model="verilog-compiler",
        stopReason="endTurn",
    )

async def run():

    async with stdio_client(server_params) as (read, write):
        # Create client session
        async with ClientSession(
            read, write, sampling_callback=handle_sampling_message
        ) as session:
            # Initialize the connection
            await session.initialize()

            
            tools = await session.list_tools()
            print("Available tools:", tools)

            # Verilog code to compile
            verilog_code = "module and_gate(input a, input b, output y);  assign y = a & b; endmodule"

            try:
               
                result = await session.call_tool(
                    "verilog_compilation", 
                    arguments={"verilog_code": verilog_code}
                )
                
                print("Compilation Result:")
                print(result)

                # If result is a list of content, extract the text
                if isinstance(result, list) and result and hasattr(result[0], 'text'):
                    print("\nCompilation Details:")
                    print(result[0].text)

            except Exception as e:
                print(f"Error calling Verilog compilation tool: {e}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(run())