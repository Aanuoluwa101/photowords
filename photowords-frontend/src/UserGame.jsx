import React, { useState, useEffect } from "react";
import axios from "axios";

const baseUrl = process.env.REACT_APP_API_BASE_URL;
const cloudFrontBaseUrl = process.env.REACT_APP_CLOUD_FRONT_BASE_URL;

const CLOUD_FRONT_URL = `${cloudFrontBaseUrl}/images`;
const PLAY_ENDPOINT = `${baseUrl}/play`;

export default function UserGame() {
  const [username, setUsername] = useState("");
  const [gameData, setGameData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [userAnswer, setUserAnswer] = useState("");
  const [feedback, setFeedback] = useState("");
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [showAnswer, setShowAnswer] = useState(false);
  const [correctCount, setCorrectCount] = useState(0);
  const [answers, setAnswers] = useState([]);
  const [startTime, setStartTime] = useState(null);
  const [submitted, setSubmitted] = useState(false);

  useEffect(() => {
    if (gameData) {
      setStartTime(Date.now());
    }
  }, [currentQuestionIndex, gameData]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const res = await axios.post(PLAY_ENDPOINT, { username });
      setGameData(res.data.game_attempt);
      setCurrentQuestionIndex(0);
      resetRound();
    } catch (err) {
      setError("Something went wrong.");
    } finally {
      setLoading(false);
    }
  };

  const resetRound = () => {
    setFeedback("");
    setUserAnswer("");
    setShowAnswer(false);
    setSubmitted(false);
    setStartTime(Date.now());
  };

  const checkAnswer = () => {
    if (!userAnswer.trim()) return;

    const correctAnswer = gameData.questions[
      currentQuestionIndex
    ].answer.trim().toLowerCase();
    const givenAnswer = userAnswer.trim().toLowerCase();

    if (givenAnswer === correctAnswer) {
      setFeedback("✅ Correct!");
      setCorrectCount((prev) => prev + 1);
    } else {
      setFeedback("❌ Incorrect. Try again or reveal the answer.");
    }

    const timeTaken = Math.floor((Date.now() - startTime) / 1000);

    const answerEntry = {
      question_id: gameData.questions[currentQuestionIndex].id,
      guesses: [givenAnswer],
      time_taken: timeTaken,
    };

    setAnswers((prev) => [...prev, answerEntry]);
    setSubmitted(true);
  };

  const handleNext = async () => {
    const isLastQuestion =
      currentQuestionIndex >= gameData.questions.length - 1;

    if (isLastQuestion) {
      const finishUrl = `${PLAY_ENDPOINT}/finish/${gameData.id}`;
      const now = Date.now();
      const totalTimeTaken = Math.floor((now - startTime) / 1000);

      const requestBody = { time_taken: totalTimeTaken, answers };

      try {
        await axios.post(finishUrl, requestBody);
        alert(
          `Game Over! 🎉 You got ${correctCount} out of ${gameData.questions.length} correct.`
        );
        handleExit();
      } catch (err) {
        const errorMessage =
          err.response?.data?.error || "An unexpected error occurred.";
        console.error("Error submitting game results:", errorMessage);
      }
    } else {
      setCurrentQuestionIndex((prev) => prev + 1);
      resetRound();
    }
  };

  const handleExit = () => {
    setGameData(null);
    setUsername("");
    setFeedback("");
    setUserAnswer("");
    setCurrentQuestionIndex(0);
    setShowAnswer(false);
    setCorrectCount(0);
    setAnswers([]);
    setStartTime(null);
    setSubmitted(false);
  };

  const toggleShowAnswer = () => {
    setShowAnswer((prev) => !prev);
    setSubmitted(true); // reveal tags when answer is revealed
  };

  return (
    <div className="p-6 max-w-2xl mx-auto bg-white rounded-xl shadow-md">
      <h1 className="text-3xl font-bold mb-6 text-center">📸 Photowords</h1>

      {!gameData ? (
        <form
          onSubmit={handleSubmit}
          className="space-y-4 bg-gray-50 p-4 rounded shadow"
        >
          <input
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            placeholder="Enter your username"
            className="w-full p-2 border rounded focus:ring focus:ring-blue-300"
            required
          />
          <button
            type="submit"
            className="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700 transition"
            disabled={loading}
          >
            {loading ? "Loading..." : "Start Game"}
          </button>
          {error && <p className="text-red-500 text-sm">{error}</p>}
        </form>
      ) : (
        <div>
          <h2 className="text-xl font-semibold mb-2">
            Welcome, {gameData.username}!
          </h2>
          <button
            onClick={handleExit}
            className="text-sm text-red-500 underline mb-4"
          >
            Exit Game
          </button>

          {gameData.questions.length > 0 && (
            <div className="mb-6">
              <p className="mb-3">
                Hint:{" "}
                <strong>{gameData.questions[currentQuestionIndex].hint}</strong>
              </p>

              {/* Images (tags hidden until submitted or showAnswer true) */}
              <div className="flex flex-wrap gap-4 mb-4">
                {gameData.questions[currentQuestionIndex].images.map(
                  (img, index) => (
                    <div
                      key={index}
                      className="flex flex-col items-center border rounded-lg shadow p-2 bg-gray-50"
                    >
                      <img
                        src={`${CLOUD_FRONT_URL}/${img.tag}`}
                        alt={img.tag}
                        className="w-32 h-32 object-cover rounded"
                      />
                      {submitted || showAnswer ? (
                        <span className="text-sm mt-1 text-gray-700">
                          {img.tag}
                        </span>
                      ) : (
                        <span className="text-sm mt-1 text-gray-400 italic">
                          Hidden
                        </span>
                      )}
                    </div>
                  )
                )}
              </div>

              {/* Answer Input */}
              <div className="space-y-3">
                <input
                  type="text"
                  value={userAnswer}
                  onChange={(e) => setUserAnswer(e.target.value)}
                  placeholder="Your answer..."
                  className="w-full p-2 border rounded focus:ring focus:ring-green-300"
                />
                <div className="flex flex-wrap gap-2">
                  <button
                    onClick={checkAnswer}
                    className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 transition"
                  >
                    Submit Answer
                  </button>
                  <button
                    onClick={toggleShowAnswer}
                    className="bg-yellow-500 text-white px-4 py-2 rounded hover:bg-yellow-600 transition"
                  >
                    {showAnswer ? "Hide Answer" : "Show Answer"}
                  </button>
                  <button
                    onClick={handleNext}
                    className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 transition"
                  >
                    {currentQuestionIndex === gameData.questions.length - 1
                      ? "Finish"
                      : "Next"}
                  </button>
                </div>

                {feedback && (
                  <p
                    className={`mt-2 font-semibold ${
                      feedback.includes("✅")
                        ? "text-green-600"
                        : "text-red-600"
                    }`}
                  >
                    {feedback}
                  </p>
                )}

                {showAnswer && (
                  <p className="text-sm text-gray-600">
                    Correct Answer:{" "}
                    <strong>
                      {gameData.questions[currentQuestionIndex].answer}
                    </strong>
                  </p>
                )}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
