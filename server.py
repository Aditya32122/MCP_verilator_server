import os
import re
import shutil
import subprocess
import sys
import uuid
from typing import Dict, Any
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Verilator Compilation Server")

def find_verilator_path():
    """
    Find Verilator executable in system PATH
    
    Returns:
    str: Path to Verilator executable or None if not found
    """
    possible_paths = [
        "/usr/local/bin/verilator",
        "/usr/bin/verilator",
        "/opt/local/bin/verilator",
        shutil.which("verilator")
    ]
    
    for path in possible_paths:
        if path and os.path.exists(path) and os.access(path, os.X_OK):
            return path
    
    return None

@mcp.tool()
async def verilog_compilation(verilog_code: str) -> Dict[str, Any]:
    """
    Compile Verilog code using Verilator.
    
    Args:
    verilog_code (str): Verilog source code to compile
    
    Returns:
    Compilation result dictionary
    """
    # Find Verilator executable
    verilator_path = find_verilator_path()
    if not verilator_path:
        return {
            "status": "error", 
            "output": "Verilator executable not found. Please install Verilator.",
            "error_code": 127
        }
    
    # Create temporary directory for compilation
    os.makedirs("temp_verilog", exist_ok=True)
    
    # Extract module name from Verilog code
    module_match = re.search(r'module\s+(\w+)', verilog_code)
    module_name = module_match.group(1) if module_match else f"test_{uuid.uuid4().hex}"
    
    # Generate filename using module name
    filename = f"{module_name}.v"
    file_path = os.path.join("temp_verilog", filename)
    
    try:
        # Write Verilog code to file
        with open(file_path, 'w') as f:
            f.write(verilog_code + "\n")
        
        verilator_cmd = [
            verilator_path, 
            "--cc",          # Generate C++ code
            file_path,       # Input Verilog file
            "--build",       # Compile generated C++
            "-Wall",         # All warnings
            "-Wno-DECLFILENAME",  # Disable DECLFILENAME warning
            "--Mdir", "temp_verilog"  # Output directory
        ]
        
        # Run Verilator
        result = subprocess.run(
            verilator_cmd, 
            capture_output=True, 
            text=True
        )
        
        # Detailed error handling
        if result.returncode == 0:
            return {
                "status": "success", 
                "output": result.stdout,
                "file_path": file_path
            }
        else:
            return {
                "status": "error", 
                "output": f"Stderr: {result.stderr}\nStdout: {result.stdout}",
                "error_code": result.returncode,
                "command": " ".join(verilator_cmd)
            }
    
    except Exception as e:
        return {
            "status": "error", 
            "output": f"Exception: {str(e)}",
            "file_path": file_path
        }
    
    finally:
        try:
            import glob
            # Remove the generated files if they exist
            for ext in ['.v', '.cpp', '.h'] + [f'V{module_name}*']:
                for temp_file in glob.glob(os.path.join("temp_verilog", ext)):
                    try:
                        os.remove(temp_file)
                    except:
                        pass
        except Exception as cleanup_error:
            print(f"Cleanup error: {cleanup_error}", file=sys.stderr)

def main():
    """Run MCP server"""
    print("Starting Verilog Compilation Server...", file=sys.stderr)
    mcp.run(transport='stdio')

if __name__ == "__main__":
    main()