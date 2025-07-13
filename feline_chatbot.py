import streamlit as st
from openai import OpenAI
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Our 7-Cats Personality Chatbot",
    page_icon="🐱",
    layout="wide"
)

# Initialize OpenAI client
@st.cache_resource
def initialize_openai_client():
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        st.error("Please set your OPENAI_API_KEY in the environment variables or .env file")
        st.stop()
    return OpenAI(api_key=openai_api_key)

# Calculate cat ages (2025 - adoption year) and human equivalent
CAT_AGES = {
    "Molly": {"actual": 2025 - 2015, "human_equivalent": 56},    # 10 years old = 56 human years
    "Ciko": {"actual": 2025 - 2015, "human_equivalent": 56},     # 10 years old = 56 human years
    "Bushy": {"actual": 2025 - 2020, "human_equivalent": 36},    # 5 years old = 36 human years
    "Lily": {"actual": 2025 - 2015, "human_equivalent": 56},     # 10 years old = 56 human years
    "Oyen": {"actual": 2025 - 2020, "human_equivalent": 36},     # 5 years old = 36 human years
    "Snowy": {"actual": 2025 - 2014, "human_equivalent": 60},    # 11 years old = 60 human years
    "Kuni": {"actual": 2025 - 2014, "human_equivalent": 60}      # 11 years old = 60 human years
}
CHARACTER_PERSONALITIES = {
    "Molly": "The smallest cat in the house, grey and white long-haired. Very quiet but gets extremely excited when scratched at the base of her tail - makes happy sounds! Has been with owners Zaidah & Faza since 2015 in their minimalist Semenyih home with wooden furniture. Roams freely except bedrooms/offices. Often bullied by Oyen but stays gentle. Uses the automatic litter robot and feeder system (10+ years together!).",
    
    "Ciko": "A dark chocolate to black domestic short-hair girl cat with only 3 legs, but don't let that fool you! Despite missing a leg, very active and can jump to higher tables. Has been with owners Zaidah & Faza since 2015 in their minimalist Semenyih home. Roams freely around the wooden furniture, uses the automatic feeder and litter robot. Very playful and gets into mischief (10+ years of adventures!).",
    
    "Bushy": "A grey flat-faced cat, very bushy as the name suggests. Can't jump to tables but makes up for it with LOUD howling like a wolf, facing walls at certain times - very annoying! Clingy but fights back with high energy when hugged. Joined Zaidah & Faza's minimalist family in 2020 in Semenyih, Malaysia. Roams the wooden-furnished house freely, uses automatic systems (5+ years of chaos!).",
    
    "Lily": "The fattest and most lazy cat! White with black spots like a cow, domestic short-hair. Very shy and loves to eat and sleep all day. Sometimes clingy wanting scratches but NEVER allows hugs. Has been with owners Zaidah & Faza since 2015 in their minimalist Semenyih home. Enjoys the automatic feeder timing! Often bullied by Oyen but too lazy to fight back (10+ years of cuddles!).",
    
    "Oyen": "An annoying orange cat! Mix of domestic long-hair with Maine Coon face shape but looks like a kitten despite being 3+ years old. Very vocal, loves meowing to humans but shy with strangers. LOVES peeing on the floor instead of the litter robot, marking territory and giving Zaidah & Faza headaches! Always disturbs other cats, especially bullying Molly and Lily. Joined the minimalist Semenyih family in 2020 (5+ years of mischief!).",
    
    "Snowy": "A beautiful white cat mixed with Ragdoll, has stunning blue eyes and dark grey stripes/spots. Very vocal with high-pitched meows to owners. The longest family member since 2014 in Zaidah & Faza's minimalist wooden-furnished home in Semenyih, Malaysia. Roams freely, uses the automatic systems. Gentle and affectionate (11+ years of love!).",
    
    "Kuni": "The biggest cat - a gentle giant! Mix of Maine Coon with domestic long-hair (though not as big as real Maine Coon). Very kind and well-behaved, gets special treatment to enter the office rooms that other cats can't access. Very clingy specifically to Faza. Has been with the family since 2014 in their minimalist Semenyih home with continuous water fountain and automatic systems (11+ years together!)."
}

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "selected_cat" not in st.session_state:
    st.session_state.selected_cat = "Molly"

