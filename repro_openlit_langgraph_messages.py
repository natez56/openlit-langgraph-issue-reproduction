import asyncio
import os
from typing import List, Optional

import openlit
from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, AIMessageChunk, BaseMessage, HumanMessage
from langchain_core.outputs import ChatGeneration, ChatGenerationChunk, ChatResult
from langgraph.graph import END, START, MessagesState, StateGraph


class FakeStreamingChatModel(BaseChatModel):
    """Minimal chat model that emits AIMessage chunks while streaming."""

    @property
    def _llm_type(self) -> str:
        return "fake-streaming-chat-model"

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs,
    ) -> ChatResult:
        text = "This is a synthetic model response."
        return ChatResult(generations=[ChatGeneration(message=AIMessage(content=text))])

    def _stream(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs,
    ):
        chunks = ["This ", "is ", "a ", "synthetic ", "model ", "response."]
        for chunk in chunks:
            yield ChatGenerationChunk(message=AIMessageChunk(content=chunk))



def build_graph():
    model = FakeStreamingChatModel()

    async def call_model(state: MessagesState):
        response = await model.ainvoke(state["messages"])
        return {"messages": [response]}

    graph = StateGraph(MessagesState)
    graph.add_node("call_model", call_model)
    graph.add_edge(START, "call_model")
    graph.add_edge("call_model", END)
    return graph.compile()


async def main():
    # Allows running locally without additional OTLP setup.
    os.environ.setdefault("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4318")

    openlit.init(
        application_name="openlit-langgraph-repro",
        environment="repro",
    )

    graph = build_graph()
    config = {"configurable": {"thread_id": "repro-thread"}}

    print("Starting graph.astream(..., stream_mode='messages')")

    stream = graph.astream(
        {"messages": [HumanMessage(content="Say hello.")]},
        config=config,
        stream_mode="messages",
    )

    count = 0
    async for chunk in stream:
        count += 1
        print(f"chunk {count}: {chunk}")

    print("All chunks yielded. If bug is present, error appears during span finalization.")

    # Leave a small window for async span finalization/export.
    await asyncio.sleep(1.0)


if __name__ == "__main__":
    asyncio.run(main())
