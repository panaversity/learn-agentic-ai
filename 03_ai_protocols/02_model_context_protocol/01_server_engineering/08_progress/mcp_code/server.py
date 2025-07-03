import asyncio
import logging
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.server import Context

# Setup logging for our console
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create MCP server - FastMCP automatically supports progress via Context
mcp = FastMCP("Simple Progress Server", stateless_http=False)

@mcp.tool()
async def download_file(filename: str, size_mb: int, ctx: Context) -> str:
    """
    Simulate downloading a file with progress tracking.
    
    Args:
        filename: Name of the file to download
        size_mb: Size of the file in MB (determines duration)
        ctx: MCP context for progress reporting
    """
    await ctx.info(f"Starting download of {filename} ({size_mb}MB)")
    
    # Simulate download with progress updates
    total_chunks = size_mb * 10  # 10 chunks per MB
    
    for chunk in range(total_chunks + 1):
        # Calculate progress
        progress = chunk
        percentage = (chunk / total_chunks) * 100
        
        # Report progress
        await ctx.report_progress(
            progress=progress,
            total=total_chunks,
            message=f"Downloading {filename}... {percentage:.1f}%"
        )
        
        # Simulate work (faster for demo)
        await asyncio.sleep(0.1)
    
    await ctx.info(f"Download completed: {filename}")
    return f"Successfully downloaded {filename} ({size_mb}MB)"

@mcp.tool()
async def process_data(records: int, ctx: Context) -> str:
    """
    Simulate processing data records with progress tracking.
    
    Args:
        records: Number of records to process
        ctx: MCP context for progress reporting
    """
    await ctx.info(f"Starting to process {records} records")
    
    for i in range(records + 1):
        # Report progress with descriptive messages
        if i == 0:
            message = "Initializing data processor..."
        elif i < records // 4:
            message = "Loading and validating records..."
        elif i < records // 2:
            message = "Applying transformations..."
        elif i < records * 3 // 4:
            message = "Running calculations..."
        else:
            message = "Finalizing results..."
            
        await ctx.report_progress(
            progress=i,
            total=records,
            message=message
        )
        
        # Simulate processing time
        await asyncio.sleep(0.05)
    
    await ctx.info(f"Processing completed: {records} records")
    return f"Successfully processed {records} records"

# Create the streamable HTTP app
mcp_app = mcp.streamable_http_app()

if __name__ == "__main__":
    import uvicorn    
    uvicorn.run(mcp_app, host="0.0.0.0", port=8000) 