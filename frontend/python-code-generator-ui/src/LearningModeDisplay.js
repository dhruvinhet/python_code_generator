import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';

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
            <ReactMarkdown className="prose prose-invert max-w-none" components={{
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
            }}>
              {msg.content}
            </ReactMarkdown>
          </div>
        ))}
        {isLoading && <p className="text-[#a59db8] italic">Typing...</p>}
      </div>
      <form onSubmit={handleSubmit} className="p-4 flex gap-2 items-center bg-[#131118] border-t border-[#2d2938]">
        <input type="text" value={inputMessage} onChange={(e) => setInputMessage(e.target.value)} placeholder="Type your message..." className="flex-1 bg-[#2d2938] text-white p-3 rounded-lg border-0 focus:ring-2 focus:ring-[#7847eb]" disabled={isLoading} />
        <button type="submit" disabled={!inputMessage.trim() || isLoading} className="bg-[#7847eb] hover:bg-[#5b36b2] text-white px-4 py-2 rounded-lg font-bold">Send</button>
        <button onClick={onReset} className="bg-[#2d2938] hover:bg-[#3d3a49] text-white px-4 py-2 rounded-lg font-bold">Start Over</button>
      </form>
    </div>
  );
};

export default LearningModeDisplay;
