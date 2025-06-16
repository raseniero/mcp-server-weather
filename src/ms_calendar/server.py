from typing import Any, List
from datetime import datetime
import pytz
from starlette.responses import JSONResponse
from mcp.server.fastmcp import FastMCP
from ms_calendar.calendar_service import fetch_all_calendar_events, get_graph_client

# Initialize FastMCP server
mcp = FastMCP("ms_calendar")

@mcp.tool()
async def get_calendar_events_time_specific(
    user_id: str,
    start: str = "2025-06-16",
    end: str = "2025-06-16",
    timezone: str = "Asia/Manila",
) -> dict[str, Any] | str:
    """
    FastMCP tool: Fetch calendar events for a user using Microsoft Graph API.

    Args:
        user_id: Microsoft Graph user ID.
        start: ISO datetime string for start.
        end: ISO datetime string for end.
        timezone: IANA timezone (default: UTC).

    Returns:
        Dictionary of events or error message.
    """
    try:
        tz = pytz.timezone(timezone)
        start_dt = tz.localize(datetime.strptime(start, "%Y-%m-%d"))
        end_dt = tz.localize(datetime.strptime(end, "%Y-%m-%d"))
    except Exception as e:
        return f"Invalid datetime or timezone: {e}"

    try:
        graph_client = get_graph_client()
        events = await fetch_all_calendar_events(
            graph_client, user_id, start_dt, end_dt
        )
        return {
            "count": len(events),
            "events": [
                {
                    "id": e.id,
                    "subject": e.subject,
                    "attendees": [
                        {
                            "email": attendee.email_address.address,
                            "name": attendee.email_address.name,
                            "type": attendee.type.value if attendee.type else None
                        }
                        for attendee in (e.attendees or [])
                    ]
                }
                for e in events
            ],
        }
    except Exception as e:
        return f"Error fetching events: {e}"

@mcp.custom_route("/health", methods=["GET"])
async def health_check(_):
    """Health check endpoint."""
    return JSONResponse({"status": "ok"})


if __name__ == "__main__":
    mcp.run(transport="stdio")
