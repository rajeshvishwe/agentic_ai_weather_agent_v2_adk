"""
Mapper between domain models and API schemas.
"""

from weather_intelligence_agent_v2.models.weather_planning import (
    WeatherPlanning,
)

from weather_intelligence_agent_v2.schemas.weather_planning_schema import (
    WeatherPlanningResponse,
)


class WeatherPlanningMapper:
    """
    Converts WeatherPlanning domain models
    into WeatherPlanningResponse API models.
    """

    @staticmethod
    def to_response(
        planning: WeatherPlanning,
    ) -> WeatherPlanningResponse:
        """
        Convert domain model into response schema.
        """

        return WeatherPlanningResponse.model_validate(
            planning
        )