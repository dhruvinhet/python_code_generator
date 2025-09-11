import React, { useState } from 'react';

const QuizSettings = ({ onGenerateQuiz }) => {
  const [quizType, setQuizType] = useState('MCQ');
  const [numQuestions, setNumQuestions] = useState(5);
  const [difficulty, setDifficulty] = useState('Medium');
  const handleSubmit = (e) => {
    e.preventDefault();
    onGenerateQuiz(quizType, numQuestions, difficulty);
  };
  return (
    <div className="flex flex-col items-center p-4 w-full">
      <h2 className="text-white text-2xl font-bold mb-4">Quiz Settings</h2>
      <form onSubmit={handleSubmit} className="w-full max-w-sm flex flex-col gap-4">
        <select className="bg-[#2d2938] text-white p-3 rounded-lg border-0 focus:ring-2 focus:ring-[#7847eb]" value={quizType} onChange={(e) => setQuizType(e.target.value)}>
          <option value="MCQ">Multiple Choice Questions</option>
          <option value="Theoretical">Short Theoretical Questions</option>
        </select>
        <input type="number" min="1" max="20" value={numQuestions} onChange={(e) => setNumQuestions(parseInt(e.target.value))} className="bg-[#2d2938] text-white p-3 rounded-lg border-0 focus:ring-2 focus:ring-[#7847eb]" />
        <select className="bg-[#2d2938] text-white p-3 rounded-lg border-0 focus:ring-2 focus:ring-[#7847eb]" value={difficulty} onChange={(e) => setDifficulty(e.target.value)}>
          <option value="Easy">Easy</option>
          <option value="Medium">Medium</option>
          <option value="Hard">Hard</option>
        </select>
        <button type="submit" className="bg-[#7847eb] hover:bg-[#5b36b2] text-white px-4 py-2 rounded-lg font-bold">Generate Quiz</button>
      </form>
    </div>
  );
};

export default QuizSettings;
