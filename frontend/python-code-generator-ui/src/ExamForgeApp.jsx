// In frontend/src/App.js

import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
// All other imports for components, libraries, etc. should go below this line.
import ReactMarkdown from 'react-markdown';
import { jsPDF } from 'jspdf';
import MarkdownIt from 'markdown-it';
import config from './config';
// ... other imports

// The rest of your file remains the same.

const FileUpload = ({ onUploadSuccess }) => {
  const fileInputRef = useRef(null);
  
  const handleFileClick = () => {
    // This function now correctly triggers the hidden file input
    fileInputRef.current.click();
  };
  
  return (
    <div className="flex flex-col items-center justify-center p-4">
      <h1 className="text-white text-3xl font-bold mb-4" style={{ fontFamily: 'Garamond, serif' }}>Welcome to the Quiz Generator</h1>
      <h2 className="text-white text-2xl font-bold mb-8" style={{ fontFamily: '"Book Antiqua", serif' }}>Let's get started</h2>
      <div className="flex items-center gap-4 border border-[#4d4957] rounded-full p-2 bg-[#2d2938] w-full  transition-all duration-200 hover:shadow-[0_0_15px_rgba(120,71,235,0.5)]">
        <div 
          onClick={handleFileClick} 
          className="flex items-center justify-center w-10 h-10 text-white rounded-full cursor-pointer hover:bg-[#3d3a49] transition-colors duration-200"
        >
          {/* Filled plus symbol for file upload */}
          <svg xmlns="http://www.w3.org/2000/svg" width="24px" height="24px" fill="currentColor" viewBox="0 0 256 256">
            <path d="M208,32H48A16,16,0,0,0,32,48V208a16,16,0,0,0,16,16H208a16,16,0,0,0,16-16V48A16,16,0,0,0,208,32ZM184,136H136v48a8,8,0,0,1-16,0V136H72a8,8,0,0,1,0-16h48V72a8,8,0,0,1,16,0v48h48a8,8,0,0,1,0,16Z"></path>
          </svg>
        </div>
        <input 
          type="file" 
          ref={fileInputRef}
          accept=".pdf,.docx,.pptx"
          onChange={async (e) => {
            if (e.target.files.length > 0) {
              const formData = new FormData();
              formData.append('file', e.target.files[0]);

              try {
                const response = await fetch(`${config.API_BASE_URL}/upload`, {
                  method: "POST",
                  body: formData,
                });

                if (!response.ok) throw new Error("Upload failed");

                const data = await response.json();
                onUploadSuccess(data.document_id);
              } catch (err) {
                console.error("File upload error:", err);
                alert("Failed to upload file.");
              }
            }
          }} 
          className="hidden" 
        />
        <p className="text-sm text-[#a59db8]">Upload Your File</p>
      </div>
    </div>
  );
};

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
        <input 
          type="number"
          min="1"
          max="20"
          value={numQuestions}
          onChange={(e) => setNumQuestions(parseInt(e.target.value))}
          className="bg-[#2d2938] text-white p-3 rounded-lg border-0 focus:ring-2 focus:ring-[#7847eb]"
        />
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

// In frontend/src/App.js

// In frontend/src/App.js

// In frontend/src/App.js

// In frontend/src/App.js

