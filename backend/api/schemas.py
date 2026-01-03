from marshmallow import Schema, fields, validates, validates_schema, ValidationError, post_load
from datetime import datetime, date, time
from typing import Dict, Any


class JourneyRequestSchema(Schema):
  """
  Schema for journey search request validation.

  Fields:
    source: Starting station code (string)
    destination: Ending station code (string)
    date: Journey date in YYYY-MM-DD format (string)
    departure_time: OPTIONAL - Earliest departure time in HH:MM format (string)
                    If not provided, uses smart defaults:
                    - If date is TODAY: current time
                    - If date is FUTURE: 00:00 (start of day)
    max_transfers: Maximum number of transfers allowed (integer, default=4)
  """
  source = fields.Str(required=True, error_messages={
    "required": "Source station is required",
    "invalid": "Source must be a string"
  })

  destination = fields.Str(required=True, error_messages={
    "required": "Destination station is required",
    "invalid": "Destination must be a string"
  })

  date = fields.Str(required=True, error_messages={
    "required": "Journey date is required",
    "invalid": "Date must be a string in YYYY-MM-DD format"
  })

  departure_time = fields.Str(
    allow_none=True,
    load_default=None,
    error_messages={
      "invalid": "Departure time must be a string in HH:MM format"
    }
  )

  max_transfers = fields.Int(
    load_default=4,
    error_messages={
      "invalid": "Max transfers must be an integer"
    }
  )

  @validates('source')
  def validate_source(self, value: str) -> None:
    """Validate source station code format."""
    if not value or not value.strip():
      raise ValidationError("Source station cannot be empty")
    if len(value.strip()) < 2:
      raise ValidationError("Source station code must be at least 2 characters")

  @validates('destination')
  def validate_destination(self, value: str) -> None:
    """Validate destination station code format."""
    if not value or not value.strip():
      raise ValidationError("Destination station cannot be empty")
    if len(value.strip()) < 2:
      raise ValidationError("Destination station code must be at least 2 characters")

  @validates('date')
  def validate_date(self, value: str) -> None:
    """
    Validate date format and ensure it's not in the past.
    Expected format: YYYY-MM-DD
    """
    try:
      date_obj = datetime.strptime(value, '%Y-%m-%d').date()
    except ValueError:
      raise ValidationError("Date must be in YYYY-MM-DD format (e.g., 2026-01-15)")

    # Check if date is today or in the future
    today = date.today()
    if date_obj < today:
      raise ValidationError(f"Date must be today or in the future. Today is {today.strftime('%Y-%m-%d')}")

  @validates('departure_time')
  def validate_departure_time(self, value: str) -> None:
    """
    Validate time format if provided.
    Expected format: HH:MM (24-hour format)
    """
    if value is None:
      return  # Optional field, None is valid

    try:
      time_obj = datetime.strptime(value, '%H:%M')
      hours = time_obj.hour
      minutes = time_obj.minute

      # Validate range
      if not (0 <= hours <= 23):
        raise ValidationError("Hour must be between 00 and 23")
      if not (0 <= minutes <= 59):
        raise ValidationError("Minute must be between 00 and 59")

    except ValueError:
      raise ValidationError("Departure time must be in HH:MM format (e.g., 14:30, 09:00)")

  @validates('max_transfers')
  def validate_max_transfers(self, value: int) -> None:
    """Validate max_transfers is a positive integer."""
    if value < 0:
      raise ValidationError("Max transfers must be a non-negative integer")
    if value > 10:
      raise ValidationError("Max transfers cannot exceed 10")

  @validates_schema
  def validate_source_destination(self, data: Dict[str, Any], **kwargs) -> None:
    """Validate that source and destination are different."""
    source = data.get('source', '').strip().upper()
    destination = data.get('destination', '').strip().upper()

    if source and destination and source == destination:
      raise ValidationError(
        "Source and destination stations must be different",
        field_name='destination'
      )

  @post_load
  def apply_smart_defaults(self, data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    """
    Apply smart defaults for departure_time based on the query date.

    Logic:
      - If departure_time provided: use it as-is (earliest departure preference)
      - If date is TODAY and no time: use current time
      - If date is FUTURE and no time: use 00:00 (all trains that day)
    """
    if data.get('departure_time') is None:
      query_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
      today = date.today()

      if query_date == today:
        # Use current time for today's searches
        current_time = datetime.now().time()
        data['departure_time'] = current_time.strftime('%H:%M')
        data['_time_source'] = 'current_time'  # For logging/debugging
      else:
        # Use start of day for future dates
        data['departure_time'] = '00:00'
        data['_time_source'] = 'start_of_day'  # For logging/debugging
    else:
      data['_time_source'] = 'user_provided'

    return data


class SegmentSchema(Schema):
  """Schema for a single journey segment."""
  route_id = fields.Str()
  train_number = fields.Str()
  train_name = fields.Str()
  category = fields.Str()
  train_class = fields.Str()
  boarding_stop_id = fields.Int()
  boarding_stop_code = fields.Str()
  boarding_stop_name = fields.Str()
  alighting_stop_id = fields.Int()
  alighting_stop_code = fields.Str()
  alighting_stop_name = fields.Str()
  departure_time = fields.Int()
  departure_day_offset = fields.Int()
  arrival_time = fields.Int()
  arrival_day_offset = fields.Int()
  duration = fields.Int()
  comfort_score = fields.Float()
  distance_km = fields.Float()
  fare = fields.Float()
  departure_time_formatted = fields.Str()
  arrival_time_formatted = fields.Str()
  duration_formatted = fields.Str()
  boarding_station_zone = fields.Str()
  boarding_station_tier = fields.Str()
  alighting_station_zone = fields.Str()
  alighting_station_tier = fields.Str()
  transfer_after = fields.Dict(allow_none=True)


class JourneySchema(Schema):
  """Schema for a complete journey."""
  segments = fields.List(fields.Nested(SegmentSchema))
  total_time = fields.Int()
  total_fare = fields.Float()
  total_transfers = fields.Int()
  comfort_score = fields.Float()
  num_segments = fields.Int()


class QueryMetadataSchema(Schema):
  """Schema for query metadata in response."""
  source = fields.Str()
  destination = fields.Str()
  date = fields.Str()
  departure_time = fields.Str()
  max_transfers = fields.Int()
  time_source = fields.Str(allow_none=True)  # Shows how departure_time was determined


class ResponseMetadataSchema(Schema):
  """Schema for response metadata."""
  query = fields.Nested(QueryMetadataSchema)
  results_count = fields.Int()


class JourneyResponseSchema(Schema):
  """
  Schema for journey search response.

  Structure:
    {
      "journeys": [<list of journey objects>],
      "metadata": {
        "query": {<original query parameters>},
        "results_count": <number of journeys found>
      }
    }
  """
  journeys = fields.List(fields.Nested(JourneySchema))
  metadata = fields.Nested(ResponseMetadataSchema)


class ErrorResponseSchema(Schema):
  """
  Schema for error responses.

  Structure:
    {
      "error": {
        "code": <HTTP status code>,
        "message": <error message>,
        "details": <optional detailed error information>
      }
    }
  """
  error = fields.Dict(keys=fields.Str(), values=fields.Raw())


# Schema instances for reuse
journey_request_schema = JourneyRequestSchema()
journey_response_schema = JourneyResponseSchema()
error_response_schema = ErrorResponseSchema()


def create_error_response(code: int, message: str, details: Any = None) -> Dict[str, Any]:
  """
  Create a standardized error response dictionary.

  Args:
    code: HTTP status code (400, 404, 500, etc.)
    message: Human-readable error message
    details: Optional detailed error information (validation errors, stack trace, etc.)

  Returns:
    Dictionary with error response structure
  """
  error_data = {
    "error": {
      "code": code,
      "message": message
    }
  }

  if details is not None:
    error_data["error"]["details"] = details

  return error_data


def create_success_response(
  journeys: list,
  query_params: Dict[str, Any]
) -> Dict[str, Any]:
  """
  Create a standardized success response dictionary.

  Args:
    journeys: List of journey dictionaries
    query_params: Original query parameters

  Returns:
    Dictionary with success response structure
  """
  # Extract time_source if present for metadata
  time_source = query_params.pop('_time_source', None)

  response_data = {
    "journeys": journeys,
    "metadata": {
      "query": {
        **query_params,
        "time_source": time_source
      },
      "results_count": len(journeys)
    }
  }

  return response_data