def get_cat_response(cat_personality, user_message, conversation_history):
    """Get response from OpenAI based on cat personality"""
    client = initialize_openai_client()
    
    # Build messages for the API call - limit conversation history to save tokens
    messages = [{"role": "system", "content": f"You are {st.session_state.selected_cat}, a cat. {cat_personality} Respond briefly as this cat would."}]
    
    # Only include last 4 messages (2 exchanges) to save tokens
    recent_history = conversation_history[-4:] if len(conversation_history) > 4 else conversation_history
    messages.extend(recent_history)
    
    # Add current user message
    messages.append({"role": "user", "content": user_message})
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Cheaper than gpt-4o-mini
            messages=messages,
            max_tokens=100,  # Reduced from 500 to keep responses short
            temperature=0.7,  # Slightly reduced for more consistent responses
            presence_penalty=0.3,  # Encourage variety in responses
            frequency_penalty=0.3   # Reduce repetition
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Meow! Sorry, I'm having trouble right now: {str(e)}"

# Main UI
st.title("🐱 Meet Zaidah & Faza's Cats from Semenyih, Malaysia")
st.markdown("Chat with our 7 real house cats! Each has their own unique personality and will respond as if you're visiting our home in Semenyih, Malaysia.")

# Add a fun info section
st.info("🏠 **About Our Cat Family**: These are real cats living with Zaidah & Faza in Semenyih, Malaysia. Each cat's personality has been captured to give you an authentic experience of what it's like to interact with them!")

# Sidebar for cat selection
with st.sidebar:
    st.header("Choose Your Cat")
    
    # Cat selection with radio buttons showing name and age (sorted by age then alphabetical)
    st.write("**Select a cat to chat with:**")
    
    # Create options with cat name and age, sorted by age (oldest first) then alphabetical
    cat_list = []
    for cat_name in CHARACTER_PERSONALITIES.keys():
        cat_age = CAT_AGES[cat_name]
        cat_list.append((cat_name, cat_age['actual']))
    
    # Sort by age (descending) then by name (ascending)
    cat_list.sort(key=lambda x: (-x[1], x[0]))
    
    # Create display options
    cat_options = []
    for cat_name, age in cat_list:
        cat_options.append(f"{cat_name} ({age} years old)")
    
    # Find current selection index
    current_cat_option = f"{st.session_state.selected_cat} ({CAT_AGES[st.session_state.selected_cat]['actual']} years old)"
    current_index = cat_options.index(current_cat_option) if current_cat_option in cat_options else 0
    
    # Display radio buttons
    selected_option = st.radio(
        "Choose your cat:",
        cat_options,
        index=current_index,
        label_visibility="collapsed"
    )
    
    # Extract cat name from selection
    selected_cat = selected_option.split(" (")[0]
    
    # Update session state if cat changed
    if selected_cat != st.session_state.selected_cat:
        st.session_state.selected_cat = selected_cat
        st.session_state.messages = []  # Clear chat history when switching cats
        st.rerun()
    
    # Display cat personality in bullet points
    st.subheader(f"About {selected_cat}")
    
    # Create bullet points based on selected cat
    if selected_cat == "Molly":
        st.markdown("""
        • **Size**: Smallest cat in the house
        • **Appearance**: Grey & white long-haired
        • **Personality**: Very quiet but gets excited with tail scratches
        • **Special**: Makes happy sounds when scratched at tail base
        • **Age**: 10 years old (since 2015)
        • **Status**: Often bullied by Oyen but stays gentle
        """)
    elif selected_cat == "Ciko":
        st.markdown("""
        • **Appearance**: Dark chocolate/black domestic short-hair
        • **Special**: 3-legged girl cat who's very active
        • **Ability**: Can jump to higher tables despite missing leg
        • **Personality**: Very playful and gets into mischief
        • **Age**: 10 years old (since 2015)
        """)
    elif selected_cat == "Bushy":
        st.markdown("""
        • **Appearance**: Grey flat-faced cat, very bushy fur
        • **Limitation**: Can't jump to tables
        • **Special**: Howls like a wolf facing walls - very annoying!
        • **Personality**: Clingy but fights back when hugged
        • **Age**: 5 years old (since 2020)
        """)
    elif selected_cat == "Lily":
        st.markdown("""
        • **Appearance**: White with black cow spots, domestic short-hair
        • **Size**: The fattest and most lazy cat
        • **Personality**: Very shy, loves eating and sleeping
        • **Behavior**: Sometimes wants scratches but NEVER allows hugs
        • **Age**: 10 years old (since 2015)
        • **Status**: Often bullied by Oyen, too lazy to fight back
        """)
    elif selected_cat == "Oyen":
        st.markdown("""
        • **Appearance**: Orange cat with Maine Coon face, looks like kitten
        • **Size**: Unable to grow big despite being 3+ years old
        • **Personality**: Very annoying, vocal with humans, shy with strangers
        • **Problem**: Loves peeing on floor (not litter!), marks territory
        • **Behavior**: Bullies Molly & Lily constantly
        • **Age**: 5 years old (since 2020)
        """)
    elif selected_cat == "Snowy":
        st.markdown("""
        • **Appearance**: White Ragdoll mix with beautiful blue eyes
        • **Pattern**: Dark grey stripes and spots
        • **Personality**: Very vocal with high-pitched meows
        • **Status**: Longest family member, gentle and affectionate
        • **Age**: 11 years old (since 2014)
        """)
    elif selected_cat == "Kuni":
        st.markdown("""
        • **Appearance**: Maine Coon mix, biggest cat (gentle giant)
        • **Personality**: Very kind and well-behaved
        • **Special**: Gets office room access (others can't enter)
        • **Favorite**: Very clingy specifically to Faza
        • **Status**: Senior cat, gets special treatment
        • **Age**: 11 years old (since 2014)
        """)

    
    # Add owner and location info
    st.markdown("---")
    st.markdown("**🏠 Our Family:**")
    st.markdown("👥 **Owners:** Zaidah & Faza")
    st.markdown("📍 **Location:** Semenyih, Malaysia")
    st.markdown("🐾 **Total Cats:** 7 adorable felines")
    
    # Clear chat button
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.rerun()

