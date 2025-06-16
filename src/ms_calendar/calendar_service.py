from typing import List, Optional
from datetime import datetime
from kiota_abstractions.request_information import RequestInformation
from kiota_abstractions.method import Method
from msgraph.generated.models.event_collection_response import EventCollectionResponse
from msgraph.generated.users.item.calendar.calendar_view.calendar_view_request_builder import CalendarViewRequestBuilder
from dotenv import load_dotenv
import os
from msgraph import GraphServiceClient
from azure.identity import ClientSecretCredential

load_dotenv()

client_id = os.getenv("AZURE_CLIENT_ID")
client_secret = os.getenv("AZURE_CLIENT_SECRET")
tenant_id = os.getenv("AZURE_TENANT_ID")

def get_graph_client() -> GraphServiceClient:
    if not all([client_id, client_secret, tenant_id]):
        raise ValueError("Missing Azure AD credentials in environment variables.")

    credential = ClientSecretCredential(
        tenant_id=tenant_id,
        client_id=client_id,
        client_secret=client_secret,
    )

    return GraphServiceClient(credential)

async def fetch_all_calendar_events(
    graph_client,
    user_id: str,
    start_date: datetime,
    end_date: datetime,
    select_fields: Optional[List[str]] = None,
    orderby: Optional[List[str]] = None,
):
    all_events = []

    query_parameters = CalendarViewRequestBuilder.CalendarViewRequestBuilderGetQueryParameters(
        start_date_time=start_date.isoformat(),
        end_date_time=end_date.isoformat(),
        select=select_fields,
        orderby=orderby,
    )

    request_config = CalendarViewRequestBuilder.CalendarViewRequestBuilderGetRequestConfiguration(
        query_parameters=query_parameters
    )

    request_builder = graph_client.users.by_user_id(user_id).calendar.calendar_view
    response = await request_builder.get(request_configuration=request_config)
    events = getattr(response, "value", [])
    all_events.extend(events)

    # Pagination
    next_link = getattr(response, "odata_next_link", None) or getattr(response, "@odata.nextLink", None)
    request_adapter = graph_client.request_adapter

    while next_link:
        request_info = RequestInformation()
        request_info.url = next_link
        request_info.http_method = Method.GET
        request_info.headers.add("Accept", "application/json")

        next_response = await request_adapter.send_async(
            request_info,
            EventCollectionResponse,
            {}
        )
        events = getattr(next_response, "value", [])
        all_events.extend(events)
        next_link = getattr(next_response, "odata_next_link", None) or getattr(next_response, "@odata.nextLink", None)

    return all_events
