import streamlit as st
import os
from dotenv import load_dotenv
from phi.agent import Agent
from phi.model.groq import Groq  # Adjust import based on actual model availability
from phi.tools.serpapi_tools import SerpApiTools

# Load environment variables from .env file (if exists)
load_dotenv()

# Set page configuration
st.set_page_config(
    page_title="AI Travel Planner",
    page_icon="🌎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for improved UI and responsiveness
st.markdown("""
    <style>
    :root {
        --primary-color: #2E86C1;
        --accent-color: #FF6B6B;
        --background-light: #F8F9FA;
        --text-color: #2C3E50;
        --hover-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }
    .main {
        padding: 2rem;
        max-width: 1200px;
        margin: 0 auto;
    }
    .stButton > button {
        width: 100%;
        border-radius: 8px;
        height: 3em;
        background-color: var(--accent-color) !important;
        color: white !important;
        font-weight: bold;
        font-size: 1rem;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: var(--hover-shadow);
        background-color: #FF4A4A !important;
    }
    .sidebar .element-container {
        background-color: var(--background-light);
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    .stExpander {
        background-color: #262730;
        border-radius: 10px;
        padding: 1rem;
        border: none;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    .travel-summary {
        background-color: #262730;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    }
    .travel-summary h4 {
        color: var(--primary-color);
        margin-bottom: 0.5rem;
    }
    .spinner-text {
        font-size: 1.2rem;
        font-weight: bold;
        color: var(--primary-color);
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar: Collecting all necessary user inputs based on the assignment requirements
with st.sidebar:
    st.image("https://img.icons8.com/clouds/200/airplane-take-off.png")
    st.title("Trip Settings")

    # API Keys for external services
    groq_api_key = st.text_input("🔑 Enter your Groq API Key", type="password")
    serpapi_key = st.text_input("🔑 Enter your SerpAPI Key", type="password")
    
    # Basic trip details
    destination = st.text_input("🌍 Destination", "")
    duration = st.number_input("📅 Trip Duration (days)", min_value=1, max_value=30, value=5)
    budget = st.select_slider("💰 Budget Level", options=["Budget", "Moderate", "Luxury"], value="Moderate")
    
    # Additional details for input refinement (Step 1 in assignment)
    st.markdown("### Additional Preferences")
    dietary = st.text_input("🍽️ Dietary Preferences (e.g., vegetarian, vegan, etc.)", "")
    mobility = st.selectbox("🚶 Mobility Concerns", options=["No Issues", "Limited Walking", "Wheelchair Accessible Needed"])
    accom_pref = st.multiselect("🏨 Accommodation Preferences", options=["Central Location", "Quiet", "Family Friendly", "Luxury", "Budget"], default=["Central Location"])
    travel_style = st.multiselect("🎯 Travel Style", options=["Culture", "Nature", "Adventure", "Relaxation", "Food", "Shopping"], default=["Culture", "Nature"])
    specific_interests = st.multiselect("🔍 Specific Interests (Optional)", options=["Museums", "Local Markets", "Historical Sites", "Outdoor Activities", "Nightlife", "Art Galleries"])

# Initialize session state variables
if 'travel_plan' not in st.session_state:
    st.session_state.travel_plan = None
if 'qa_expanded' not in st.session_state:
    st.session_state.qa_expanded = False

loading_container = st.empty()

# Set API keys to environment variables
os.environ["GROQ_API_KEY"] = groq_api_key
os.environ["SERP_API_KEY"] = serpapi_key

# Initialize travel agent with Groq Llama model and SerpAPI tools
# Agent instructions include steps to verify live information and chain prompts to refine inputs
travel_agent = Agent(
    name="Travel Planner",
    model=Groq(id="llama-3.3-70b-versatile"),  # Adjust model ID if needed
    tools=[SerpApiTools()],
    instructions=[
        "System Prompt: You are an AI travel planning assistant using Groq Llama. Your goal is to generate a highly personalized travel itinerary.",
        "Input Refinement: Ask clarifying questions to gather detailed information about dietary preferences, mobility concerns, accommodation preferences, and specific interests if not provided.",
        "Activity Suggestions: Use live web search tools to gather up-to-date information on attractions, dining, accommodations, and transportation options that match user inputs.",
        "Itinerary Generation: Create a detailed, day-by-day itinerary that includes seasonal highlights, top attractions, local culinary experiences, and practical travel tips. Always include verified source links.",
        "Ensure the itinerary is clear, well-structured, and tailored to the provided travel preferences."
    ],
    show_tool_calls=True,
    markdown=True
)

# Main UI: Display travel summary based on user inputs
st.title("🌎 AI Travel Planner")
st.markdown(f"""
    <div class="travel-summary">
        <h4>Welcome to your personal AI Travel Assistant! 🌟</h4>
        <p>We'll use your inputs to craft a personalized itinerary.</p>
        <p><strong>Destination:</strong> {destination}</p>
        <p><strong>Duration:</strong> {duration} days</p>
        <p><strong>Budget:</strong> {budget}</p>
        <p><strong>Travel Styles:</strong> {', '.join(travel_style)}</p>
        <p><strong>Accommodation Preferences:</strong> {', '.join(accom_pref)}</p>
        <p><strong>Dietary Preferences:</strong> {dietary if dietary else 'None specified'}</p>
        <p><strong>Mobility:</strong> {mobility}</p>
        <p><strong>Specific Interests:</strong> {', '.join(specific_interests) if specific_interests else 'Not specified'}</p>
    </div>
""", unsafe_allow_html=True)

# New UI section for confirmation and additional details
st.markdown("### Can you confirm the details?")
confirmation = st.checkbox("I confirm that the above details are correct.")
extra_details = st.text_area("Is there anything else you’d like to add?")

# Button to generate suggestions and final itinerary; ensure confirmation before proceeding
if st.button("✨ Generate My Perfect Travel Plan", type="primary"):
    if not destination:
        st.warning("Please enter a destination")
    elif not confirmation:
        st.warning("Please confirm your details before proceeding")
    else:
        try:
            with st.spinner("🔍 Refining inputs and gathering suggestions..."):
                # Step 1: Input refinement prompt – ensure we have a complete set of preferences
                refinement_prompt = f"""
                System Prompt:
                You are an AI travel assistant. Gather and confirm the following details:
                - Destination: {destination}
                - Duration: {duration} days
                - Budget Level: {budget}
                - Travel Styles: {', '.join(travel_style)}
                - Specific Interests: {', '.join(specific_interests) if specific_interests else "None"}
                - Dietary Preferences: {dietary if dietary else "None"}
                - Mobility Concerns: {mobility}
                - Accommodation Preferences: {', '.join(accom_pref)}
                
                Ask if any of these details require further clarification before generating a plan.
                Provide a short confirmation message with any suggestions for additional details if needed.
                """
                # Optionally, you might run a first call to refine user inputs (here we assume confirmation)
                refinement_response = travel_agent.run(refinement_prompt)
                
                # Step 2: Detailed itinerary generation prompt, chaining the refined inputs
                itinerary_prompt = f"""
                Create a comprehensive travel plan for {destination} for {duration} days.
                
                Travel Preferences:
                - Budget Level: {budget}
                - Travel Styles: {', '.join(travel_style)}
                - Specific Interests: {', '.join(specific_interests) if specific_interests else "None"}
                - Dietary Preferences: {dietary if dietary else "None"}
                - Mobility Concerns: {mobility}
                - Accommodation Preferences: {', '.join(accom_pref)}
                
                Additional Details: {extra_details if extra_details else "None provided"}
                
                The itinerary should include:
                1. 🌞 Best Time to Visit:
                   - Seasonal highlights and weather considerations.
                2. 🏨 Accommodation Recommendations:
                   - Options within the {budget} range, with details on location and amenities.
                3. 🗺️ Day-by-Day Itinerary:
                   - Detailed daily activities, sightseeing, and local experiences.
                4. 🍽️ Culinary Experiences:
                   - Recommended restaurants and local cuisine, considering dietary needs.
                5. 💡 Practical Travel Tips:
                   - Local transportation, cultural etiquette, safety tips, and estimated daily costs.
                6. 💰 Estimated Total Trip Cost:
                   - Expense breakdown and money-saving tips.
                
                Include up-to-date suggestions with verified live links for attractions, accommodations, and dining.
                Format the response in clear markdown with headings and bullet points.
                """
                final_response = travel_agent.run(itinerary_prompt)
                if hasattr(final_response, 'content'):
                    clean_response = final_response.content.replace('∣', '|').replace('\n\n\n', '\n\n')
                    st.session_state.travel_plan = clean_response
                    st.markdown(clean_response)
                else:
                    st.session_state.travel_plan = str(final_response)
                    st.markdown(str(final_response))
        except Exception as e:
            st.error(f"Error generating travel plan: {str(e)}")
            st.info("Please try again in a few moments.")

# Q&A Section for further inquiries about the itinerary
st.divider()
qa_expander = st.expander("🤔 Ask a specific question about your destination or travel plan", expanded=st.session_state.qa_expanded)
with qa_expander:
    st.session_state.qa_expanded = True
    question = st.text_input("Your question:", placeholder="What would you like to know about your trip?")
    if st.button("Get Answer", key="qa_button"):
        if question and st.session_state.travel_plan:
            with st.spinner("🔍 Finding answer..."):
                try:
                    context_question = f"""
                    I have a travel plan for {destination}. Here is the existing plan:
                    {st.session_state.travel_plan}
                    
                    Now, please answer this specific question: {question}
                    
                    Provide a focused and concise answer related to the travel itinerary.
                    """
                    response = travel_agent.run(context_question)
                    if hasattr(response, 'content'):
                        st.markdown(response.content)
                    else:
                        st.markdown(str(response))
                except Exception as e:
                    st.error(f"Error getting answer: {str(e)}")
        elif not st.session_state.travel_plan:
            st.warning("Please generate a travel plan first before asking questions.")
        else:
            st.warning("Please enter a question")

