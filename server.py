
import os
import subprocess
import sys
import json
from typing import Any, Dict
from mcp.server.fastmcp import FastMCP
import uuid
import re

mcp = FastMCP("Verilator for Verilog Simulation")

@mcp.tool()
async def verilog_compilation(verilog_code: str) -> Dict[str, Any]:
    """
    Compile Verilog code using Verilator.
    
    Args:
    verilog_code (str): Verilog source code to compile
    
    Returns:
    Dict containing compilation status and output
    """
    # Clean and parse the input
    if isinstance(verilog_code, str):

        verilog_code = verilog_code.strip('"')
        
      
        verilog_code = verilog_code.rstrip('\\')
        
       
        verilog_code = verilog_code.replace('\\n', '\n')
    
    
    verilog_code = verilog_code.rstrip() + "\n"
    
   
    os.makedirs("temp_verilog", exist_ok=True)
    

    verilog_filename = f"test_{uuid.uuid4().hex}.v"
    verilog_file_path = os.path.join("temp_verilog", verilog_filename)
    
    try:
       
        with open(verilog_file_path, "w") as verilog_file:
            verilog_file.write(verilog_code)
        
        verilator_cmd = [
            "verilator",
            "--cc",
            verilog_file_path,
            "--build",
            "--Mdir", "temp_verilog",
            "-Wall",  
            "--error-limit", "10"  
        ]
        
        result = subprocess.run(
            verilator_cmd,
            capture_output=True,
            text=True,
            check=True
        )
        
        return {
            "status": "success",
            "output": result.stdout,
            "file_path": verilog_file_path
        }
    
    except subprocess.CalledProcessError as e:
        return {
            "status": "error",
            "output": e.stderr,
            "error_code": e.returncode
        }
    
    except Exception as e:
        return {
            "status": "error",
            "output": str(e)
        }
    
    finally:
        # Optional: Clean up temporary files
        try:
            if os.path.exists(verilog_file_path):
                os.remove(verilog_file_path)
        except Exception:
            pass

def main():
    """
    Main entry point for the MCP server.
   
    """
    print("Starting Verilog Compilation MCP Server...", file=sys.stderr)
    
    try:
        mcp.run(transport='stdio')
    except Exception as e:
        print(f"Server error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()