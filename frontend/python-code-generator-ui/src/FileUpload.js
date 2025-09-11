import React, { useRef } from 'react';

const FileUpload = ({ onUploadSuccess }) => {
  const fileInputRef = useRef(null);
  const handleFileClick = () => {
    fileInputRef.current.click();
  };
  return (
    <div className="flex flex-col items-center justify-center p-4">
      <h1 className="text-white text-3xl font-bold mb-4" style={{ fontFamily: 'Garamond, serif' }}>Welcome to the Quiz Generator</h1>
      <h2 className="text-white text-2xl font-bold mb-8" style={{ fontFamily: 'Book Antiqua, serif' }}>Let's get started</h2>
      <div className="flex items-center gap-4 border border-[#4d4957] rounded-full p-2 bg-[#2d2938] w-full  transition-all duration-200 hover:shadow-[0_0_15px_rgba(120,71,235,0.5)]">
        <div onClick={handleFileClick} className="flex items-center justify-center w-10 h-10 text-white rounded-full cursor-pointer hover:bg-[#3d3a49] transition-colors duration-200">
          {/* Filled plus symbol for file upload */}
          <svg xmlns="http://www.w3.org/2000/svg" width="24px" height="24px" fill="currentColor" viewBox="0 0 256 256">
            <path d="M208,32H48A16,16,0,0,0,32,48V208a16,16,0,0,0,16,16H208a16,16,0,0,0,16-16V48A16,16,0,0,0,208,32ZM184,136H136v48a8,8,0,0,1-16,0V136H72a8,8,0,0,1,0-16h48V72a8,8,0,0,1,16,0v48h48a8,8,0,0,1,0,16Z"></path>
          </svg>
        </div>
        <input type="file" ref={fileInputRef} accept=".pdf,.docx,.pptx" onChange={async (e) => {
          if (e.target.files.length > 0) {
            const formData = new FormData();
            formData.append('file', e.target.files[0]);
            try {
              const response = await fetch("http://127.0.0.1:5000/upload", {
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
        }} className="hidden" />
        <p className="text-sm text-[#a59db8]">Upload Your File</p>
      </div>
    </div>
  );
};

export default FileUpload;
