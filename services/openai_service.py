import openai
import logging
from typing import List
from cachetools import cached, TTLCache
from config import Config

class OpenAIService:
    def __init__(self, api_key: str, model: str):
        if not Config.ENABLE_OPENAI_SERVICE:
            logging.info('OpenAI service is disabled.')
            return

        openai.api_key = api_key
        self.client = openai
        self.model = model
        self.logger = logging.getLogger(__name__)
        self.cache = TTLCache(maxsize=100, ttl=300)  # Cache results for 5 minutes

    def generate_report_content(self, industry: str, answers: List[str]) -> str:
        if not Config.ENABLE_OPENAI_SERVICE:
            logging.info('OpenAI service is disabled. Skipping report content generation.')
            return ""

        try:
            # Construct the prompt
            prompt = self.build_prompt(industry, answers)

            self.logger.debug('Generating report content with OpenAI')
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1500
            )
            report_content = response.choices[0].message.content
            self.logger.info('Report content generated successfully')

            # Extract HTML content from the response
            html_body_content = self.extract_html(report_content)
            self.logger.info('HTML content extracted from the response')

            # Inject CSS styles into the HTML content
            styled_html_content = self.inject_styles(html_body_content)

            return styled_html_content
        except Exception as e:
            self.logger.error(f'Error generating report content: {e}', exc_info=True)
            return ""

    def inject_styles(self, html_content: str) -> str:
        """Injects CSS styles into the HTML content."""
        styles = """
        <style>
        body {
            font-family: Arial, sans-serif;
            color: #333;
            line-height: 1.6;
            margin: 0;
            padding: 0;
            background-color: #f4f4f4;
        }
        .container {
            width: 80%;
            margin: auto;
            overflow: hidden;
            background: #fff;
            padding: 20px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
        }
        header {
            background-color: #4CAF50;
            color: #fff;
            padding: 10px 0;
            text-align: center;
        }
        header img {
            width: 150px;
            margin: 0 auto;
        }
        h1, h2 {
            color: #4CAF50;
        }
        section {
            margin: 20px 0;
        }
        .cta {
            margin: 40px 0;
            padding: 20px;
            background-color: #e7f7e7;
            text-align: center;
            border: 2px solid #4CAF50;
        }
        .cta a {
            color: #fff;
            background-color: #4CAF50;
            padding: 10px 20px;
            text-decoration: none;
            font-weight: bold;
            border-radius: 5px;
        }
        footer {
            text-align: center;
            margin-top: 20px;
            padding: 10px 0;
            background-color: #333;
            color: #fff;
            position: relative;
            bottom: 0;
            width: 100%;
        }
        footer p {
            margin: 0;
        }
        </style>
        """
        return f"<html><head>{styles}</head>{html_content}</html>"


    def build_prompt(self, industry: str, answers: List[str]) -> str:
        return f"""
        You are an AI consultant preparing a comprehensive report for a business owner in the {industry} industry. The report must be detailed, insightful, and structured into the following sections:

        1. **Introduction**: Provide a brief overview of the business's context based on the industry.
        2. **Industry Trends**: Provide the latest AI trends in the {industry} industry.
        3. **AI Solutions**: Offer AI-driven solutions for the following business needs:
            - Current data management and utilization challenges: {answers[0]}
            - Areas of technology integration and inefficiency: {answers[1]}
            - Long-term business goals and AI's role in achieving them: {answers[2]}
        4. **Analysis and Recommendations**:
            - Include a detailed analysis of how AI can address the specific challenges mentioned.
            - Offer actionable recommendations for AI implementation.
        5. **Conclusion**: Summarize the key insights and recommend next steps.

        Ensure the report is structured professionally, with clear headings and well-organized content. Also, include a call-to-action encouraging the business owner to engage with Daley Mottley AI Consulting for further AI consulting services.

        The report should be in the following format embedded in HTML code with the brackets filled in with the appropraite content:

        ## Format
        ```
        <body>
            <header>
                <img src="{{ url_for('static', filename='images/logo.png') }}" alt="Daley Mottley AI Consulting">
                <h1>AI Insights Report</h1>
            </header>

            <div class="container">
                <section>
                    <h2>Introduction</h2>
                    <p>{{ introduction }}</p>
                </section>

                <section>
                    <h2>Industry Trends</h2>
                    <p>{{ industry_trends }}</p>
                </section>

                <section>
                    <h2>AI Solutions</h2>
                    <p>{{ ai_solutions }}</p>
                </section>

                <section>
                    <h2>Analysis</h2>
                    <p>{{ analysis }}</p>
                </section>

                <section>
                    <h2>Conclusion</h2>
                    <p>{{ conclusion }}</p>
                </section>

                <section class="cta">
                    <h2>Ready to Implement AI in Your Business?</h2>
                    <p>Contact Daley Mottley AI Consulting for expert guidance on how AI can transform your business. Let us help you stay ahead of the competition with cutting-edge AI solutions.</p>
                    <a href="daley.mottley@hotmail.com">Contact Us Today</a>
                </section>
            </div>

            <footer>
                <p>Daley Mottley AI Consulting | All Rights Reserved &copy; {{ current_year }}</p>
            </footer>
        </body>
        ```
        """

    def extract_html(self, content: str) -> str:
        """
        Extracts HTML content from the OpenAI response.
        Assumes the content is wrapped in a ```html block.
        """
        start = content.find("<body>")
        end = content.find("</body>") + len("</body>")
        if start == -1 or end == -1:
            self.logger.error("HTML content not found in the response")
            return content  # Fallback to returning the whole content
        return content[start:end]

