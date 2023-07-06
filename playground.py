

from griptape.memory.structure import ConversationMemory
from griptape.memory.tool import TextToolMemory, BlobToolMemory
from griptape.structures import Pipeline
from griptape.tasks import ToolkitTask, PromptTask
from griptape.tools import WebScraper, FileManager


# Tool memory enables LLMs to store and manipulate data
# without ever looking at it directly.
text_memory = TextToolMemory()
blob_memory = BlobToolMemory()

# Connect a web scraper to load web pages.
web_scraper = WebScraper(
    output_memory={
        "get_content": [text_memory]
    }
)

# File manager can load and store files locally.
file_manager = FileManager(
    input_memory=text_memory,
    output_memory={
        "load_files_from_disk": [blob_memory]
    }
)

# Pipelines represent sequences of tasks.
pipeline = Pipeline(
    memory=ConversationMemory()
)

pipeline.add_tasks(
    # Load up the first argument from `pipeline.run`.
    ToolkitTask(
        "{{ args[0] }}",
        tools=[web_scraper, file_manager]
    ),
    # Augment `input` from the previous task.
    PromptTask(
        "Say the following in spanish: {{ input }}"
    )
)

pipeline.run(
    "Load https://www.griptape.ai, summarize it, and store it in griptape.txt"
)
