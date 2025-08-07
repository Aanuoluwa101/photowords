import React, { useState, useEffect } from 'react';
import axios from 'axios';

const CLOUD_FRONT_URL = 'https://d26z1cm3nkb7ze.cloudfront.net/images';
const PLAY_ENDPOINT = 'https://1xcn1oc7x7.execute-api.eu-west-2.amazonaws.com/dev/play';

export default function UserGame() {
  const [username, setUsername] = useState('');
  const [gameData, setGameData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [userAnswer, setUserAnswer] = useState('');
  const [feedback, setFeedback] = useState('');
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [showAnswer, setShowAnswer] = useState(false);
  const [correctCount, setCorrectCount] = useState(0);
  const [answers, setAnswers] = useState([]);
  const [startTime, setStartTime] = useState(null);

  useEffect(() => {
    if (gameData) {
      setStartTime(Date.now());
    }
  }, [currentQuestionIndex]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const res = await axios.post(PLAY_ENDPOINT, { username });
      setGameData(res.data.game_attempt);
      setCurrentQuestionIndex(0);
      setFeedback('');
      setUserAnswer('');
      setShowAnswer(false);
      setCorrectCount(0);
      setAnswers([]);
      setStartTime(Date.now());
    } catch (err) {
      setError('Something went wrong.');
    } finally {
      setLoading(false);
    }
  };

  const checkAnswer = () => {
    const correctAnswer = gameData.questions[currentQuestionIndex].answer.trim().toLowerCase();
    const givenAnswer = userAnswer.trim().toLowerCase();

    if (givenAnswer === correctAnswer) {
      setFeedback('✅ Correct!');
      setCorrectCount((prev) => prev + 1);
    } else {
      setFeedback('❌ Incorrect. Try again!');
    }

    const timeTaken = Math.floor((Date.now() - startTime) / 1000); // seconds

    const answerEntry = {
      question_id: gameData.questions[currentQuestionIndex].id,
      guesses: [givenAnswer],
      time_taken: timeTaken,
    };

    setAnswers((prev) => [...prev, answerEntry]);
  };

const handleNext = async () => {
  const isLastQuestion = currentQuestionIndex >= gameData.questions.length - 1;

  if (isLastQuestion) {
    const finishUrl = `${PLAY_ENDPOINT}/finish/${gameData.id}`;
    const now = Date.now();
    const totalTimeTaken = Math.floor((now - startTime) / 1000); // in seconds

    const requestBody = {
      time_taken: totalTimeTaken,
      answers,
    };

    // console.log('Submitting game results:', requestBody);

    try {
      await axios.post(finishUrl, requestBody);
      alert(`You got ${correctCount} out of ${gameData.questions.length} correct.`);
      handleExit();
    } catch (err) {
      const errorMessage = err.response?.data?.error || 'An unexpected error occurred.';
      console.error('Error submitting game results:', errorMessage);
    }
  } else {
    setCurrentQuestionIndex((prev) => prev + 1);
    setFeedback('');
    setUserAnswer('');
    setShowAnswer(false);
    setStartTime(Date.now());
  }
};



  const handleExit = () => {
    setGameData(null);
    setUsername('');
    setFeedback('');
    setUserAnswer('');
    setCurrentQuestionIndex(0);
    setShowAnswer(false);
    setCorrectCount(0);
    setAnswers([]);
    setStartTime(null);
  };

  const toggleShowAnswer = () => {
    setShowAnswer(!showAnswer);
  };

  return (
    <div className="p-4 max-w-xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">Play Photowords</h1>
      {!gameData ? (
        <form onSubmit={handleSubmit} className="space-y-4">
          <input
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            placeholder="Enter your username"
            className="w-full p-2 border rounded"
            required
          />
          <button
            type="submit"
            className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
            disabled={loading}
          >
            {loading ? 'Loading...' : 'Start Game'}
          </button>
          {error && <p className="text-red-500">{error}</p>}
        </form>
      ) : (
        <div>
          <h2 className="text-xl font-semibold mb-2">Welcome, {gameData.username}!</h2>
          <button onClick={handleExit} className="text-sm text-red-500 underline mb-4">Exit Game</button>

          {gameData.questions.length > 0 && (
            <div className="mb-6">
              <p className="mb-2">Hint: <strong>{gameData.questions[currentQuestionIndex].hint}</strong></p>
              <div className="flex gap-4 mb-4">
                {gameData.questions[currentQuestionIndex].images.map((img, index) => (
                  <div key={index} className="flex flex-col items-center">
                    <img
                      src={`${CLOUD_FRONT_URL}/${img.tag}`}
                      alt={img.tag}
                      className="w-32 h-32 object-cover border rounded"
                    />
                    <span className="text-sm mt-1">{img.tag}</span>
                  </div>
                ))}
              </div>
              <div className="space-y-2">
                <input
                  type="text"
                  value={userAnswer}
                  onChange={(e) => setUserAnswer(e.target.value)}
                  placeholder="Your answer..."
                  className="w-full p-2 border rounded"
                />
                <div className="flex gap-2">
                  <button
                    onClick={checkAnswer}
                    className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700"
                  >
                    Submit Answer
                  </button>
                  <button
                    onClick={toggleShowAnswer}
                    className="bg-yellow-500 text-white px-4 py-2 rounded hover:bg-yellow-600"
                  >
                    {showAnswer ? 'Hide Answer' : 'Show Answer'}
                  </button>
                  <button
                    onClick={handleNext}
                    className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
                  >
                    Next
                  </button>
                </div>
                {feedback && <p className="mt-2 font-semibold">{feedback}</p>}
                {showAnswer && (
                  <p className="text-sm text-gray-600">Correct Answer: <strong>{gameData.questions[currentQuestionIndex].answer}</strong></p>
                )}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
