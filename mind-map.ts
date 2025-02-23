const group = {
    "answer": "clone",
    "difficulty": 1,
    "hint": "a copy of something",
    "images": [
        {
            "url": "https://example.com/image1.jpg",
            "tag": "cloud",
            "start_index": 0,
            "end_index": 3
        },
        {
            "url": "https://example.com/image1.jpg",
            "tag": "tone",
            "start_index": 2,
            "end_index": 4
        }
    ]
}


const image = {
    "id": 2,
    "tag": "cloud",
    "url": "https://example.com/image1.jpg",
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