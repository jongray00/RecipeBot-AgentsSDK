#!/usr/bin/env python3
"""
Advanced Recipe Voice Agent - SignalWire Agents SDK

This agent demonstrates sophisticated conversational AI capabilities for culinary assistance.
It can find recipes, provide cooking guidance, suggest ingredient substitutions, and even
help with meal planning - all through natural voice conversation.

Key Features:
- Multi-context conversation flow (greeting, recipe search, cooking guidance)
- State management to remember user preferences and dietary restrictions
- Multiple API integrations via SWAIG functions and DataMap
- Structured prompt engineering with POM (Prompt Object Model)
- Dynamic responses based on conversation context
"""

import os
import logging
from typing import Dict, Any, Optional
from signalwire_agents import AgentBase, SwaigFunctionResult, DataMap

class AdvancedRecipeAgent(AgentBase):
    """
    A sophisticated recipe agent that provides personalized cooking assistance
    through natural voice conversation.
    
    This agent maintains conversation context, learns user preferences, and
    provides step-by-step cooking guidance with appropriate timing and pacing
    for voice-based interaction.
    """
    
    def __init__(self):
        # Initialize the base agent with comprehensive configuration
        super().__init__(
            name="advanced-recipe-agent",
            auto_answer=True,
            record_call=True,  # Enable call recording for quality assurance
            record_format="mp3"
        )
        
        # Optionally configure post-prompt webhook URL from environment
        post_prompt_url = os.getenv("POST_PROMPT_URL")
        if post_prompt_url:
            try:
                self.set_post_prompt_url(post_prompt_url)
            except Exception as e:
                logging.warning(f"Failed to set post prompt URL: {e}")
        
        # Configure the agent's personality and capabilities
        self._setup_agent_personality()
        
        # Set up structured conversation workflows
        self._setup_conversation_contexts()
        
        # Add modular skills for enhanced functionality
        self._add_core_skills()
        
        # Register custom tools and API integrations
        self._register_recipe_tools()
        
        # Configure speech recognition for cooking terminology
        self._setup_speech_optimization()
        
        # Initialize global data that will be available across all conversations
        self._initialize_global_data()
    
    def _setup_agent_personality(self):
        """
        Configure the agent's core personality using Prompt Object Model.
        
        This structured approach allows us to define different aspects of the
        agent's behavior separately, making it easier to maintain and modify.
        """
        
        # Define the agent's primary role and expertise
        self.prompt_add_section(
            "Role",
            "You are Chef Auguste, an experienced culinary assistant with expertise in "
            "international cuisines, dietary accommodations, and cooking techniques. "
            "You speak with warmth and enthusiasm about food while being practical "
            "and helpful."
        )
        
        # Establish the conversational context and expectations
        self.prompt_add_section(
            "Context",
            "Users call seeking cooking help - from finding recipes to step-by-step "
            "cooking guidance. You can access recipe databases, suggest substitutions, "
            "and provide personalized recommendations based on dietary needs."
        )
        
        # Provide specific behavioral guidelines
        self.prompt_add_section(
            "Communication Style",
            bullets=[
                "Use encouraging, friendly language that builds cooking confidence",
                "Break complex recipes into manageable voice-friendly steps",
                "Always ask about dietary restrictions and allergies for safety",
                "Provide timing estimates that work well for voice-guided cooking",
                "Suggest modifications for different skill levels"
            ]
        )
        
        # Define safety and dietary considerations
        self.prompt_add_section(
            "Safety Guidelines",
            "Always prioritize food safety and allergen awareness",
            bullets=[
                "Ask about food allergies before suggesting recipes",
                "Mention food safety temperatures when relevant",
                "Warn about common allergens in ingredients",
                "Suggest safe ingredient substitutions when needed"
            ]
        )
        
        # Configure voice and language settings for natural conversation
        self.add_language(
                name="British English",
                code="en-GB",
                voice="spore",
                engine="rime",
            model="multilingual",
            speech_fillers=[
                "Let me find that recipe for you...",
                "Searching our culinary database...",
                "One moment while I check the ingredients...",
                "Looking up cooking techniques..."
            ],
            function_fillers=[
                "Checking our recipe collection...",
                "Finding ingredient substitutions...",
                "Calculating cooking times..."
            ]
        )
        
        # Set AI parameters optimized for cooking conversations
        self.set_params({
            "ai_model": "gpt-4.1-nano",
            "end_of_speech_timeout": 1200,  # Longer timeout for thoughtful responses
            "attention_timeout": 45000,     # Keep attention during longer cooking steps
            "temperature": 0.8,             # Creative but consistent responses
            "max_tokens": 200               # Concise responses suitable for voice
        })
    
    def _setup_conversation_contexts(self):
        """
        Define structured conversation workflows using the Context System.
        
        This creates a natural flow from greeting to recipe assistance,
        with appropriate transitions and capabilities at each stage.
        """
        contexts = self.define_contexts()
        
        # Initial greeting and preference gathering context
        greeting_context = contexts.add_context("greeting")
        greeting_context.add_step("welcome") \
            .set_text(
                "Hello! I'm Chef Auguste, your personal culinary assistant. "
                "I'm here to help you discover delicious recipes and guide you "
                "through cooking. What brings you to the kitchen today?"
            ) \
            .set_step_criteria("User has indicated what type of cooking help they need") \
            .set_functions(["gather_preferences", "search_recipe_by_name"]) \
            .set_valid_steps(["preferences"])
        
        greeting_context.add_step("preferences") \
            .add_section("Current Task", "Gather dietary preferences and restrictions") \
            .add_bullets("Key Information", [
                "Food allergies or restrictions",
                "Cuisine preferences",
                "Cooking skill level",
                "Available cooking time"
            ]) \
            .set_functions(["save_preferences", "search_recipes_by_criteria"]) \
            .set_step_criteria("Preferences gathered and recipe search initiated")
        
        # Recipe discovery and selection context
        recipe_context = contexts.add_context("recipe_discovery")
        recipe_context.add_step("search") \
            .set_text("Let me search for recipes that match your preferences.") \
            .set_functions(["search_recipes_by_criteria", "get_recipe_details", "suggest_alternatives"]) \
            .set_step_criteria("Recipe options presented to user") \
            .set_valid_steps(["selection"]
        )
        
        recipe_context.add_step("selection") \
            .add_section("Current Task", "Help user choose the perfect recipe") \
            .add_bullets("Considerations", [
                "Cooking time available",
                "Ingredient availability",
                "Skill level match",
                "Dietary compatibility"
            ]) \
            .set_functions(["get_recipe_details", "check_ingredients", "estimate_cooking_time"]) \
            .set_step_criteria("User has selected a recipe to cook")
        
        # Active cooking guidance context
        cooking_context = contexts.add_context("cooking_guidance")
        cooking_context.add_step("preparation") \
            .set_text("Perfect choice! Let's start by preparing everything you'll need.") \
            .set_functions(["list_ingredients", "prep_timeline", "substitute_ingredient"]) \
            .set_step_criteria("User has gathered ingredients and tools") \
            .set_valid_steps(["cooking"])
        
        cooking_context.add_step("cooking") \
            .add_section("Guidance Mode", "Provide step-by-step cooking instructions") \
            .add_bullets("Coaching Style", [
                "Break complex steps into simple actions",
                "Provide timing cues and checkpoints",
                "Encourage and reassure throughout process",
                "Offer troubleshooting for common issues"
            ]) \
            .set_functions(["next_cooking_step", "cooking_timer", "troubleshoot_issue", "substitute_ingredient"]) \
            .set_step_criteria("Cooking process completed successfully")
    
    def _add_core_skills(self):
        """
        Add essential skills that enhance the agent's capabilities.
        
        Skills provide pre-built functionality that integrates seamlessly
        with the agent's conversation flow.
        """
        
        # Add time awareness for cooking timing and scheduling
        self.add_skill("datetime", {
            "timezone": "America/New_York",  # Adjust based on your deployment
            "format": "%I:%M %p"  # 12-hour format for natural speech
        })
        
        # Add mathematical calculations for recipe scaling and conversions
        self.add_skill("math", {
            "precision": 2  # Appropriate for cooking measurements
        })
    
    def _register_recipe_tools(self):
        """
        Register sophisticated recipe-related tools using DataMap for API integration
        and custom SWAIG functions for specialized logic.
        """
        
        # Spoonacular API integration for comprehensive recipe data
        recipe_search_tool = (DataMap("search_recipes_by_criteria")
            .purpose("Search for recipes based on dietary preferences, cuisine, and cooking time")
            .parameter("query", "string", "Recipe name or type of dish", required=True)
            .parameter("diet", "string", "Dietary restrictions (vegetarian, vegan, gluten-free, etc.)")
            .parameter("cuisine", "string", "Preferred cuisine type")
            .parameter("max_ready_time", "number", "Maximum cooking time in minutes")
            .parameter("intolerances", "string", "Food allergies or intolerances")
            .webhook(
                "GET",
                "https://api.spoonacular.com/recipes/complexSearch",
                headers={"Content-Type": "application/json"}
            )
            .params({
                "apiKey": os.getenv("SPOONACULAR_API_KEY", "YOUR_API_KEY_HERE"),
                "query": "${args.query}",
                "diet": "${args.diet}",
                "cuisine": "${args.cuisine}",
                "maxReadyTime": "${args.max_ready_time}",
                "intolerances": "${args.intolerances}",
                "addRecipeInformation": "true",
                "fillIngredients": "true",
                "number": 3,  # Limit results for voice-friendly presentation
                "sort": "popularity"
            })
            .foreach({
                "input_key": "results",
                "output_key": "recipes_list",
                "max": 3,
                "append": "I found ${this.title}. It takes about ${this.readyInMinutes} minutes and serves ${this.servings} people. ${this.summary}\n"
            })
            .output(SwaigFunctionResult(
                "${foreach.recipes_list}"
            ))
            .fallback_output(SwaigFunctionResult(
                "I'm sorry, I'm having trouble accessing the recipe database right now. "
                "Let me try a different approach to help you find something delicious to cook."
            ))
        )
        
        # Detailed recipe information retrieval
        recipe_details_tool = (DataMap("get_recipe_details")
            .purpose("Get complete recipe details including ingredients and instructions")
            .parameter("recipe_id", "string", "Unique recipe identifier", required=True)
            .webhook(
                "GET", 
                "https://api.spoonacular.com/recipes/${args.recipe_id}/information"
            )
            .params({
                "apiKey": os.getenv("SPOONACULAR_API_KEY", "YOUR_API_KEY_HERE"),
                "includeNutrition": "false"
            })
            .output(SwaigFunctionResult(
                "Here's how to make ${response.title}: "
                "You'll need ${response.extendedIngredients[*].original}. "
                "Ready in ${response.readyInMinutes} minutes. "
                "Here are the steps: ${response.analyzedInstructions[0].steps[*].step}"
            ))
        )
        
        # Ingredient substitution assistance
        substitution_tool = (DataMap("substitute_ingredient")
            .purpose("Find suitable ingredient substitutions")
            .parameter("ingredient", "string", "Ingredient to substitute", required=True)
            .webhook(
                "GET",
                "https://api.spoonacular.com/food/ingredients/substitutes"
            )
            .params({
                "apiKey": os.getenv("SPOONACULAR_API_KEY", "YOUR_API_KEY_HERE"),
                "ingredientName": "${args.ingredient}"
            })
            .output(SwaigFunctionResult(
                "For ${args.ingredient}, you can substitute: ${response.substitutes[*]}. "
                "These work well because ${response.message}"
            ))
        )
        
        # Register all DataMap tools with the agent
        self.register_swaig_function(recipe_search_tool.to_swaig_function())
        self.register_swaig_function(recipe_details_tool.to_swaig_function())
        self.register_swaig_function(substitution_tool.to_swaig_function())
        
        # Custom SWAIG functions are registered via the @AgentBase.tool decorator
    
    def _setup_speech_optimization(self):
        """
        Optimize speech recognition for cooking-related terminology.
        
        This helps the system better understand culinary terms, measurements,
        and common cooking phrases that users might say.
        """
        
        # Add cooking-specific vocabulary hints
        cooking_terms = [
            "sauté", "julienne", "brunoise", "mise en place", "al dente",
            "roux", "emulsion", "caramelize", "braise", "poach",
            "tablespoon", "teaspoon", "cup", "ounce", "pound",
            "Fahrenheit", "Celsius", "degrees", "minutes", "hours",
            "gluten-free", "dairy-free", "vegan", "vegetarian", "keto",
            "Italian", "French", "Asian", "Mexican", "Mediterranean"
        ]
        self.add_hints(cooking_terms)
        
        # Add pattern-based hints for common measurements
        self.add_pattern_hint(
            "measurement",
            r"(\d+)\s*(cup|cups|tablespoon|tablespoons|teaspoon|teaspoons)",
            r"\1 \2"
        )
        
        # Add pronunciation rules for commonly mispronounced cooking terms
        self.add_pronunciation("quinoa", "KEEN-wah")
        self.add_pronunciation("acai", "ah-sah-EE")
        self.add_pronunciation("gyoza", "gee-OH-zah")
    
    def _initialize_global_data(self):
        """
        Set up global data that will be available throughout conversations.
        
        This includes system information and default preferences that
        can be referenced by SWAIG functions and in conversation context.
        """
        
        self.set_global_data({
            "agent_version": "2.0.0",
            "cuisine_specialties": ["Italian", "French", "Asian", "Mediterranean", "American"],
            "dietary_options": ["vegetarian", "vegan", "gluten-free", "dairy-free", "keto", "paleo"],
            "skill_levels": ["beginner", "intermediate", "advanced"],
            "default_servings": 4,
            "support_contact": "For additional help, say 'transfer to support'"
        })
    
    # Custom SWAIG Functions for specialized recipe agent behavior
    
    @AgentBase.tool(
        name="save_user_preferences",
        description="Save user's dietary preferences and cooking style for future reference",
        parameters={
            "type": "object",
            "properties": {
                "dietary_restrictions": {
                    "type": "string",
                    "description": "Dietary restrictions or allergies"
                },
                "cuisine_preferences": {
                    "type": "string", 
                    "description": "Preferred cuisine types"
                },
                "skill_level": {
                    "type": "string",
                    "description": "Cooking skill level (beginner, intermediate, advanced)"
                },
                "cooking_time_preference": {
                    "type": "string",
                    "description": "Preferred cooking time (quick, moderate, leisurely)"
                }
            }
        }
    )
    def save_user_preferences(self, args: Dict[str, Any], raw_data: Dict[str, Any]) -> SwaigFunctionResult:
        """
        Save user preferences to persistent state for personalized future interactions.
        
        This function demonstrates how to use the state management system
        to create personalized experiences across multiple conversations.
        """
        
        # Extract user preferences from the function arguments
        preferences = {
            "dietary_restrictions": args.get("dietary_restrictions", ""),
            "cuisine_preferences": args.get("cuisine_preferences", ""),
            "skill_level": args.get("skill_level", "intermediate"),
            "cooking_time_preference": args.get("cooking_time_preference", "moderate"),
            "saved_at": "now"  # This will be processed by the state manager
        }
        
        # Update global data for immediate use in current conversation
        current_global_data = self.get_global_data() or {}
        current_global_data.update({"user_preferences": preferences})
        
        # Create a response that acknowledges the saved preferences
        response_text = (
            f"Perfect! I've noted that you prefer {preferences['cuisine_preferences']} cuisine "
            f"and consider yourself a {preferences['skill_level']} cook. "
        )
        
        if preferences['dietary_restrictions']:
            response_text += f"I'll make sure to consider your {preferences['dietary_restrictions']} needs. "
        
        response_text += "Now I can give you more personalized recipe suggestions!"
        
        return (SwaigFunctionResult(response_text)
                .update_global_data({"user_preferences": preferences})
                .set_metadata({"preferences_saved": True}))
    
    @AgentBase.tool(
        name="get_cooking_timer",
        description="Set up cooking timers with voice-friendly alerts",
        parameters={
            "type": "object",
            "properties": {
                "duration_minutes": {
                    "type": "number",
                    "description": "Timer duration in minutes"
                },
                "timer_name": {
                    "type": "string",
                    "description": "What this timer is for (e.g., 'pasta cooking', 'oven preheating')"
                }
            },
            "required": ["duration_minutes"]
        }
    )
    def get_cooking_timer(self, args: Dict[str, Any], raw_data: Dict[str, Any]) -> SwaigFunctionResult:
        """
        Provide cooking timer functionality optimized for voice interaction.
        
        This demonstrates how to create SWAIG functions that provide
        practical cooking assistance with appropriate voice feedback.
        """
        
        duration = args.get("duration_minutes", 0)
        timer_name = args.get("timer_name", "cooking")
        
        # Convert minutes to seconds for the wait action
        duration_seconds = int(duration * 60)
        
        response_text = f"Setting a {duration} minute timer for {timer_name}. "
        
        if duration <= 5:
            response_text += "I'll check back with you soon!"
        elif duration <= 15:
            response_text += "I'll let you know when it's ready. Feel free to ask me other cooking questions while you wait!"
        else:
            response_text += "That gives us plenty of time. Would you like help with another part of the recipe?"
        
        return (SwaigFunctionResult(response_text)
                .add_action("wait_seconds", duration_seconds)
                .update_global_data({
                    "active_timer": {
                        "name": timer_name,
                        "duration": duration,
                        "started_at": "now"
                    }
                }))
    
    @AgentBase.tool(
        name="provide_cooking_encouragement",
        description="Give encouraging cooking tips and motivation",
        parameters={
            "type": "object",
            "properties": {
                "cooking_stage": {
                    "type": "string",
                    "description": "Current stage of cooking (prep, cooking, finishing, etc.)"
                },
                "difficulty_level": {
                    "type": "string",
                    "description": "How challenging this step is"
                }
            }
        }
    )
    def provide_cooking_encouragement(self, args: Dict[str, Any], raw_data: Dict[str, Any]) -> SwaigFunctionResult:
        """
        Provide contextual encouragement and cooking tips.
        
        This function shows how SWAIG functions can provide dynamic,
        context-aware responses that enhance the user experience.
        """
        
        stage = args.get("cooking_stage", "cooking")
        difficulty = args.get("difficulty_level", "moderate")
        
        # Create encouraging responses based on context
        encouragement_responses = {
            "prep": [
                "Great job getting organized! Good prep work makes everything else easier.",
                "You're doing wonderfully. Taking time to prep properly is the mark of a great cook!"
            ],
            "cooking": [
                "You're doing fantastic! Trust the process and your instincts.",
                "Looking good! Remember, cooking is about enjoying the journey as much as the destination."
            ],
            "finishing": [
                "You're almost there! The final touches make all the difference.",
                "Excellent work! These last steps will make your dish truly special."
            ]
        }
        
        # Select appropriate encouragement
        responses = encouragement_responses.get(stage, encouragement_responses["cooking"])
        import random
        selected_response = random.choice(responses)
        
        if difficulty == "challenging":
            selected_response += " Don't worry if it's not perfect - every chef learns by doing!"
        
        return SwaigFunctionResult(selected_response)
    
    def on_summary(self, summary: Optional[Dict[str, Any]], raw_data: Optional[Dict[str, Any]] = None):
        """
        Handle conversation summaries for analytics and improvement.
        
        This is called at the end of conversations and can be used
        for logging, analytics, or triggering follow-up actions.
        """
        
        if summary:
            # Log successful recipe assistance for analytics
            logging.info(f"Recipe conversation completed: {summary}")
            
            # Could implement features like:
            # - Sending recipe cards via SMS
            # - Adding recipes to user's saved collection
            # - Scheduling follow-up calls for cooking results
            # - Analytics tracking for popular recipes
            
        super().on_summary(summary, raw_data)

def main():
    """
    Main entry point for the recipe agent application.
    
    This function initializes and runs the agent, with proper
    error handling and environment validation.
    """
    
    # Validate required environment variables
    required_env_vars = ["SPOONACULAR_API_KEY"]
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    
    if missing_vars:
        print("Warning: Missing environment variables:", ", ".join(missing_vars))
        print("Some features may not work correctly without proper API keys.")
        print("Please set the following environment variables:")
        for var in missing_vars:
            print(f"  export {var}=your_api_key_here")
    
    # Set up logging for development and debugging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        # Initialize and run the advanced recipe agent
        agent = AdvancedRecipeAgent()
        
        print("🍳 Advanced Recipe Agent starting...")
        print("Ready to help with all your cooking needs!")
        print("Call your SignalWire number to begin cooking!")
        
        # Run the agent - this will auto-detect the deployment environment
        agent.run()
        
    except KeyboardInterrupt:
        print("\n👋 Recipe agent shutting down gracefully...")
    except Exception as e:
        logging.error(f"Failed to start recipe agent: {e}")
        raise

if __name__ == "__main__":
    main()
