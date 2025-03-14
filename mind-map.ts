const group = {
    "id": "uuid",
    "answer": "clone",
    "difficulty": 1,
    "hint": "a copy of something",
    "images": [
        {
            "tag": "cloud",
            "start_index": 0,
            "end_index": 3
        },
        {
            "tag": "tone",
            "start_index": 2,
            "end_index": 4
        }
    ]
}

const user = {
    "username": "john_doe",
    "password": "1234",
    "created_at": "2023-10-01T12:00:00Z"
}


const image = {
    "id": "uuid string",
    "tag": "cloud",
    "url": "s3-url",
}




// endpoint for uploading images
// endpoint for uploading groups
// endpoint for retrieving groups
// sign up. just username
// record each attempts 
// add timeframe so one cannot play forever

const attempt = {
    "user": 1,
    "time_started": "23:00",
    "time_ended": "00:00",
    "score": 20,
    "questions": [
        {
           "question": 1,
           "success": true    
        },
        {
            "question": 2,
            "success": false
        }
    ]
}


// complete a sprint: answer 5 in 10 seconds
// mode: Soft. Hard
// contiguous words can be reversed