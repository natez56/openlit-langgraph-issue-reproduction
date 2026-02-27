# OpenLIT + LangGraph Messages Streaming Repro

Minimal reproducible example for an OpenLIT crash when instrumenting LangGraph async streaming with `stream_mode="messages"`.

## Issue Summary

When running:

`graph.astream(input, config=config, stream_mode="messages")`

the stream yields message chunks, then crashes during OpenLIT span finalization with:

`TypeError: Object of type AIMessageChunk is not JSON serializable`

Traceback points to:

`openlit/instrumentation/langgraph/async_langgraph.py`, `_finalize_async_stream_span`, `json.dumps(execution_state["executed_nodes"])`

## Environment

- Python: `3.12.12`
- OpenLIT: `1.37.1`
- LangGraph: `0.6.11`
- LangChain: `0.3.27`
- LangChain Core: `0.3.83`
- OS: macOS (Apple Silicon)

## Reproduction Steps

```bash
git clone <this-repo-url>
cd openlit-minimal-reproduction

uv python install 3.12
uv venv --python 3.12 --clear .venv
source .venv/bin/activate
uv pip install -r requirements.txt

python repro_openlit_langgraph_messages.py
```

Shortcut:

```bash
./run_repro.sh
```

## Expected Behavior

The stream should complete and OpenLIT should finalize spans without raising serialization errors.

## Actual Behavior

After the final streamed message chunk, execution fails with:

`TypeError: Object of type AIMessageChunk is not JSON serializable`

## Notes

- You may also see OTLP exporter connection errors if no collector is running on `localhost:4318`. Those are separate from the serialization crash.
- The repro uses a fake local chat model to avoid external API dependencies.