// In frontend/src/App.js

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

          if (!originalQuestion) {
            return null;
          }

          const isMCQ = originalQuestion.options !== undefined; // Check if 'options' property exists
          const isCorrect = result.evaluation.is_correct;
          const questionText = originalQuestion.question;

          return (
            <div key={index} className="bg-[#1e1e1e] p-6 rounded-lg mb-4 shadow-md">
              <h4 className="text-white text-lg font-semibold mb-2">Question {index + 1}</h4>
              <p className="text-[#a59db8] mb-4">{questionText}</p>

              {/* Conditionally render based on quiz type */}
              {isMCQ ? (
                // --- MCQ Rendering Logic ---
                <div className="flex flex-col gap-2">
                  {Object.entries(originalQuestion.options).map(([letter, text]) => {
                    const correctOptionLetter = originalQuestion.correct_answer.trim();
                    const userOptionLetter = result.userAnswer.trim();
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
              ) : (
                // --- Theoretical Question Rendering Logic ---
                <div className="flex flex-col gap-2">
                  <div className={`p-3 rounded-lg border ${isCorrect ? 'bg-[#28a745] border-[#28a745]' : 'bg-[#dc3545] border-[#dc3545]'}`}>
                    <p className="text-white">
                      <strong className="mr-2">Your Answer:</strong> {result.userAnswer}
                    </p>
                  </div>
                  {!isCorrect && (
                    <div className="p-3 rounded-lg border bg-[#2d2938] border-[#4d4957]">
                      <p className="text-white">
                        <strong className="mr-2">Correct Answer:</strong> {result.evaluation.correct_answer_text}
                      </p>
                    </div>
                  )}
                </div>
              )}

              {/* Display explanation for incorrect answers, regardless of type */}
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

// In frontend/src/App.js

// In frontend/src/App.js

const LOADING_MESSAGES = [
  "Uploading your document...",
  "Extracting text and preparing for analysis...",
  "Chunking the document into smaller, manageable sections...",
  "Generating embeddings for efficient retrieval...",
  "Building the FAISS index for lightning-fast search...",
  "Consulting the knowledge base to generate your quiz...",
  "Finalizing questions and answers...",
  "Almost there! Just a moment longer..."
];

const LoadingSpinner = () => {
  const [messageIndex, setMessageIndex] = useState(0);

  useEffect(() => {
    // Increase the interval to 3000ms (3 seconds) for a slower, more readable pace
    const interval = setInterval(() => {
      setMessageIndex(prevIndex => {
        // If we've reached the last message, stop changing it
        if (prevIndex === LOADING_MESSAGES.length - 1) {
          return prevIndex;
        }
        // Otherwise, move to the next message
        return prevIndex + 1;
      });
    }, 3000); // Change message every 3 seconds

    // Clean up the interval when the component unmounts
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="flex flex-col items-center justify-center h-full">
      <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-[#7847eb]"></div>
      <p className="mt-4 text-[#a59db8]">{LOADING_MESSAGES[messageIndex]}</p>
    </div>
  );
};

// In frontend/src/App.js

// In frontend/src/App.js

// In frontend/src/App.js

// In frontend/src/App.js

const DocumentHistory = ({ documentsMeta, chatSessionsMeta, onSelectDocument, onSelectChatSession, onChatSessionDelete, selectedDocumentIds }) => {
  // Group chat sessions by quiz type
  const groupedChatSessions = chatSessionsMeta.reduce((acc, session) => {
    const type = session.quiz_type || 'Other';
    if (!acc[type]) {
      acc[type] = [];
    }
    acc[type].push(session);
    return acc;
  }, {});

  // Define a mapping for display names and icons
  const sessionTypes = [
    { key: 'Theoretical', name: 'Theoretical Quizzes' },
    { key: 'MCQ', name: 'MCQ Quizzes' },
    { key: 'Story Mode', name: 'Story Mode' },
    { key: 'Learning Mode', name: 'Learning Mode' }
  ];

  const hasChatSessions = Object.keys(groupedChatSessions).length > 0;

  return (
    <div className="flex flex-col gap-4 overflow-y-auto h-full p-4">
      {/* Uploaded Documents Section - No Change */}
      <div className="flex flex-col gap-2">
        <h2 className="text-[#a59db8] text-xs font-semibold uppercase tracking-wider flex items-center gap-2">
          {/* Outline SVG for Uploaded Documents */}
          <svg xmlns="http://www.w3.org/2000/svg" width="16px" height="16px" fill="none" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="16px" viewBox="0 0 256 256"><path d="M224,88H168L128,48H48A16,16,0,0,0,32,64V200a16,16,0,0,0,16,16H208a16,16,0,0,0,16-16Z"></path></svg>
          Uploaded Documents
        </h2>
        <ul className="flex flex-col gap-2">
          {documentsMeta.map(doc => (
            <li 
              key={doc.id} 
              onClick={() => onSelectDocument(doc.id)} 
              className={`flex items-center gap-3 px-3 py-2 rounded-lg cursor-pointer transition-all duration-200 ${selectedDocumentIds.includes(doc.id) ? 'bg-[#2d2938] shadow-[0_0_15px_rgba(120,71,235,0.5)]' : 'hover:bg-[#2d2938] hover:shadow-[0_0_15px_rgba(120,71,235,0.5)]'}`}>
              <p className="text-white text-sm truncate">{doc.filename}</p>
            </li>
          ))}
        </ul>
      </div>

      {/* Grouped Chat Sessions Section */}
      <div className="flex flex-col gap-2">
        <h2 className="text-[#a59db8] text-xs font-semibold uppercase tracking-wider flex items-center gap-2">
          {/* Outline SVG for Chat Sessions */}
          <svg xmlns="http://www.w3.org/2000/svg" width="16px" height="16px" fill="none" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="16px" viewBox="0 0 256 256"><path d="M224,56V184a16,16,0,0,1-16,16H168.42L128,226.75,87.58,200H48a16,16,0,0,1-16-16V56A16,16,0,0,1,48,40H208A16,16,0,0,1,224,56Z"></path></svg>
          Chat Sessions
        </h2>
        {hasChatSessions ? (
          <>
            {sessionTypes.map(type => {
              const sessions = groupedChatSessions[type.key];
              if (sessions && sessions.length > 0) {
                return (
                  <div key={type.key} className="flex flex-col gap-2">
                    <h3 className="text-[#a59db8] text-sm font-semibold pl-2">{type.name}</h3>
                    <ul className="flex flex-col gap-2 pl-4">
                      {sessions.map(session => (
                        <li 
                          key={session.chat_id} 
                          className="flex items-center justify-between gap-3 px-3 py-2 rounded-lg cursor-pointer transition-all duration-200 hover:bg-[#2d2938] hover:shadow-[0_0_15px_rgba(120,71,235,0.5)] group">
                          <p 
                            onClick={() => onSelectChatSession(session.chat_id, session.document_id, session.quiz_type)}
                            className="text-white text-sm truncate flex-1">
                            {session.document_filename}
                          </p>
                          <button 
                            onClick={(e) => {
                              e.stopPropagation(); // Prevent the parent <li>'s onClick from firing
                              onChatSessionDelete(session.chat_id);
                            }}
                            className="flex-shrink-0 text-[#a59db8] hover:text-[#dc3545] transition-colors duration-200 opacity-0 group-hover:opacity-100"
                            title="Delete chat session"
                          >
                            {/* Trash Can SVG Icon */}
                            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 256 256">
                              <path d="M216,48H176V40a24,24,0,0,0-24-24H104A24,24,0,0,0,80,40v8H40a8,8,0,0,0,0,16h8V208a16,16,0,0,0,16,16H192a16,16,0,0,0,16-16V64h8a8,8,0,0,0,0-16ZM96,40a8,8,0,0,1,8-8h48a8,8,0,0,1,8,8v8H96ZM192,208H64V64H192ZM112,104v64a8,8,0,0,1-16,0V104a8,8,0,0,1,16,0Zm48,0v64a8,8,0,0,1-16,0V104a8,8,0,0,1,16,0Z"></path>
                            </svg>
                          </button>
                        </li>
                      ))}
                    </ul>
                  </div>
                );
              }
              return null;
            })}
          </>
        ) : (
          <p className="text-[#a59db8] text-sm pl-2">No chat sessions found.</p>
        )}
      </div>
    </div>
  );
};


const handleChatSessionDelete = async (chatId) => {
    try {
        const response = await fetch(`${config.API_BASE_URL}/chat-sessions/${chatId}`, {
            method: 'DELETE',
        });
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        // After successful deletion, refresh the history
        fetchHistory();
        alert("Chat session deleted successfully!");
    } catch (err) {
        console.error("Failed to delete chat session:", err);
        alert("Failed to delete chat session.");
    }
};
// In frontend/src/App.js

// In frontend/src/App.js

const ChatInterface = ({ messages, onSendMessage, isLoading, quizCompleted, onViewFullResults }) => {
  const [inputMessage, setInputMessage] = useState('');
  const textareaRef = useRef(null); // Create a ref to the textarea element

  const handleSubmit = (e) => {
    e.preventDefault();
    if (inputMessage.trim()) {
      onSendMessage(inputMessage);
      setInputMessage('');
    }
  };

  // This effect will run every time inputMessage changes
  useEffect(() => {
    if (textareaRef.current) {
      // Reset the height to 'auto' to correctly calculate the new scrollHeight
      textareaRef.current.style.height = 'auto';
      // Set the height to the new scrollHeight, ensuring it expands
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  }, [inputMessage]);

  return (
    <div className="flex flex-col h-full w-full mx-auto">
      <div className="flex-1 overflow-y-auto p-4 flex flex-col gap-4">
        {messages.map((msg, index) => (
          <div key={index} className={`my-2 p-3 rounded-lg w-fit max-w-[80%] ${msg.role === 'user' ? 'bg-[#2d2938] ml-auto rounded-br-none' : 'bg-[#1e1e1e] mr-auto rounded-bl-none'}`}>
            <div className="prose prose-invert max-w-none">
              <ReactMarkdown
                components={{
                  h1: ({ node, ...props }) => <h1 className="text-2xl font-bold mt-6 mb-4 text-white" {...props} />,
                  h2: ({ node, ...props }) => <h2 className="text-xl font-semibold mt-5 mb-3 text-white" {...props} />,
                  h3: ({ node, ...props }) => <h3 className="text-lg font-medium mt-4 mb-2 text-white" {...props} />,
                  p: ({ node, ...props }) => <p className="text-base text-[#FFFFFF]" {...props} />,
                  ul: ({ node, ...props }) => <ul className="list-disc list-outside text-[#a59db8] mb-4 pl-5" {...props} />,
                  ol: ({ node, ...props }) => <ol className="list-decimal list-outside text-[#a59db8] mb-4 pl-5" {...props} />,
                  li: ({ node, ...props }) => <li className="mb-2" {...props} />,
                  code: ({ node, inline, ...props }) => (
                    inline ? (
                      <code className="bg-[#1e1e1e] text-[#7847eb] px-1 rounded" {...props} />
                    ) : (
                      <pre className="bg-[#1e1e1e] p-4 rounded-lg text-[#a59db8] overflow-x-auto"><code {...props} /></pre>
                    )
                  ),
                  blockquote: ({ node, ...props }) => <blockquote className="border-l-4 border-[#7847eb] pl-4 italic text-[#a59db8] mb-4" {...props} />,
                }}
              >
                {msg.content}
              </ReactMarkdown>
            </div>
          </div>
        ))}
      </div>
      <form onSubmit={handleSubmit} className="p-4 flex gap-2 items-center border-t border-[#2d2938]">
        <textarea
          ref={textareaRef} // Attach the ref to the textarea
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          placeholder="Type your Answer..."
          className="flex-1 bg-[#2d2938] text-white p-3 rounded-lg border-0 focus:ring-2 focus:ring-[#7847eb] resize-none overflow-hidden h-auto min-h-[48px]"
          rows="1"
          disabled={quizCompleted || isLoading}
        />
        <button type="submit" disabled={!inputMessage.trim() || quizCompleted || isLoading} className="bg-[#7847eb] hover:bg-[#5b36b2] text-white px-4 py-2 rounded-lg font-bold">Send</button>
        {quizCompleted && (
          <button onClick={onViewFullResults} className="bg-[#2d2938] hover:bg-[#3d3a49] text-white px-4 py-2 rounded-lg font-bold">View Full Results</button>
        )}
      </form>
    </div>
  );
};

// In frontend/src/App.js

const StoryModeDisplay = ({ explanations, onReset }) => {
  const md = new MarkdownIt();

  const handleDownloadPDF = () => {
    const doc = new jsPDF({
      orientation: 'portrait',
      unit: 'mm',
      format: 'a4',
    });
    const margin = 15;
    const maxWidth = 180;
    const pageHeight = doc.internal.pageSize.height;
    let yOffset = 15;

    // Add title
    doc.setFont('helvetica', 'bold');
    doc.setFontSize(18);
    doc.setTextColor(40, 40, 40);
    doc.text('Story Mode Explanations', margin, yOffset);
    yOffset += 12;

    explanations.forEach((exp, idx) => {
      // Section header
      doc.setFont('helvetica', 'bold');
      doc.setFontSize(14);
      doc.setTextColor(120, 71, 235);
      yOffset += 8;
      if (yOffset > pageHeight - 20) {
        doc.addPage();
        yOffset = 15;
      }
      const sectionLines = doc.splitTextToSize(exp.section, maxWidth);
      sectionLines.forEach(line => {
        doc.text(line, margin, yOffset);
        yOffset += 6;
      });
      yOffset += 4;

      // --- START: MODIFIED CODE ---

      // Function to strip all Markdown from the text
      const stripMarkdown = (markdownText) => {
        if (!markdownText) return '';
        // Regex to remove headers, bold, italics, lists, and links
        return markdownText
          .replace(/^(#+\s*.*$)/gm, '') // Remove headers
          .replace(/(\*\*|__)(.*?)\1/g, '$2') // Remove bold
          .replace(/(\*|_)(.*?)\1/g, '$2') // Remove italics
          .replace(/^(\s*[\*-]\s*)/gm, '') // Remove list bullets
          .replace(/\[(.*?)\]\(.*?\)/g, '$1') // Remove links
          .trim();
      };

      const plainText = stripMarkdown(exp.explanation);
      const lines = doc.splitTextToSize(plainText, maxWidth);
      doc.setFont('helvetica', 'normal');
      doc.setFontSize(12);
      doc.setTextColor(60, 60, 60);

      lines.forEach(line => {
        if (yOffset > pageHeight - 20) {
          doc.addPage();
          yOffset = 15;
        }
        doc.text(line, margin, yOffset);
        yOffset += 6;
      });
      yOffset += 8;

      // --- END: MODIFIED CODE ---
    });

    // Add page numbers
    const pageCount = doc.internal.getNumberOfPages();
    for (let i = 1; i <= pageCount; i++) {
      doc.setPage(i);
      doc.setFontSize(10);
      doc.setTextColor(100, 100, 100);
      doc.text(`Page ${i}`, 180, pageHeight - 10);
    }

    doc.save('story-mode-explanations.pdf');
  };

  return (
    <div className="flex flex-col items-center p-4 w-full  mx-auto"> {/* Changed to custom  */}
      <h2 className="text-white text-2xl font-bold mb-4">Story Mode</h2>
      <div className="flex justify-end mb-4">
        <button
          onClick={handleDownloadPDF}
          className="bg-[#7847eb] hover:bg-[#5b36b2] text-white px-4 py-2 rounded-lg"
        >
          Download PDF
        </button>
      </div>
      <div className="max-h-[calc(100vh-200px)] overflow-y-auto bg-[#2d2938] text-white p-6 rounded-lg w-full mb-4">
        {explanations.length > 0 ? (
          explanations.map((exp, idx) => (
            <div key={idx} className="mb-8">
              <h3 className="text-xl font-bold mb-4 text-[#7847eb]">{exp.section}</h3>
              <div className="prose prose-invert max-w-none">
                <ReactMarkdown
                  components={{
                    h1: ({ node, ...props }) => <h1 className="text-2xl font-bold mt-6 mb-4 text-white" {...props} />,
                    h2: ({ node, ...props }) => <h2 className="text-xl font-semibold mt-5 mb-3 text-white" {...props} />,
                    h3: ({ node, ...props }) => <h3 className="text-lg font-medium mt-4 mb-2 text-white" {...props} />,
                    p: ({ node, ...props }) => <p className="text-base text-[#FFFFFF]" {...props} />,
                    ul: ({ node, ...props }) => <ul className="list-disc list-outside text-[#a59db8] mb-4 pl-5" {...props} />,
                    ol: ({ node, ...props }) => <ol className="list-decimal list-outside text-[#a59db8] mb-4 pl-5" {...props} />,
                    li: ({ node, ...props }) => <li className="mb-2" {...props} />,
                    code: ({ node, inline, ...props }) => (
                      inline ? (
                        <code className="bg-[#1e1e1e] text-[#7847eb] px-1 rounded" {...props} />
                      ) : (
                        <pre className="bg-[#1e1e1e] p-4 rounded-lg text-[#a59db8] overflow-x-auto"><code {...props} /></pre>
                      )
                    ),
                    blockquote: ({ node, ...props }) => <blockquote className="border-l-4 border-[#7847eb] pl-4 italic text-[#a59db8] mb-4" {...props} />,
                  }}
                >
                  {exp.explanation}
                </ReactMarkdown>
              </div>
            </div>
          ))
        ) : (
          <p className="text-[#a59db8] text-base">Your story explanation will appear here.</p>
        )}
      </div>
      <button onClick={onReset} className="bg-[#2d2938] hover:bg-[#3d3a49] text-white px-4 py-2 rounded-lg">Start Over</button>
    </div>
  );
};

const LearningModeDisplay = ({ messages, onSendMessage, isLoading, onReset }) => {
  const [inputMessage, setInputMessage] = useState('');
  const handleSubmit = (e) => {
    e.preventDefault();
    if (inputMessage.trim()) {
      onSendMessage(inputMessage);
      setInputMessage('');
    }
  };
  return (
    <div className="flex flex-col h-full w-full  mx-auto">
      <div className="flex-1 overflow-y-auto p-4 flex flex-col gap-4">
        {messages.map((msg, index) => (
          <div key={index} className={`my-2 p-3 rounded-lg w-fit max-w-[80%] ${msg.role === 'user' ? 'bg-[#2d2938] ml-auto rounded-br-none' : 'bg-[#1e1e1e] mr-auto rounded-bl-none'}`}>
            <div className="prose prose-invert max-w-none">
              <ReactMarkdown
                components={{
                  h1: ({ node, ...props }) => <h1 className="text-2xl font-bold mt-6 mb-4 text-white" {...props} />,
                  h2: ({ node, ...props }) => <h2 className="text-xl font-semibold mt-5 mb-3 text-white" {...props} />,
                  h3: ({ node, ...props }) => <h3 className="text-lg font-medium mt-4 mb-2 text-white" {...props} />,
                  p: ({ node, ...props }) => <p className="text-base text-[#a59db8]" {...props} />,
                  ul: ({ node, ...props }) => <ul className="list-disc list-outside text-[#a59db8] mb-4 pl-5" {...props} />,
                  ol: ({ node, ...props }) => <ol className="list-decimal list-outside text-[#a59db8] mb-4 pl-5" {...props} />,
                  li: ({ node, ...props }) => <li className="mb-2" {...props} />,
                  code: ({ node, inline, ...props }) => (
                    inline ? (
                      <code className="bg-[#1e1e1e] text-[#7847eb] px-1 rounded" {...props} />
                    ) : (
                      <pre className="bg-[#1e1e1e] p-4 rounded-lg text-[#a59db8] overflow-x-auto"><code {...props} /></pre>
                    )
                  ),
                  blockquote: ({ node, ...props }) => <blockquote className="border-l-4 border-[#7847eb] pl-4 italic text-[#a59db8] mb-4" {...props} />,
                }}
              >
                {msg.content}
              </ReactMarkdown>
            </div>
          </div>
        ))}
        {isLoading && <p className="text-[#a59db8] italic">Typing...</p>}
      </div>
      <form onSubmit={handleSubmit} className="p-4 flex gap-2 items-center bg-[#131118] border-t border-[#2d2938]">
        <input 
          type="text" 
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          placeholder="Type your message..."
          className="flex-1 bg-[#2d2938] text-white p-3 rounded-lg border-0 focus:ring-2 focus:ring-[#7847eb]"
          disabled={isLoading}
        />
        <button type="submit" disabled={!inputMessage.trim() || isLoading} className="bg-[#7847eb] hover:bg-[#5b36b2] text-white px-4 py-2 rounded-lg font-bold">Send</button>
        <button onClick={onReset} className="bg-[#2d2938] hover:bg-[#3d3a49] text-white px-4 py-2 rounded-lg font-bold">Start Over</button>
      </form>
    </div>
  );
};

// --- Main App Component ---
export default function App() {
  const navigate = useNavigate();
  const [documentId, setDocumentId] = useState(null);
  const [quizData, setQuizData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [quizResults, setQuizResults] = useState([]);
  const [viewMode, setViewMode] = useState('upload');
  const [chatMessages, setChatMessages] = useState([]);
  const [currentChatSessionId, setCurrentChatSessionId] = useState(null);
  const [currentQuizType, setCurrentQuizType] = useState(null);
  const [selectedDocumentIds, setSelectedDocumentIds] = useState([]);
  const [documentsMeta, setDocumentsMeta] = useState([]);
  const [chatSessionsMeta, setChatSessionsMeta] = useState([]);
  const [analysis, setAnalysis] = useState(null);
  const [quizId, setQuizId] = useState(null);
  const [storyExplanations, setStoryExplanations] = useState([]);
  const [learningTopic, setLearningTopic] = useState('');
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });

  // Navigate to home/landing page
  const handleNavigateHome = () => {
    navigate('/');
  };

  useEffect(() => {
    const handleMouseMove = (e) => {
      setMousePosition({ x: e.clientX, y: e.clientY });
    };

    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);

  // --- API and Logic Functions ---
  const fetchHistory = async () => {
    try {
      const docsResponse = await fetch(`${config.API_BASE_URL}/documents`);
      const docsData = await docsResponse.json();
      setDocumentsMeta(docsData);
      const chatResponse = await fetch(`${config.API_BASE_URL}/chat-sessions`);
      const chatData = await chatResponse.json();
      setChatSessionsMeta(chatData);
    } catch (err) {
      console.error("Failed to fetch history:", err);
      setError("Failed to connect to the backend server. Please ensure the server is running.");
    }
  };

  const handleChatSessionDelete = async (chatId) => {
    try {
        const response = await fetch(`${config.API_BASE_URL}/chat-sessions/${chatId}`, {
            method: 'DELETE',
        });
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        // After successful deletion, refresh the history
        fetchHistory();
        alert("Chat session deleted successfully!");
    } catch (err) {
        console.error("Failed to delete chat session:", err);
        alert("Failed to delete chat session.");
    }
  };

  const handleFileUploadSuccess = (docId) => {
    console.log("Upload success with document ID:", docId); // Debug log
    setDocumentId(docId);
    setSelectedDocumentIds([docId]);
    setQuizData(null);
    setQuizResults([]);
    setError(null);
    setViewMode('action_select');
    fetchHistory();
  };

  const handleSelectDocument = (docId) => {
    console.log("Selecting document with ID:", docId); // Debug log
    setSelectedDocumentIds([docId]);
    setViewMode('action_select');
  };


  const handleGenerateQuiz = async (quizType, numQuestions, difficulty) => {
    if (selectedDocumentIds.length === 0) {
        setError("Please select a document from history or upload a new one to generate a quiz.");
        return;
    }
    setIsLoading(true);
    setError(null);
    setQuizData(null);
    setQuizResults([]);
    setCurrentQuizType(quizType);
    try {
        const response = await fetch(`${config.API_BASE_URL}/generate-quiz`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                document_ids: selectedDocumentIds,
                quiz_type: quizType,
                num_questions: numQuestions,
                difficulty: difficulty
            }),
        });
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        console.log('Quiz response from server:', data);
        if (response.ok) {
            setQuizData(data.quiz);
            setQuizId(data.quiz_id);
            if (quizType === 'Theoretical') {
                setCurrentChatSessionId(data.quiz_id);
                const initialMessages = [];
                if (data.quiz && data.quiz.length > 0) {
                    initialMessages.push({ role: 'system', content: `Quiz generated! This is a theoretical quiz with ${data.quiz.length} questions.` });
                    initialMessages.push({ role: 'system', content: `**Question 1:** ${data.quiz[0].question}` });
                } else {
                    initialMessages.push({ role: 'system', content: "Quiz generated, but no questions found. Please try a different document." });
                }
                setChatMessages(initialMessages);
                setViewMode('theoretical_quiz_chat');
                
                // Add this block to save the initial chat session to the database.
                await fetch(`${config.API_BASE_URL}/chat-history`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        chat_id: data.quiz_id,
                        document_id: selectedDocumentIds[0],
                        quiz_type: quizType,
                        messages: initialMessages
                    })
                });
                
            } else {
                setViewMode('quiz_display');
            }
        } else {
            setError(data.error || 'Failed to generate quiz.');
        }
    } catch (err) {
        console.error('Error generating quiz:', err);
        setError('Network error or server unavailable during quiz generation.');
    } finally {
        setIsLoading(false);
    }
  };  
  // In frontend/src/App.js

  // In frontend/src/App.js

  // In frontend/src/App.js

  const handleSubmitQuiz = async (answers) => {
    if (!quizId) {
      setError("Quiz ID is missing. Cannot submit answers.");
      return;
    }
    setIsLoading(true);
    setError(null);
    try {
      const response = await fetch(`${config.API_BASE_URL}/evaluate-quiz`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          quiz_id: quizId,
          answers: answers,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      // The backend returns the evaluated results and analysis
      setQuizResults(data.results);
      setAnalysis(data.analysis);
      
      // Switch the view to the results page
      setViewMode('results');

    } catch (err) {
      console.error('Error submitting quiz:', err);
      setError(`Failed to submit quiz: ${err.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleChatSubmit = async (message) => {
      if (!message.trim() || !quizData || isLoading) return;
      const currentQuestionIndex = chatMessages.filter(msg => msg.role === 'user').length;
      const currentQuestion = quizData[currentQuestionIndex];
      if (!currentQuestion) {
          setChatMessages(prev => [...prev, { role: 'system', content: "No more questions in this quiz. Please click 'View Full Results' or 'Start Over'." }]);
          return;
      }
      const messagesAfterUser = [...chatMessages, { role: 'user', content: message }];
      setChatMessages(messagesAfterUser);
      setIsLoading(true);

      try {
          const response = await fetch(`${config.API_BASE_URL}/evaluate-answer`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({
                  document_id: selectedDocumentIds[0],
                  quiz_id: currentChatSessionId,
                  question_index: currentQuestionIndex,
                  user_answer: message,
              }),
          });
          if (!response.ok) {
              throw new Error(`HTTP error! status: ${response.status}`);
          }
          const data = await response.json();
          const nextQuestion = quizData[currentQuestionIndex + 1];

          // --- ADDED LOGIC: SAVE THE RESULT TO LOCAL STATE ---
          const resultForState = {
              question: currentQuestion.question,
              userAnswer: message,
              correctAnswer: data.evaluation.correct_answer_text,
              evaluation: data.evaluation,
              is_mcq: false // Theoretical questions are not MCQs
          };
          // Use a functional update to ensure we have the latest state
          setQuizResults(prevResults => {
            const newResults = [...prevResults, resultForState];
            // If this is the last question, save the analysis from the backend response
            if (nextQuestion === undefined && data.analysis) {
              setAnalysis(data.analysis);
            }
            return newResults;
          });
          // --- END OF ADDED LOGIC ---

          let feedbackMessage = `**Evaluation:**\n\n`;
          if (data.evaluation.is_correct) {
              feedbackMessage += `Your answer was correct! ✅\n\n`;
          } else {
              feedbackMessage += `Your answer was incorrect. ❌\n\n`;
          }

          if (data.evaluation.correct_answer_text) {
              feedbackMessage += `**Correct Answer:** ${data.evaluation.correct_answer_text}\n\n`;
          }
          if (!data.evaluation.is_correct && data.evaluation.explanation) {
              feedbackMessage += `**Explanation:** ${data.evaluation.explanation}\n\n`;
          }

          if (nextQuestion) {
              feedbackMessage += `---\n\n**Next Question:** ${nextQuestion.question}`;
          } else {
              feedbackMessage += "You've completed this quiz! To see a summary of your results, click 'View Full Results'.";
          }
          const messagesAfterSystem = [...messagesAfterUser, { role: 'system', content: feedbackMessage }];
          setChatMessages(messagesAfterSystem);

          await fetch(`${config.API_BASE_URL}/chat-history`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({
                  chat_id: currentChatSessionId,
                  document_id: selectedDocumentIds[0],
                  quiz_type: currentQuizType,
                  messages: messagesAfterSystem
              })
          });
      } catch (err) {
          setChatMessages(prev => [...prev, { role: 'system', content: `Error during evaluation: ${err.message}` }]);
          console.error('Chat evaluation error:', err);
          setError('Network error or server unavailable during chat evaluation.');
      } finally {
          setIsLoading(false);
      }
  };

  const handleDownloadRevisionSheet = async () => {
    if (!quizId) {
        setError("Cannot download revision sheet. Quiz ID not found.");
        return;
    }
    try {
        setIsLoading(true);
        const response = await fetch(`${config.API_BASE_URL}/generate-revision-sheet/${quizId}`);
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `revision_sheet_${quizId}.pdf`;
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);
    } catch (err) {
        console.error('Error downloading revision sheet:', err);
        setError('Failed to download revision sheet due to a network error.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleStoryMode = async () => {
    if (selectedDocumentIds.length !== 1) {
      setError("Please select exactly one document to use Story Mode.");
      return;
    }
    const docIdToUse = selectedDocumentIds[0];
    setIsLoading(true);
    setError(null);
    setStoryExplanations([]);
    setViewMode('story');
    try {
      const response = await fetch(`${config.API_BASE_URL}/story-mode/${docIdToUse}`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      if (response.ok) {
        setStoryExplanations(data.explanations || []);
        // Save the new session ID
        setCurrentChatSessionId(data.session_id);
        // Fetch history to update the sidebar with the new session
        fetchHistory();
      } else {
        setError(data.error || 'Failed to generate story explanations.');
      }
    } catch (err) {
      console.error('Error generating story:', err);
      setError('Network error or server unavailable during story generation.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleStartLearningMode = () => {
    if (selectedDocumentIds.length !== 1) {
      setError("Please select exactly one document to start Learning Mode.");
      return;
    }
    setQuizData(null);
    setQuizResults([]);
    setError(null);
    setChatMessages([]);
    setCurrentChatSessionId(null);
    setLearningTopic('');
    setViewMode('learning_topic_input');
  };

  const handleLearningTopicSubmit = async (topic) => {
    console.log("Entering handleLearningTopicSubmit");
    console.log("Current selectedDocumentIds:", selectedDocumentIds);
    console.log("Current documentsMeta:", documentsMeta);
    const docIdToUse = selectedDocumentIds[0];
    if (!docIdToUse) {
      console.log("No document ID found, setting error");
      setError("No document selected. Please select a document from the history or upload a new one.");
      return;
    }
    if (!topic || topic.trim().length < 3) {
      console.log("Invalid topic, setting error");
      setError("Please enter a valid topic with at least 3 characters.");
      return;
    }
    setIsLoading(true);
    setError(null);
    setLearningTopic(topic);
    try {
      console.log("Preparing request with:", { document_ids: [docIdToUse], topic: topic });
      const response = await fetch(`${config.API_BASE_URL}/learning-mode/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ document_ids: [docIdToUse], topic: topic }),
      });
      console.log("Received response, status:", response.status);
      console.log("Response headers:", Object.fromEntries(response.headers.entries()));
      if (!response.ok) {
        const errorText = await response.text();
        console.error("Server response:", errorText);
        throw new Error(`HTTP error! status: ${response.status} - ${errorText}`);
      }
      const data = await response.json();
      console.log("Server response data:", data);
      if (response.ok) {
        setCurrentChatSessionId(data.session_id);
        setChatMessages([{ role: 'system', content: data.initial_message || 'Explanation not available.' }]);
        setViewMode('learning_chat');
      } else {
        setError(data.error || 'Failed to start learning session.');
      }
    } catch (err) {
      console.error('Error starting learning session:', err);
      setError(`Network error or server unavailable during learning session. Details: ${err.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleLearningChatSubmit = async (message) => {
    if (!message.trim() || !currentChatSessionId || isLoading) return;
    const messagesAfterUser = [...chatMessages, { role: 'user', content: message }];
    setChatMessages(messagesAfterUser);
    setIsLoading(true);
    try {
      const response = await fetch(`${config.API_BASE_URL}/learning-mode/respond`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: currentChatSessionId,
          user_answer: message,
          document_ids: selectedDocumentIds, // Add document context
          topic: learningTopic, // Add topic context
        }),
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      if (response.ok) {
        const isFirstResponse = chatMessages.length === 1; // Only initial system message
        const nextMessage = isFirstResponse 
          ? `${data.initial_message || 'No explanation available.'}\n\n${data.next_message || 'Question not available.'}`
          : data.next_message || 'No response available.';
        const messagesAfterSystem = [...messagesAfterUser, { role: 'system', content: nextMessage }];
        setChatMessages(messagesAfterSystem);
      } else {
        setError(data.error || 'Failed to get a response.');
      }
    } catch (err) {
      console.error('Error during learning chat:', err);
      setError('Network error or server unavailable during chat.');
    } finally {
      setIsLoading(false);
    }
  };

  const navigateToResults = async () => {
  setIsLoading(true);
  setError(null);
  let attempts = 0;
  const maxAttempts = 3;

  const fetchResults = async () => {
    try {
      const response = await fetch(`${config.API_BASE_URL}/quiz-results/${currentChatSessionId}`);
      if (!response.ok) {
        if (response.status === 404 && attempts < maxAttempts) {
          console.log(`Results not found, retrying... (Attempt ${attempts + 1})`);
          attempts++;
          setTimeout(fetchResults, 1500); // Wait 1.5 seconds and retry
          return;
        }
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      if (data.quiz_results && data.quiz_results.length > 0) {
        setQuizResults(data.quiz_results);
        setAnalysis(data.analysis || null);
        setViewMode('results');
      } else {
        setError("No results found for this quiz.");
      }
    } catch (err) {
      console.error('Error fetching quiz results:', err);
      setError('Failed to fetch quiz results. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  fetchResults();
  };

  const handleLoadChatSession = async (chatId, documentIdForSession, quizTypeForSession) => {
    setIsLoading(true);
    setError(null);
    setDocumentId(documentIdForSession);
    setSelectedDocumentIds([documentIdForSession]);
    setCurrentChatSessionId(chatId);
    setCurrentQuizType(quizTypeForSession); 
    setAnalysis(null);
    setQuizId(chatId);
    try {
        const chatHistoryResponse = await fetch(`${config.API_BASE_URL}/chat-history/${chatId}`);
        if (!chatHistoryResponse.ok) {
          throw new Error(`HTTP error! status: ${chatHistoryResponse.status}`);
        }
        const chatHistoryData = await chatHistoryResponse.json();
        setChatMessages(chatHistoryData);

        if (quizTypeForSession === 'Theoretical') {
            const docQuizzesResponse = await fetch(`${config.API_BASE_URL}/document/${documentIdForSession}/quizzes`);
            if (!docQuizzesResponse.ok) {
              throw new Error(`HTTP error! status: ${docQuizzesResponse.status}`);
            }
            const docQuizzesData = await docQuizzesResponse.json();
            const loadedQuiz = docQuizzesData.find(q => q.quiz_id === chatId); 
            setQuizData(loadedQuiz ? loadedQuiz.quiz_data : []);
            setViewMode('theoretical_quiz_chat');
        } else {
            setViewMode('learning_chat');
        }
    } catch (err) {
        console.error("Error loading chat session:", err);
        setError("Failed to load chat session. Please check your backend connection.");
    } finally {
      setIsLoading(false);
    }
  };

  const resetApplication = () => {
    setDocumentId(null);
    setSelectedDocumentIds([]);
    setQuizData(null);
    setIsLoading(false);
    setError(null);
    setQuizResults([]);
    setViewMode('upload');
    setChatMessages([]);
    setCurrentChatSessionId(null);
    setCurrentQuizType(null);
    setAnalysis(null);
    setQuizId(null);
    setLearningTopic('');
    fetchHistory();
  };

  useEffect(() => {
    fetchHistory();
  }, []);

  const renderMainContent = () => {
    switch (viewMode) {
      case 'upload':
        return (
          <div className="flex flex-col justify-center items-center h-full">
            <FileUpload onUploadSuccess={handleFileUploadSuccess} />
          </div>
        );
      case 'action_select':
        return (
          <div className="flex flex-col items-center p-8 bg-[#1e1e1e] rounded-[4rem] shadow-xl w-full  mx-auto transition-all duration-300">
              <p className="text-white text-base font-normal leading-normal pb-3 pt-1 px-4 text-center">
                  Documents selected: <strong className="font-bold">
                      {selectedDocumentIds.map(id => documentsMeta.find(d => d.id === id)?.filename).join(', ')}
                  </strong>. Choose an action:
              </p>

              <div className="flex gap-4">
                <button onClick={() => setViewMode('quiz_settings')} className="bg-[#2d2938] hover:bg-[#3d3a49] text-white px-4 py-2 rounded-lg">Generate Quiz</button>
                <button onClick={handleStoryMode} className="bg-[#2d2938] hover:bg-[#3d3a49] text-white px-4 py-2 rounded-lg" disabled={selectedDocumentIds.length > 1}>Story Mode</button>
                <button onClick={handleStartLearningMode} className="bg-[#2d2938] hover:bg-[#3d3a49] text-white px-4 py-2 rounded-lg" disabled={selectedDocumentIds.length > 1}>Learning Mode</button>
              </div>
          </div>
        );
      case 'quiz_settings':
        return (
          <div className="flex flex-col items-center p-8 bg-[#1e1e1e] rounded-[4rem] shadow-xl w-full  mx-auto transition-all duration-300">
            <p className="text-white text-base font-normal leading-normal pb-3 pt-1 px-4 text-center">
              Generate your quiz for: <strong className="font-bold">
                {selectedDocumentIds.map(id => documentsMeta.find(d => d.id === id)?.filename).join(', ')}
              </strong>
            </p>

            <QuizSettings onGenerateQuiz={handleGenerateQuiz} />
          </div>
        );
      case 'quiz_display':
        return (
          <div className="flex flex-col p-8 bg-[#1e1e1e] rounded-[4rem] shadow-xl w-full mx-auto transition-all duration-300">
            <h2 className="text-white text-2xl font-bold mb-4">Quiz Display</h2>
            {quizData && quizData.length > 0 ? (
              <div>
                {quizData.map((question, index) => (
                  <div key={index} className="mb-6 p-4 bg-[#2d2938] rounded-lg">
                    <p className="text-white mb-2"><strong>Question {index + 1}:</strong> {question.question}</p>
                    {question.options && Object.entries(question.options).map(([key, value]) => (
                      <div key={key} className="flex items-center mb-2">
                        <input
                          type="radio"
                          id={`q${index}-option${key}`}
                          name={`question-${index}`}
                          value={key}
                          className="mr-2 text-[#7847eb]"
                        />
                        <label htmlFor={`q${index}-option${key}`} className="text-[#a59db8]">
                          {key}) {value}
                        </label>
                      </div>
                    ))}
                  </div>
                ))}
                <button
                  onClick={() => {
                    const answers = quizData.map((_, index) =>
                      document.querySelector(`input[name="question-${index}"]:checked`)?.value || ''
                    );
                    handleSubmitQuiz(answers);
                  }}
                  className="bg-[#7847eb] hover:bg-[#5b36b2] text-white px-4 py-2 rounded-lg mt-4"
                  disabled={quizData.some((_, index) => !document.querySelector(`input[name="question-${index}"]:checked`))}
                >
                  Submit Quiz
                </button>
              </div>
            ) : (
              <p className="text-[#a59db8]">No questions available. Please generate a quiz.</p>
            )}
          </div>
        );
      case 'results':
        return (
          <div className="flex flex-col items-center p-8 bg-[#1e1e1e] rounded-[4rem] shadow-xl w-full mx-auto transition-all duration-300">
            <Results quizResults={quizResults} analysis={analysis} quizData={quizData} />
            <div className="flex gap-4 mt-4">
                <button onClick={resetApplication} className="bg-[#2d2938] hover:bg-[#3d3a49] text-white px-4 py-2 rounded-lg">Start New Quiz</button>
                <button onClick={handleDownloadRevisionSheet} className="bg-[#2d2938] hover:bg-[#3d3a49] text-white px-4 py-2 rounded-lg">Download Revision Sheet</button>
            </div>
          </div>
        );
      case 'theoretical_quiz_chat':
        return (
          <div className="flex flex-col p-8 bg-[#1e1e1e] rounded-[4rem] shadow-xl w-full  mx-auto transition-all duration-300">
            <ChatInterface 
              messages={chatMessages} 
              onSendMessage={handleChatSubmit} 
              isLoading={isLoading}
              currentQuestion={quizData[chatMessages.filter(msg => msg.role === 'user').length] ? quizData[chatMessages.filter(msg => msg.role === 'user').length].question : "Quiz Completed!"}
              quizCompleted={chatMessages.filter(msg => msg.role === 'user').length >= quizData.length}
              onViewFullResults={navigateToResults}
            />
          </div>
        );
      case 'story':
        return (
          <div className="flex flex-col items-center p-8 bg-[#1e1e1e] rounded-[4rem] shadow-xl w-full  mx-auto transition-all duration-300"> {/* Changed  to  */}
            <StoryModeDisplay explanations={storyExplanations} onReset={resetApplication} />
          </div>
        );
      case 'learning_topic_input':
        return (
          <div className="flex flex-col items-center p-8 bg-[#1e1e1e] rounded-[4rem] shadow-xl w-full  mx-auto transition-all duration-300">
            <h2 className="text-white text-2xl font-bold leading-tight pb-3">What would you like to learn?</h2>
            <p className="text-[#a59db8] text-base font-normal leading-normal pb-3 text-center">
              {selectedDocumentIds.length === 0 
                ? "Please select a document from the history or upload a new one to start your learning session."
                : "Type a topic from the document to start your learning session."}
            </p>
            <form onSubmit={(e) => { e.preventDefault(); handleLearningTopicSubmit(learningTopic); }} className="w-full max-w-lg flex flex-col items-center">
              <input
                type="text"
                value={learningTopic}
                onChange={(e) => setLearningTopic(e.target.value)}
                placeholder="e.g., Photosynthesis"
                className="w-full form-input flex min-w-0 flex-1 resize-none overflow-hidden rounded-lg text-white focus:outline-0 focus:ring-0 border-none bg-[#2d2938] focus:border-none h-12 placeholder:text-[#a59db8] px-4 text-base font-normal leading-normal mb-4"
                disabled={selectedDocumentIds.length === 0}
              />
              <button 
                type="submit" 
                disabled={!learningTopic.trim() || selectedDocumentIds.length === 0} 
                className="bg-[#7847eb] hover:bg-[#5b36b2] text-white px-4 py-2 rounded-lg font-bold"
              >
                Start Learning
              </button>
            </form>
          </div>
        );
      case 'learning_chat':
        return (
          <div className="flex flex-col p-8 bg-[#1e1e1e] rounded-[4rem] shadow-xl w-full  mx-auto transition-all duration-300">
            <LearningModeDisplay 
              messages={chatMessages} 
              onSendMessage={handleLearningChatSubmit} 
              isLoading={isLoading} 
              onReset={resetApplication}
            />
          </div>
        );
      default:
        return (
          <div className="flex flex-col justify-center items-center h-full">
            <FileUpload onUploadSuccess={handleFileUploadSuccess} />
          </div>
        );
    }
  };
  return (
    
    <div className="relative flex size-full min-h-screen flex-col bg-[#131118] dark group/design-root overflow-x-hidden" style={{ fontFamily: 'Aktiv Grotesk, "Noto Sans", sans-serif' }}>
      <div className="layout-container flex h-screen grow flex-row overflow-hidden">
        
        {/* Left Sidebar - Fixed and independent scroll */}
        <div className="flex flex-col w-80 flex-shrink-0 bg-[#1a1a1a]">
          <div className="flex flex-col h-full justify-between p-4 overflow-y-auto">
            <div className="flex flex-col gap-4">
              <h1 className="text-white text-base font-medium leading-normal p-2 border border-gray-600 rounded-lg">Retrieval Augmented Quiz Generator</h1>
              <div className="flex flex-col gap-2">
                <DocumentHistory
                  documentsMeta={documentsMeta} 
                  chatSessionsMeta={chatSessionsMeta}   
                  onSelectDocument={handleSelectDocument}
                  onSelectChatSession={handleLoadChatSession}
                  onChatSessionDelete={handleChatSessionDelete} // Add the new prop
                  selectedDocumentIds={selectedDocumentIds}
                />
              </div>
            </div>
            <div className="flex flex-col gap-4 mt-auto">
              <button onClick={handleNavigateHome} className="flex min-w-[84px] max-w-[480px] cursor-pointer items-center justify-center overflow-hidden rounded-lg h-10 px-4 bg-[#374151] text-white text-sm font-bold leading-normal tracking-[0.015em] hover:bg-[#4b5563] transition-colors duration-200">
                <span className="truncate">← Home</span>
              </button>
              <button onClick={resetApplication} className="flex min-w-[84px] max-w-[480px] cursor-pointer items-center justify-center overflow-hidden rounded-lg h-10 px-4 bg-[#7847eb] text-white text-sm font-bold leading-normal tracking-[0.015em] hover:bg-[#5b36b2]">
                <span className="truncate">Generate New Quiz</span>
              </button>
            </div>
          </div>
        </div>

        {/* Main Content Area - Scrollable */}
        <div className="flex flex-col flex-1 overflow-y-auto">
          {isLoading ? (
            <div className="w-full h-full flex items-center justify-center">
              <LoadingSpinner />
            </div>
          ) : (
            <div className="flex flex-col items-center px-6 py-5">
              {renderMainContent()}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
