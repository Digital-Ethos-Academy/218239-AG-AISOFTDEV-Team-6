import pydantic
from datetime import date
from typing import List, Dict, Optional

# Ensure Pydantic v2 is used if available, otherwise this works with v1 too.
# For v1, you might need to inherit from pydantic.BaseModel directly.
BaseModel = pydantic.BaseModel
Field = pydantic.Field

# --- Component Models for PRD Sections ---

class UserPersona(BaseModel):
    """Represents a user persona affected by the problem."""
    name: str = Field(..., description="The title or name of the persona (e.g., 'The New Hire').")
    scenario: str = Field(..., description="A typical scenario the persona faces that highlights the problem.")

class ProblemDefinition(BaseModel):
    """Details the pain points and user personas this product addresses."""
    problem_statement: str = Field(..., description="A clear and concise description of the primary problem.")
    user_personas: List[UserPersona] = Field(..., description="A list of key user personas affected by this problem.")

class SuccessMetric(BaseModel):
    """Defines a specific, measurable outcome for the product."""
    goal: str = Field(..., description="The high-level objective.")
    kpi: str = Field(..., alias="Key Performance Indicator (KPI)", description="The KPI to measure the goal.")
    target: str = Field(..., description="The specific target value or outcome for the KPI.")

class AcceptanceCriterion(BaseModel):
    """Defines the 'Given-When-Then' conditions for a user story to be considered 'done'."""
    given: str = Field(..., description="The initial context or precondition.")
    when: str = Field(..., description="The action taken by the user.")
    then: str = Field(..., description="The expected outcome or result.")

class UserStory(BaseModel):
    """Describes a feature from an end-user's perspective."""
    story_id: str = Field(..., description="A unique identifier for the story (e.g., '1.1').")
    description: str = Field(..., description="The user story in the format 'As a [persona], I want to [action], so that [benefit]'.")
    acceptance_criteria: List[AcceptanceCriterion] = Field(default_factory=list)

class Epic(BaseModel):
    """A large body of work that can be broken down into smaller user stories."""
    name: str = Field(..., description="The name of the epic (e.g., 'User Authentication').")
    user_stories: List[UserStory] = Field(default_factory=list)

class NonFunctionalRequirements(BaseModel):
    """Defines the quality attributes of the system."""
    performance: Optional[str] = Field(None, description="Requirements for system responsiveness and load times.")
    security: Optional[str] = Field(None, description="Requirements for data protection, authentication, and authorization.")
    accessibility: Optional[str] = Field(None, description="Requirements for usability by people with disabilities (e.g., WCAG compliance).")
    scalability: Optional[str] = Field(None, description="Requirements for handling load and concurrent users.")
    other: Optional[Dict[str, str]] = Field(default_factory=dict, description="A dictionary for any other NFRs not covered above.")

class Milestone(BaseModel):
    """Represents a key point in the project's release plan."""
    version: str = Field(..., description="The name or version of the release (e.g., 'Version 1.0 (MVP)').")
    target_date: date = Field(..., description="The target delivery date for this milestone.")
    description: str = Field(..., description="A summary of the features included in this release.")

class ScopeDefinition(BaseModel):
    """Clarifies what is and is not included in the project to manage expectations."""
    out_of_scope: List[str] = Field(..., description="A list of features or functionalities that will explicitly not be built in this version.")
    future_work: List[str] = Field(..., description="A list of potential future features or enhancements to consider later.")

class Appendix(BaseModel):
    """A place for tracking dependencies, assumptions, and open questions."""
    open_questions: List[str] = Field(default_factory=list)
    dependencies: List[str] = Field(default_factory=list)


# --- Main ProductRequirementsDocument Class ---

