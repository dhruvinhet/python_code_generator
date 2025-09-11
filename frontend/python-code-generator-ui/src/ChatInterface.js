import React, { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';

const ChatInterface = ({ messages, onSendMessage, isLoading, quizCompleted, onViewFullResults }) => {
  const [inputMessage, setInputMessage] = useState('');
  const textareaRef = useRef(null);
  const handleSubmit = (e) => {
    e.preventDefault();
    if (inputMessage.trim()) {
      onSendMessage(inputMessage);
      setInputMessage('');
    }
  };
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  }, [inputMessage]);
  return (
    <div className="flex flex-col h-full w-full mx-auto">
      <div className="flex-1 overflow-y-auto p-4 flex flex-col gap-4">
        {messages.map((msg, index) => (
          <div key={index} className={`my-2 p-3 rounded-lg w-fit max-w-[80%] ${msg.role === 'user' ? 'bg-[#2d2938] ml-auto rounded-br-none' : 'bg-[#1e1e1e] mr-auto rounded-bl-none'}`}>
            <ReactMarkdown className="prose prose-invert max-w-none" components={{
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
            }}>
              {msg.content}
            </ReactMarkdown>
          </div>
        ))}
      </div>
      <form onSubmit={handleSubmit} className="p-4 flex gap-2 items-center border-t border-[#2d2938]">
        <textarea ref={textareaRef} value={inputMessage} onChange={(e) => setInputMessage(e.target.value)} placeholder="Type your Answer..." className="flex-1 bg-[#2d2938] text-white p-3 rounded-lg border-0 focus:ring-2 focus:ring-[#7847eb] resize-none overflow-hidden h-auto min-h-[48px]" rows="1" disabled={quizCompleted || isLoading} />
        <button type="submit" disabled={!inputMessage.trim() || quizCompleted || isLoading} className="bg-[#7847eb] hover:bg-[#5b36b2] text-white px-4 py-2 rounded-lg font-bold">Send</button>
        {quizCompleted && (
          <button type="button" onClick={onViewFullResults} className="bg-[#2d2938] hover:bg-[#3d3a49] text-white px-4 py-2 rounded-lg font-bold">View Full Results</button>
        )}
      </form>
    </div>
  );
};

export default ChatInterface;
