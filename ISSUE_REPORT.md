# Title
LangGraph messages streaming crashes on AIMessageChunk JSON serialization

# What happened?
The application crashes when iterating `graph.astream(..., stream_mode="messages")`. Message chunks are yielded successfully, then OpenLIT fails during span finalization with:

`TypeError: Object of type AIMessageChunk is not JSON serializable`

Traceback points to:

`openlit/instrumentation/langgraph/async_langgraph.py` in `_finalize_async_stream_span` at `json.dumps(execution_state["executed_nodes"])`.

# Steps to reproduce
1. Clone this repository.
2. Run:

```bash
uv python install 3.12
uv venv --python 3.12 --clear .venv
source .venv/bin/activate
uv pip install -r requirements.txt
python repro_openlit_langgraph_messages.py
```

3. Observe streamed chunks are printed, followed by the serialization crash during finalization.

# Expected behavior
`graph.astream(..., stream_mode="messages")` should complete and OpenLIT should finalize spans without serialization errors.

# Environment
- Python: `3.12.12`
- OpenLIT: `1.37.1`
- LangGraph: `0.6.11`
- LangChain: `0.3.27`
- LangChain Core: `0.3.83`
- OS: macOS (Apple Silicon)

# Notes
- OTLP connection errors to `localhost:4318` may also appear if no collector is running; those are separate from the serialization crash.