# Main chat interface
cat_age = CAT_AGES[st.session_state.selected_cat]
st.header(f"Chatting with {st.session_state.selected_cat} 🐾")
st.subheader(f"Age: {cat_age['actual']} years old (≈ {cat_age['human_equivalent']} in human years)")

# Display chat history
chat_container = st.container()
with chat_container:
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.chat_message("user").write(message["content"])
        else:
            st.chat_message("assistant").write(message["content"])

# Chat input
user_input = st.chat_input(f"Say something to {st.session_state.selected_cat}...")

if user_input:
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Display user message
    st.chat_message("user").write(user_input)
    
    # Get cat response
    with st.chat_message("assistant"):
        with st.spinner(f"{st.session_state.selected_cat} is thinking..."):
            cat_response = get_cat_response(
                CHARACTER_PERSONALITIES[st.session_state.selected_cat],
                user_input,
                st.session_state.messages[:-1]  # Exclude the current user message
            )
        st.write(cat_response)
    
    # Add cat response to chat history
    st.session_state.messages.append({"role": "assistant", "content": cat_response})

# Footer
st.markdown("---")
st.markdown("*Made with ❤️ by Zaidah & Faza for their beloved cats in Semenyih, Malaysia*")

# Quick start suggestions
if len(st.session_state.messages) == 0:
    st.subheader("💡 Try these conversation starters:")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("What's your favorite activity?"):
            user_message = "What's your favorite activity?"
            st.session_state.messages.append({"role": "user", "content": user_message})
            # Generate AI response
            cat_response = get_cat_response(
                CHARACTER_PERSONALITIES[st.session_state.selected_cat],
                user_message,
                st.session_state.messages[:-1]
            )
            st.session_state.messages.append({"role": "assistant", "content": cat_response})
            st.rerun()
        
        if st.button("How do you feel about your owner?"):
            user_message = "How do you feel about your owner?"
            st.session_state.messages.append({"role": "user", "content": user_message})
            # Generate AI response
            cat_response = get_cat_response(
                CHARACTER_PERSONALITIES[st.session_state.selected_cat],
                user_message,
                st.session_state.messages[:-1]
            )
            st.session_state.messages.append({"role": "assistant", "content": cat_response})
            st.rerun()
    
    with col2:
        if st.button("What's your plan for today?"):
            user_message = "What's your plan for today?"
            st.session_state.messages.append({"role": "user", "content": user_message})
            # Generate AI response
            cat_response = get_cat_response(
                CHARACTER_PERSONALITIES[st.session_state.selected_cat],
                user_message,
                st.session_state.messages[:-1]
            )
            st.session_state.messages.append({"role": "assistant", "content": cat_response})
            st.rerun()
        
        if st.button("Tell me about yourself"):
            user_message = "Tell me about yourself"
            st.session_state.messages.append({"role": "user", "content": user_message})
            # Generate AI response
            cat_response = get_cat_response(
                CHARACTER_PERSONALITIES[st.session_state.selected_cat],
                user_message,
                st.session_state.messages[:-1]
            )
            st.session_state.messages.append({"role": "assistant", "content": cat_response})
            st.rerun()