import React from 'react';

const DocumentHistory = ({ documentsMeta, chatSessionsMeta, onSelectDocument, onSelectChatSession, selectedDocumentIds }) => (
  <div className="flex flex-col gap-4 overflow-y-auto h-full p-4">
    <div className="flex flex-col gap-2">
      <h2 className="text-[#a59db8] text-xs font-semibold uppercase tracking-wider flex items-center gap-2">
        <svg xmlns="http://www.w3.org/2000/svg" width="16px" height="16px" fill="none" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="16px" viewBox="0 0 256 256"><path d="M224,88H168L128,48H48A16,16,0,0,0,32,64V200a16,16,0,0,0,16,16H208a16,16,0,0,0,16-16V48A16,16,0,0,0,208,32ZM184,136H136v48a8,8,0,0,1-16,0V136H72a8,8,0,0,1,0-16h48V72a8,8,0,0,1,16,0v48h48a8,8,0,0,1,0,16Z"></path></svg>
        Uploaded Documents
      </h2>
      <ul className="flex flex-col gap-2">
        {documentsMeta.map(doc => (
          <li key={doc.id} onClick={() => onSelectDocument(doc.id)} className={`flex items-center gap-3 px-3 py-2 rounded-lg cursor-pointer transition-all duration-200 ${selectedDocumentIds.includes(doc.id) ? 'bg-[#2d2938] shadow-[0_0_15px_rgba(120,71,235,0.5)]' : 'hover:bg-[#2d2938] hover:shadow-[0_0_15px_rgba(120,71,235,0.5)]'}`}>
            <p className="text-white text-sm truncate">{doc.filename}</p>
          </li>
        ))}
      </ul>
    </div>
    <div className="flex flex-col gap-2">
      <h2 className="text-[#a59db8] text-xs font-semibold uppercase tracking-wider flex items-center gap-2">
        <svg xmlns="http://www.w3.org/2000/svg" width="16px" height="16px" fill="none" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="16px" viewBox="0 0 256 256"><path d="M224,56V184a16,16,0,0,1-16,16H168.42L128,226.75,87.58,200H48a16,16,0,0,1-16-16V56A16,16,0,0,1,48,40H208A16,16,0,0,1,224,56Z"></path></svg>
        Chat Sessions
      </h2>
      <ul className="flex flex-col gap-2">
        {chatSessionsMeta.map(session => (
          <li key={session.chat_id} onClick={() => onSelectChatSession(session.chat_id, session.document_id, session.quiz_type)} className="flex items-center gap-3 px-3 py-2 rounded-lg cursor-pointer transition-all duration-200 hover:bg-[#2d2938] hover:shadow-[0_0_15px_rgba(120,71,235,0.5)]">
            <p className="text-white text-sm truncate">{session.document_filename}</p>
          </li>
        ))}
      </ul>
    </div>
  </div>
);

export default DocumentHistory;
