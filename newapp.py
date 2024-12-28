import streamlit as st
import asyncio
import os
from together import AsyncTogether, Together

# Set page configuration
st.set_page_config(page_title="SimpleAI", page_icon="🤖", layout="wide")

# Title and Header
st.title("🤖 SimpleAI")
st.markdown(
    """
    Welcome to the **SimpleAI**!  
    This app uses multiple open-source AI models to generate responses and synthesizes them into a high-quality aggregated answer.  
    """
)

# Sidebar for Settings
st.sidebar.title("About")
st.sidebar.markdown("Hiii!")


# Ensure API key is set
if together_api_key:
    os.environ["TOGETHER_API-KEY"] = together_api_key
    client = Together(api_key=together_api_key)
    async_client = AsyncTogether(api_key=together_api_key)

    # Define reference models and aggregator model
    reference_models = [
        "Qwen/QwQ-32B-Preview",
        "Quen/Qwen2-728-Instruct",
        "Qwen/Qwen1.5-728-Chat",
        "meta-llama/Llama-Vision-Free",
        "databricks/dbrx-instruct",
    ]
    aggregator_model = "databricks/dbrx-instruct"
    aggregator_system_prompt = """You have been provided with a set of responses from various open-source models to the latest user query. 
    Your task is to synthesize these responses into a single, high-quality response. It is crucial to critically evaluate the information 
    provided in these responses, recognizing that some of it may be biased or incorrect. Your response should not simply replicate the 
    given answers but should offer a refined, accurate, and comprehensive reply to the instruction. Ensure your response is well-structured, 
    coherent, and adheres to the highest standards of accuracy and reliability. Response from models:"""

    # Async function to get responses from models
    async def run_llm(model, user_prompt):
        try:
            response = await async_client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": user_prompt}],
                max_tokens=256,
                temperature=0.5,
                top_p=0.7,
                top_k=50,
                repetition_penalty=1,
            )
            return model, response.choices[0].message.content
        except Exception as e:
            return model, f"Error: {e}"

    # Main async function
    async def main(user_prompt):
        # Display loading spinner while responses are being fetched
        with st.spinner("Generating responses from models..."):
            results = await asyncio.gather(*[run_llm(model, user_prompt) for model in reference_models])

        # Display individual model responses
        st.subheader("📄 Individual Model Responses")
        for model, response in results:
            with st.expander(f"Response from {model}"):
                st.write(response)

        # Aggregated response
        st.subheader("🤝 Aggregated Response")
        try:
            final_stream = client.chat.completions.create(
                model=aggregator_model,
                messages=[
                    {"role": "system", "content": aggregator_system_prompt},
                    {"role": "user", "content": "\n\n".join(response for _, response in results)},
                ],
                stream=True,
            )

            # Display aggregated response in real-time
            response_container = st.empty()
            full_response = ""
            for chunk in final_stream:
                content = chunk.choices[0].delta.content or ""
                full_response += content
                response_container.markdown(f"**{full_response}**")
        except Exception as e:
            st.error(f"Error during aggregation: {e}")

    # User input section
    st.subheader("💬 Ask Your Question")
    user_prompt = st.text_area("Enter your question here:", height=150, placeholder="Type your query...")

    # Generate response button
    if st.button("🧠 Generate Answer"):
        if user_prompt:
            asyncio.run(main(user_prompt))
        else:
            st.warning("⚠️ Please enter a question to proceed.")

# Sidebar footer
st.sidebar.markdown(
    """
    **Developed by [SREEHARI](#)**  
    For any issues, [abcd@gmail.com](#).
    """
)
