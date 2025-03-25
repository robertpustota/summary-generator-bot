import dspy

lm = dspy.LM(model="gpt-4o-mini")
dspy.settings.configure(lm=lm)


class SummaryGenerationSignature(dspy.Signature):
    chat: list[str] = dspy.InputField(
        desc="Input text as a list of strings, where each element is a message, e.g., ['liubachevskyi_inv: Dspy as it is', 'liubachevskyi_inv: Too bad there is no native async', 'robertpustota: yeah']"
    )
    summary_length: int = dspy.InputField(
        desc="The number of characters to generate for the summary."
    )
    summary: str = dspy.OutputField(
        desc="Generated summary based on the input list of messages."
    )


class SummaryGenerator(dspy.Module):
    """
    A module for generating summaries from chat history using a specified language model.
    Attributes:
        llm_model (str): The name of the language model to use for summary generation.
        llm_model_kwargs (dict): Additional keyword arguments for configuring the language model.
        agent (dspy.Predict): An agent responsible for handling the summary generation process.
    Methods:
        forward(chat_history: list[str], summary_length: int) -> str:
            Generates a summary based on the provided chat history and desired summary length.
        invoke(chat_history: list[str], summary_length: int) -> str:
            Executes the summary generation process within a specific language model context.
    """
    def __init__(self, llm_model: str = "openai/gpt-4o-mini", llm_model_kwargs: dict = {}):
        self.llm_model = llm_model
        self.llm_model_kwargs = llm_model_kwargs
        self.agent = dspy.Predict(SummaryGenerationSignature)

    def forward(self, chat_history: list[str], summary_length: int):
        return self.agent(chat=chat_history, summary_length=summary_length).summary
    
    def invoke(self, chat_history: list[str], summary_length):
        with dspy.settings.context(lm=dspy.LM(self.llm_model, **self.llm_model_kwargs)):
            return self.forward(chat_history, summary_length=summary_length)
