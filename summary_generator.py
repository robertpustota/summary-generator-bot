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
    additional_info: str | None = dspy.InputField(
        desc="Additional information that is not part of the summary, but is relevant to the conversation."
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

    def forward(self, chat_history: list[str], summary_length: int, additional_info: str | None = None):
        return self.agent(chat=chat_history, summary_length=summary_length, additional_info=additional_info).summary
    
    def invoke(self, chat_history: list[str], summary_length: int, additional_info: str | None = None):
        with dspy.settings.context(lm=dspy.LM(self.llm_model, **self.llm_model_kwargs)):
            return self.forward(chat_history, summary_length=summary_length, additional_info=additional_info)


class OneShotAskSignature(dspy.Signature):
    query: str = dspy.InputField(
        desc="The query to be answered."
    )
    context: list[str] = dspy.InputField(
        desc="The context to be used for answering the query. Can be empty."
    )
    answer: str = dspy.OutputField(
        desc="The answer to the query."
    )
    
class OneShotAsk(dspy.Module):
    """
    A module for answering questions based on a given context using a specified language model.
    Attributes:
        llm_model (str): The name of the language model to use for answering questions.
        llm_model_kwargs (dict): Additional keyword arguments for configuring the language model.
        agent (dspy.Predict): An agent responsible for handling the question answering process.
    Methods:
        forward(query: str, context: list[str]) -> str:
            Generates an answer based on the provided query and context.
        invoke(query: str, context: list[str]) -> str:
            Executes the question answering process within a specific language model context.   
    """
    def __init__(self, llm_model: str = "openai/gpt-4o-mini", llm_model_kwargs: dict = {}):
        self.llm_model = llm_model
        self.llm_model_kwargs = llm_model_kwargs
        self.agent = dspy.Predict(OneShotAskSignature)

    def forward(self, query: str, context: list[str]) -> str:
        return self.agent(query=query, context=context).answer
    
    def invoke(self, query: str, context: list[str]) -> str:
        with dspy.settings.context(lm=dspy.LM(self.llm_model, **self.llm_model_kwargs)):
            return self.forward(query, context)
