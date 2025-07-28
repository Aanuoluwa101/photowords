# CreateGroup 
CreateGroup = {
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "GroupPayload",
  "type": "object",
  "properties": {
    "answer": {
      "type": "string",
      "minLength": 1
    },
    "difficulty": {
      "type": "string",
      "enum": ["EASY", "MEDIUM", "HARD"]
    },
    "hint": {
      "type": "string",
      "minLength": 1
    },
    "images": {
      "type": "array",
      "minItems": 2,
      "items": {
        "type": "object",
        "properties": {
          "tag": {
            "type": "string",
            "minLength": 1
          },
          "start_index": {
            "type": "integer",
            "minimum": 0
          },
          "end_index": {
            "type": "integer",
            "minimum": 0
          },
          "position": {
            "type": "integer",
            "minimum": 0
          }
        },
        "required": ["tag", "start_index", "end_index", "position"],
        "additionalProperties": false
      }
    }
  },
  "required": ["answer", "difficulty", "hint", "images"],
  "additionalProperties": false
}


# GameAttemptCreate 
GameAttemptCreate = {
  "type": "object",
  "properties": {
    "username": {
      "type": "string",
      "minLength": 3,
      "maxLength": 30,
      "pattern": "^[a-zA-Z0-9_]+$"
    },
    "count": {
      "type": "number",
      "minimum": 1,
      "exclusiveMinimum": true
    }
  },
  "required": ["username"],
  "additionalProperties": false
}


# GameAttemptFinish
GameAttemptFinish = {
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "GameAttemptSubmission",
  "type": "object",
  "properties": {
    "time_taken": {
      "type": "number",
      "minimum": 0
    },
    "time_requested": {
      "type": "number",
      "minimum": 0
    },
    "answers": {
      "type": "array",
      "minItems": 0,
      "items": {
        "type": "object",
        "properties": {
          "question_id": {
            "type": "string",
            "minLength": 1
          },
          "guesses": {
            "type": "array",
            "minItems": 1,
            "items": {
              "type": "string",
              "minLength": 1
            }
          },
          "time_taken": {
            "type": "number",
            "minimum": 0
          }
        },
        "required": ["question_id", "guesses", "time_taken"],
        "additionalProperties": false
      }
    }
  },
  "required": ["time_taken", "answers"],
  "additionalProperties": false
}
