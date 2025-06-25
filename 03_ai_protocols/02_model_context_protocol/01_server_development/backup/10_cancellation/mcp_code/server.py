#!/usr/bin/env python3
"""
MCP Server demonstrating proper cancellation using MCP's built-in capabilities.

This shows how to build cancellable tools that work with MCP's native request management,
rather than manually tracking tasks.
"""

import asyncio
import time
from typing import Dict, Any

from mcp.server.fastmcp import FastMCP, Context

# Create the FastMCP server
server = FastMCP("Cancellation Demo Server")

# Simple storage for demonstration (in production, use proper state management)
operation_status: Dict[str, str] = {}

@server.tool()
async def process_large_file(
    filename: str, 
    processing_time: int = 10,
    ctx: Context = None
) -> str:
    """
    Simulate processing a large file with progress reporting.
    This operation can be cancelled via asyncio cancellation.
    
    Args:
        filename: Name of the file to process
        processing_time: How long to simulate processing (seconds)
        ctx: MCP context (injected automatically)
    """
    if ctx:
        request_id = ctx.request_id
        await ctx.info(f"Starting to process {filename} (Request: {request_id})")
        operation_status[request_id] = "processing"
    
    try:
        # Simulate long-running operation with progress updates
        for i in range(processing_time):
            # Check if we should cancel (asyncio will raise CancelledError)
            await asyncio.sleep(1)
            
            if ctx:
                progress = ((i + 1) / processing_time) * 100
                await ctx.report_progress(progress, 100, f"Processing {filename}... {i+1}/{processing_time}")
                await ctx.debug(f"Processed chunk {i+1}/{processing_time}")
        
        result = f"Successfully processed {filename} in {processing_time} seconds"
        if ctx:
            operation_status[ctx.request_id] = "completed"
            await ctx.info(f"Completed processing {filename}")
        
        return result
        
    except asyncio.CancelledError:
        # Handle cancellation gracefully
        if ctx:
            operation_status[ctx.request_id] = "cancelled"
            await ctx.warning(f"Processing of {filename} was cancelled")
        raise  # Re-raise to properly signal cancellation


@server.tool()
async def get_request_status(ctx: Context = None) -> str:
    """
    Get the status of the current request.
    
    Args:
        ctx: MCP context (injected automatically)
    """
    if not ctx:
        return "No context available"
    
    request_id = ctx.request_id
    status = operation_status.get(request_id, "unknown")
    
    await ctx.info(f"Request {request_id} status: {status}")
    return f"Request {request_id} status: {status}"


@server.tool()
async def quick_task(message: str = "Hello", ctx: Context = None) -> str:
    """
    A quick task that completes immediately.
    
    Args:
        message: Message to return
        ctx: MCP context (injected automatically)
    """
    if ctx:
        await ctx.info(f"Executing quick task (Request: {ctx.request_id})")
        operation_status[ctx.request_id] = "completed"
    
    return f"Quick task completed: {message}"


@server.tool()
async def simulate_network_request(
    url: str,
    timeout: int = 5,
    ctx: Context = None
) -> str:
    """
    Simulate a network request that can be cancelled.
    
    Args:
        url: URL to simulate requesting
        timeout: Timeout in seconds
        ctx: MCP context (injected automatically)
    """
    if ctx:
        await ctx.info(f"Making request to {url} (Request: {ctx.request_id})")
        operation_status[ctx.request_id] = "requesting"
    
    try:
        # Simulate network delay
        await asyncio.sleep(timeout)
        
        result = f"Successfully fetched data from {url}"
        if ctx:
            operation_status[ctx.request_id] = "completed"
            await ctx.info(f"Request to {url} completed")
        
        return result
        
    except asyncio.CancelledError:
        if ctx:
            operation_status[ctx.request_id] = "cancelled"
            await ctx.warning(f"Request to {url} was cancelled")
        raise


if __name__ == "__main__":
    # Run the server
    server.run("streamable-http") 