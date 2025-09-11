import React from 'react';

const Results = ({ quizResults, analysis, quizData }) => {
  if (!quizResults || quizResults.length === 0) {
    return (
      <div className="flex flex-col items-center p-4 w-full">
        <h2 className="text-white text-2xl font-bold mb-4">Results</h2>
        <p className="text-[#a59db8]">No quiz results to display.</p>
      </div>
    );
  }
  const correctCount = quizResults.filter(q => q.evaluation.is_correct).length;
  const totalQuestions = quizResults.length;
  const score = Math.round((correctCount / totalQuestions) * 100);
  return (
    <div className="flex flex-col items-center p-4 w-full">
      <h2 className="text-white text-3xl font-bold mb-6">Quiz Results</h2>
      <div className="bg-[#2d2938] p-6 rounded-xl w-full max-w-2xl mb-6">
        <h3 className="text-white text-xl font-bold mb-2">Overall Performance</h3>
        <p className="text-[#a59db8] text-lg">
          You scored <strong className="text-white">{score}%</strong> ({correctCount} out of {totalQuestions} correct).
        </p>
      </div>
      <div className="w-full max-w-2xl">
        {quizResults.map((result, index) => {
          const originalQuestion = quizData ? quizData[index] : null;
          if (!originalQuestion) return null;
          const correctOptionLetter = originalQuestion.correct_answer;
          const userOptionLetter = result.userAnswer;
          const isCorrect = result.evaluation.is_correct;
          const questionText = originalQuestion.question;
          return (
            <div key={index} className="bg-[#1e1e1e] p-6 rounded-lg mb-4 shadow-md">
              <h4 className="text-white text-lg font-semibold mb-2">Question {index + 1}</h4>
              <p className="text-[#a59db8] mb-4">{questionText}</p>
              <div className="flex flex-col gap-2">
                {Object.entries(originalQuestion.options).map(([letter, text]) => {
                  const isUserAnswer = letter === userOptionLetter;
                  const isCorrectAnswer = letter === correctOptionLetter;
                  let optionClass = 'p-3 rounded-lg border';
                  let icon = null;
                  if (isUserAnswer && isCorrect) {
                    optionClass += ' bg-[#28a745] border-[#28a745]';
                    icon = '✅';
                  } else if (isUserAnswer && !isCorrect) {
                    optionClass += ' bg-[#dc3545] border-[#dc3545]';
                    icon = '❌';
                  } else if (isCorrectAnswer) {
                    optionClass += ' bg-[#28a745] border-[#28a745]';
                    icon = '✅';
                  } else {
                    optionClass += ' border-[#4d4957]';
                  }
                  return (
                    <div key={letter} className={optionClass}>
                      <p className="text-white">
                        <span className="font-bold mr-2">{letter})</span> {text} {icon}
                      </p>
                    </div>
                  );
                })}
              </div>
              {!isCorrect && result.evaluation.explanation && (
                <div className="mt-4 p-3 bg-[#3d3a49] rounded-lg">
                  <h5 className="text-white font-bold">Explanation</h5>
                  <p className="text-[#a59db8] mt-2">{result.evaluation.explanation}</p>
                </div>
              )}
            </div>
          );
        })}
      </div>
      {analysis && (
        <div className="bg-[#2d2938] p-6 rounded-xl w-full max-w-2xl mt-6">
          <h3 className="text-white text-xl font-bold mb-2">Analysis</h3>
          <p className="text-[#a59db8] mb-2">{analysis.overall_summary}</p>
          {analysis.weak_areas.length > 0 && (
            <p className="text-[#a59db8]">
              <strong className="text-white">Weak Areas:</strong> {analysis.weak_areas.join(', ')}
            </p>
          )}
          {analysis.strong_areas.length > 0 && (
            <p className="text-[#a59db8]">
              <strong className="text-white">Strong Areas:</strong> {analysis.strong_areas.join(', ')}
            </p>
          )}
        </div>
      )}
    </div>
  );
};

export default Results;
