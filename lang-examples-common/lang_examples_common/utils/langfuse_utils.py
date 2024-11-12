import os

import pandas as pd
from langfuse import Langfuse
from langfuse.api.resources.commons.types.trace import Trace

langfuse = Langfuse(
    host=os.environ["LANGFUSE_HOST"],
    public_key=os.environ["LANGFUSE_PUBLIC_KEY"],
    secret_key=os.environ["LANGFUSE_SECRET_KEY"],
)


def fetch_traces(session_id) -> list[Trace]:
    """
    Wrapper for langfuse.fetch_traces to paginate
    """
    all_traces = []
    for page in range(1, 15):
        # 100 is the max allowed by default. We could increase it if needed
        traces = langfuse.fetch_traces(session_id=session_id, limit=100, page=page)
        assert traces.meta.page == page
        all_traces.extend(traces.data)
        if traces.meta.total_pages == traces.meta.page:
            break
    # log_and_add_to_report_critical("Warning: More than 15 pages of traces for this session !")
    return all_traces


def get_stats_from_traces(traces: list[Trace]) -> dict[str, float | pd.Timedelta]:
    if not traces:
        return {"total_cost": 0, "total_duration": pd.Timedelta(seconds=0)}
    traces_df = pd.DataFrame([trace.dict() for trace in traces])
    return {
        "total_cost": traces_df.totalCost.sum(),
        "total_duration": pd.Timedelta(seconds=traces_df.latency.sum()),
    }
