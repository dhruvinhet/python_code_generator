import React from 'react';
import ReactMarkdown from 'react-markdown';
import { jsPDF } from 'jspdf';
import MarkdownIt from 'markdown-it';

const StoryModeDisplay = ({ explanations, onReset }) => {
  const md = new MarkdownIt();
  const handleDownloadPDF = () => {
    const doc = new jsPDF({ orientation: 'portrait', unit: 'mm', format: 'a4' });
    const margin = 15;
    const maxWidth = 180;
    const pageHeight = doc.internal.pageSize.height;
    let yOffset = 15;
    doc.setFont('helvetica', 'bold');
    doc.setFontSize(18);
    doc.setTextColor(40, 40, 40);
    doc.text('Story Mode Explanations', margin, yOffset);
    yOffset += 12;
    explanations.forEach((exp, idx) => {
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
      const plainText = md.render(exp.explanation).replace(/<[^>]+>/g, '');
      const lines = doc.splitTextToSize(plainText, maxWidth);
      doc.setFont('helvetica', 'normal');
      doc.setFontSize(12);
      doc.setTextColor(60, 60, 60);
      lines.forEach(line => {
        if (yOffset > pageHeight - 20) {
          doc.addPage();
          yOffset = 15;
        }
        if (line.startsWith('* ')) {
          doc.text('• ', margin, yOffset);
          doc.text(line.slice(2), margin + 5, yOffset);
        } else if (line.match(/^#{1,3}\s/)) {
          doc.setFont('helvetica', 'bold');
          doc.text(line.replace(/^#{1,3}\s/, ''), margin, yOffset);
          doc.setFont('helvetica', 'normal');
        } else {
          doc.text(line, margin, yOffset);
        }
        yOffset += 6;
      });
      yOffset += 8;
    });
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
    <div className="flex flex-col items-center p-4 w-full  mx-auto">
      <h2 className="text-white text-2xl font-bold mb-4">Story Mode</h2>
      <div className="flex justify-end mb-4">
        <button onClick={handleDownloadPDF} className="bg-[#7847eb] hover:bg-[#5b36b2] text-white px-4 py-2 rounded-lg">Download PDF</button>
      </div>
      <div className="max-h-[calc(100vh-200px)] overflow-y-auto bg-[#2d2938] text-white p-6 rounded-lg w-full mb-4">
        {explanations.length > 0 ? (
          explanations.map((exp, idx) => (
            <div key={idx} className="mb-8">
              <h3 className="text-xl font-bold mb-4 text-[#7847eb]">{exp.section}</h3>
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
                {exp.explanation}
              </ReactMarkdown>
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

export default StoryModeDisplay;
