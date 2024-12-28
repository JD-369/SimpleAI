import streamlit as st
import asyncio
import os
from together import AsyncTogether, Together

# Set page configuration with custom CSS
st.set_page_config(page_title="SimpleAI", page_icon="🤖", layout="wide")

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 2rem;
        background-color: white;
    }
    
    /* Animation for the background text */
    @keyframes moveBackground {
        0% {
        
            transform: translateX(-50%) translateY(0);
            color: rgba(255, 0, 0, 0.03);
        }
        33% {
            color: rgba(0, 255, 0, 0.03);
        }
        66% {
            color: rgba(0, 0, 255, 0.03);
        }
        100% {
            transform: translateX(-50%) translateY(-20px);
            color: rgba(255, 0, 0, 0.03);
        }
    }
    
    .background-text {
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translateX(-50%) translateY(-50%);
        font-size: 15vw;
        font-weight: bold;
        white-space: nowrap;
        z-index: -1;
        animation: moveBackground 8s infinite ease-in-out;
        pointer-events: none;
    }
    
    .stTitle {
        color: #2E4057;
        font-size: 3rem !important;
    }
    .stSubheader {
        color: #048BA8;
        margin-top: 2rem;
    }
    .stTextArea textarea {
        border-radius: 10px;
        border: 2px solid #E4E4E4;
    }
    .stButton>button {
        background-color: #048BA8;
        color: white;
        padding: 0.5rem 2rem;
        border-radius: 10px;
        border: none;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #037187;
    }
    .stExpander {
        background-color: #F7F7F7;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    </style>
    
    <!-- Add the background text element -->
    <div class="background-text">SimpleAI</div>
    """, unsafe_allow_html=True)

# Title and Header with better formatting
st.title("🤖 SimpleAI")
st.markdown("""
    <div style='background-color: #F0F8FF; padding: 1.5rem; border-radius: 10px; margin-bottom: 2rem;'>
        <h3 style='color: #2E4057; margin-bottom: 1rem;'>Welcome to SimpleAI!</h3>
        <p style='color: #666666;'>
            This app leverages multiple open-source AI models to generate comprehensive responses by:
            <ul>
                <li>Gathering insights from various AI models</li>
                <li>Synthesizing responses into a cohesive answer</li>
                <li>Providing both individual and aggregated perspectives</li>
            </ul>
        </p>
    </div>
    """, unsafe_allow_html=True)

# Sidebar with better styling
with st.sidebar:
    st.markdown("""
        <div style='text-align: center; padding: 1.5rem;'>
            <h2 style='color: #2E4057;'>About SimpleAI</h2>
            <p style='color: #666666; margin-top: 1rem;'>
                Your intelligent AI assistant powered by multiple language models.
            </p>
        </div>
        """, unsafe_allow_html=True)

# Sidebar for Settings
st.sidebar.title("About")
st.sidebar.markdown("Hiii!")
together_api_key = "4d9d6d2dddf8c56eb92ba82a0d09be9005570d9d654c7264cc355f6f7ebf2ce5"

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
                messages=[
                    {"role": "system", "content": "Provide a single, focused response to the user's query."},
                    {"role": "user", "content": user_prompt}
                ],
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

    # User input section with better styling
    st.markdown("### 💬 Ask Your Question")
    user_prompt = st.text_area(
        "",  # Remove label as we're using markdown above
        height=150,
        placeholder="Type your question here...",
        help="Enter any question or topic you'd like to explore"
    )

    # Create two columns for the button
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        generate_button = st.button("🧠 Generate Answer", use_container_width=True)

    # Add this at the top level of your script
    if 'response_shown' not in st.session_state:
        st.session_state.response_shown = False

    # Update your response handling section
    if generate_button and user_prompt and not st.session_state.response_shown:
        asyncio.run(main(user_prompt))  # Use the existing main() function instead

    # Add a clear button to reset the conversation
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        if st.button("🔄 Start New Conversation"):
            st.session_state.response_shown = False
            st.experimental_rerun()

    # Footer with better styling
    st.sidebar.markdown("""
        <div style='margin-top: 5rem; padding: 1.5rem; text-align: center; 
             background: linear-gradient(135deg, #f6f8fa 0%, #e9ecef 100%);
             border-top: 1px solid #dee2e6;
             box-shadow: 0 -2px 10px rgba(0,0,0,0.05);'>
            <p style='color: #495057; font-size: 0.9rem; margin: 0;'>
                <strong style='color: #2E4057;'>Developed by SREEHARI</strong><br>
                <span style='color: #6c757d;'>Contact: 
                    <a href='mailto:mesreehari23@gmail.com' style='color: #048BA8; text-decoration: none; 
                       hover: {color: #037187};'>abcd@gmail.com</a>
                </span>
            </p>
        </div>
        """, unsafe_allow_html=True)

    # Add a divider before responses
    if generate_button and user_prompt:
        st.markdown("<hr style='margin: 2rem 0;'>", unsafe_allow_html=True)

    async def get_model_response(model_name, model_info, prompt):
        try:
            # Your existing model response logic here
            response = await model_info['function'](prompt)
            return model_name, response
        except Exception as e:
            st.warning(f"Error getting response from {model_name}: {str(e)}")
            return model_name, None

    def combine_responses(responses):
        # Remove any None values and duplicates
        valid_responses = []
        seen = set()
        for r in responses:
            if r is not None and r not in seen:
                valid_responses.append(r)
                seen.add(r)
                
        if not valid_responses:
            raise ValueError("No valid responses to combine")
        
        # Take just the first response to avoid repetition
        return valid_responses[0]
