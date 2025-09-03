# Advanced Recipe Voice Agent

This project demonstrates a **SignalWire AI Agent** that acts as a
sophisticated culinary assistant.
It integrates **SWAIG (SignalWire AI Gateway)** with the **Agents SDK**
to deliver real-time cooking guidance, recipe discovery, and ingredient
substitution via natural voice conversation.

------------------------------------------------------------------------

## ✨ Features

-   **Multi-context conversation flow**: Greeting, recipe search,
    cooking guidance.
-   **State management**: Remembers user preferences and dietary
    restrictions.
-   **API integrations**: Uses Spoonacular for recipe data.
-   **Prompt Object Model (POM)**: Structured configuration for AI
    personality.
-   **Voice-optimized interactions**: Breaks recipes into manageable
    spoken steps.
-   **Custom SWAIG functions**: For recipe search, cooking timers,
    substitutions, and encouragement.

------------------------------------------------------------------------

## 🚀 Getting Started

### 1. Clone Repository

``` bash
gh repo clone jongray00/RecipeBot-AgentsSDK
```

### 2. Install Dependencies

``` bash
pip install signalwire-agents
```

### 3. Configure Environment Variables

Create a `.env` file with the following content:

``` bash
# Required
SPOONACULAR_API_KEY=your_spoonacular_api_key_here

# Optional: Basic authentication for webhook security
# SWML_BASIC_AUTH_USER=your_username
# SWML_BASIC_AUTH_PASSWORD=your_password

# Optional: SSL configuration for production deployment
# SWML_SSL_ENABLED=true
# SWML_SSL_CERT_PATH=/path/to/certificate.pem
# SWML_SSL_KEY_PATH=/path/to/private-key.pem

# Optional: Post-prompt webhook for logging or analytics
# POST_PROMPT_URL=https://your-webhook-url.com
```

------------------------------------------------------------------------

## 📖 How It Works

### SWAIG Overview

SWAIG allows your AI Agent to **call external APIs in real-time** during
conversations.
This project uses SWAIG + DataMap to connect with the **Spoonacular
API** for recipes. [Spoonacular API](https://spoonacular.com/food-api)

Instead of juggling multiple services and webhooks, the **Agents SDK**
provides everything in a **single Python file**.

### Example: DataMap Integration

``` python
recipe_search_tool = (DataMap("search_recipes_by_criteria")
    .purpose("Search for recipes based on dietary preferences, cuisine, and cooking time")
    .parameter("query", "string", "Recipe name or type of dish", required=True)
    .webhook(
        "GET",
        "https://api.spoonacular.com/recipes/complexSearch",
        headers={"Content-Type": "application/json"}
    )
    .params({
        "apiKey": os.getenv("SPOONACULAR_API_KEY"),
        "query": "${args.query}",
        "number": 3
    })
    .foreach({
        "input_key": "results",
        "output_key": "recipes_list",
        "append": "I found ${this.title}, ready in ${this.readyInMinutes} minutes."
    })
    .output(SwaigFunctionResult("${foreach.recipes_list}"))
)
```

------------------------------------------------------------------------

## 📞 Running the Agent

``` bash
python recipe_agent.py
```

Expected output:

    🍳 Advanced Recipe Agent starting...
    Ready to help with all your cooking needs!
    Call your SignalWire number to begin cooking!

------------------------------------------------------------------------

## 📡 Deployment

1.  Expose local server with **ngrok**:

    ``` bash
    ngrok http 5000
    ```

    Copy the public URL.

2.  In the **SignalWire Dashboard**:

    -   Buy a number
    -   Point it to your agent's ngrok URL

3.  Call your number and start cooking with **Chef Auguste** 🍲.

------------------------------------------------------------------------

## 🧑‍🍳 Agent Personality

-   Role: *Chef Auguste*, expert in world cuisines.
-   Style: Friendly, encouraging, and practical.
-   Safety: Always checks for allergies, food safety, and
    substitutions.
-   Languages: British English with natural fillers for voice guidance.

------------------------------------------------------------------------

## 🛠️ SWAIG Best Practices

1.  **Single responsibility functions** -- Each tool does one thing
    well.
2.  **Error handling** -- Always provide fallback responses.
3.  **State management** -- Persist user preferences across calls.
4.  **Voice-optimized responses** -- Keep them short, clear, and
    encouraging.

------------------------------------------------------------------------

## 🔗 Resources

-   [SignalWire Developer Docs](https://developer.signalwire.com)
-   [Agents SDK Documentation](https://developer.signalwire.com/agents)
-   [Spoonacular API](https://spoonacular.com/food-api)

------------------------------------------------------------------------

## 📝 License

MIT License -- feel free to use and extend this project.
