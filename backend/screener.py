from dotenv import load_dotenv
import os
from agents import Agent, OpenAIChatCompletionsModel, AsyncOpenAI, RunConfig, Runner

load_dotenv()

gemini_api_key = os.getenv("GEMINI_API_KEY")
client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

model = OpenAIChatCompletionsModel(
    model="gemini-2.0-flash",
    openai_client=client
)

config = RunConfig(
    model=model,
    model_provider=client,
    tracing_disabled=True,
)

async def evaluate_cv(cv_content: str, job_prompt: str):
    agent = Agent(
         name="CV Screener",
        instructions="You're a hiring assistant. Based on the given job description, rate this CV from 1 to 100 and explain why.",
        
    )

    full_prompt = f"""
    Job Description:
    {job_prompt}

    Candidate CV:
    {cv_content}

    Respond with:
    1. A score from 1 to 100
    2. A short explanation of how well this CV fits the job
    """

    result = await Runner.run(agent,full_prompt,run_config=config)
    return result.final_output