class ProductRequirementsDocument(BaseModel):
    """
    Represents the complete structure of a Product Requirements Document (PRD),
    modeling all key sections from a standard template.
    """
    product_name: str = Field(..., description="The name of the product this PRD is for.")
    status: str = Field("Draft", description="The current status of the document (e.g., Draft, In Review, Approved).")
    author: str = Field(..., description="The name of the author or team responsible for the PRD.")
    version: float = Field(1.0, description="The version number of the document.")
    last_updated: date = Field(..., description="The date the document was last updated.")

    executive_summary: str = Field(
        ...,
        description="A high-level overview of the product, its purpose, the problem it solves, and the vision for success."
    )

    problem_definition: ProblemDefinition = Field(
        ...,
        description="A detailed look at the pain points this product will solve."
    )

    success_metrics: List[SuccessMetric] = Field(
        ...,
        description="A list of specific, measurable outcomes to define success."
    )

    functional_requirements: List[Epic] = Field(
        default_factory=list,
        description="The core of the PRD, detailing what the product must do, broken down into epics and user stories."
    )

    non_functional_requirements: NonFunctionalRequirements = Field(
        ...,
        description="The quality attributes of the system, such as performance, security, and accessibility."
    )

    release_plan: List[Milestone] = Field(
        ...,
        description="A high-level timeline for delivery, broken down into milestones."
    )

    scope: ScopeDefinition = Field(
        ...,
        description="Clarifies what is in and out of scope to manage expectations and prevent scope creep."
    )

    appendix: Appendix = Field(
        default_factory=Appendix,
        description="A place to track dependencies, assumptions, and open questions."
    )

    class Config:
        """Pydantic model configuration."""
        # For Pydantic v2:
        json_schema_extra = {
            "example": {
                "product_name": "New Hire Onboarding Platform",
                "status": "Draft",
                "author": "Product Team Alpha",
                "version": 1.0,
                "last_updated": "2023-10-27",
                "executive_summary": "This product is a centralized web platform designed to streamline the onboarding process for new hires. By consolidating tasks, documents, and introductions, we aim to reduce administrative overhead and help new employees become productive faster. The ultimate vision is to create a welcoming and efficient onboarding experience that sets a positive tone for the entire employee lifecycle.",
                "problem_definition": {
                    "problem_statement": "New hires currently face a fragmented and overwhelming onboarding experience, leading to decreased initial productivity and a high volume of repetitive questions to HR and managers.",
                    "user_personas": [
                        {"name": "The New Hire", "scenario": "Alex, a new software engineer, is unsure where to find company policy documents and who to ask for access to development tools, delaying their first project contribution."},
                        {"name": "The Hiring Manager", "scenario": "Sarah, a department head, spends hours each week answering the same set of questions from different new hires, taking time away from her core responsibilities."},
                    ]
                },
                "success_metrics": [
                    {"goal": "Improve New Hire Efficiency", "Key Performance Indicator (KPI)": "Reduce time-to-first-contribution", "target": "Decrease by 20% in Q1"},
                    {"goal": "Reduce Support Load", "Key Performance Indicator (KPI)": "Decrease repetitive questions to HR", "target": "30% reduction in support tickets"},
                ],
                "functional_requirements": [
                    {
                        "name": "User Authentication",
                        "user_stories": [
                            {
                                "story_id": "1.1",
                                "description": "As a New Hire, I want to log in with my company credentials, so that I can access the onboarding platform securely.",
                                "acceptance_criteria": [
                                    {"given": "I am on the login page", "when": "I enter my valid SSO credentials", "then": "I am redirected to my personal dashboard."},
                                    {"given": "I am on the login page", "when": "I enter invalid credentials", "then": "I see a clear error message."}
                                ]
                            }
                        ]
                    }
                ],
                "non_functional_requirements": {
                    "performance": "The application must load in under 3 seconds on a standard corporate network connection.",
                    "security": "All data must be encrypted in transit and at rest. The system must comply with company SSO policies.",
                    "accessibility": "The user interface must be compliant with WCAG 2.1 AA standards.",
                    "scalability": "The system must support up to 500 concurrent users during peak onboarding seasons."
                },
                "release_plan": [
                    {"version": "Version 1.0 (MVP)", "target_date": "2024-03-31", "description": "Core features including user login, task checklist, and document repository."},
                    {"version": "Version 1.1", "target_date": "2024-05-31", "description": "Mentorship connection and team introduction features."}
                ],
                "scope": {
                    "out_of_scope": [
                        "Direct integration with third-party HR payroll systems.",
                        "A native mobile application (the web app will be mobile-responsive).",
                    ],
                    "future_work": [
                        "Integration with the corporate Learning Management System (LMS).",
                        "AI-powered personalized learning paths for new hires."
                    ]
                },
                "appendix": {
                    "open_questions": ["Which team will be responsible for maintaining the content in the document repository?"],
                    "dependencies": ["The final UI design mockups are required from the Design team by 2024-01-15."]
                }
            }
        }
        # For Pydantic v1, you would use schema_extra as a static method:
        # @staticmethod
        # def schema_extra(schema: dict, model: type):
        #     schema["example"] = { ... }

# Example of how to create an instance of the class
if __name__ == '__main__':
    # You can populate the PRD using the example data from the model's config
    example_data = ProductRequirementsDocument.Config.json_schema_extra["example"]
    
    try:
        prd_instance = ProductRequirementsDocument(**example_data)

        # Print the validated data as a nicely formatted JSON string
        print(prd_instance.json(indent=2))

        # Accessing a specific field
        print("\n--- Example of accessing a field ---")
        print(f"Product Name: {prd_instance.product_name}")
        print(f"First Goal: {prd_instance.success_metrics[0].goal}")

    except pydantic.ValidationError as e:
        print("There was a validation error:")
        print(e)