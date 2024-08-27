import logging
import os
import google.generativeai as genai

class GeminiModel:
    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("API key not found. Please set the GEMINI_API_KEY environment variable.")
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
        logging.info("GeminiModel initialized.")

    def create_prompt(self, responses, num_days, inferred_season):
        logging.debug(f"Creating prompt with responses: {responses}, num_days: {num_days}, inferred_season: {inferred_season}")
        prompt = (
            "You are an experienced travel consultant specialized in creating comprehensive travel checklists for trips in Pakistan. "
            "Based on the provided details, generate a detailed and practical checklist for the traveler. "
            "The checklist should include essential items to pack, travel documents, health & safety tips, and other recommended items based on the location, season, and trip duration. "
            "Here are the details:\n"
            f"**Destination**: {responses['destination']}\n"
            f"**Start Date**: {responses['start_date']}\n"
            f"**Number of Nights**: {responses['nights']}\n"
            f"**Number of Days**: {num_days}\n"
            f"**Inferred Season**: {inferred_season}\n"
            f"**Trip Type**: {responses['trip_type']} (Adventure or Leisure)\n"
            f"**Group Size**: {responses['group_size']}\n"
            f"**Special Considerations**: {responses['special_considerations']}\n"
            "Ensure the checklist covers the following:\n"
            "1. **Packing List**: Include items specific to the season and activities planned.\n"
            "2. **Travel Documents**: List essential documents needed for the trip.\n"
            "3. **Health & Safety**: Provide health and safety recommendations based on the location and season.\n"
            "4. **Activity Essentials**: Recommend items necessary for the specific activities mentioned.\n"
            "5. **Miscellaneous**: Include any additional items that may be useful for the trip.\n"
            "Ensure the checklist is tailored to the specific needs and preferences of the traveler."
        )

        logging.debug(f"Prompt created: {prompt}")
        return prompt

    def generate_checklist(self, prompt):
        logging.debug(f"Generating checklist with prompt: {prompt}")
        try:
            response = self.model.generate_content(prompt)
            generated_text = response.text
            logging.info("Checklist generated successfully.")
            logging.debug(f"Model response: {generated_text}")

            # Check if the generated text is the same as the prompt and use a fallback if necessary
            if generated_text.strip() == prompt.strip():
                generated_text = (
                    "Oops! It seems we've reached our daily limit for generating checklists."
                )
            return generated_text
        except Exception as e:
            logging.error(f"Error generating checklist: {e}")
            raise
