import React, { useState, useRef } from "react";
import axios from "axios";
import jsPDF from 'jspdf';
import { saveAs } from 'file-saver';
import config from '../config';

export default function QABlogUI() {
  const [topic, setTopic] = useState("");
  const [conversation, setConversation] = useState([]);
  const [userInput, setUserInput] = useState("");
  const [blogResult, setBlogResult] = useState(null);
  const [isReadyToWrite, setIsReadyToWrite] = useState(false);
  const [loading, setLoading] = useState(false);
  const [youtubeUrl, setYoutubeUrl] = useState("");
  const [additionalContext, setAdditionalContext] = useState("");
  const [activeTab, setActiveTab] = useState("topic"); // "topic" or "youtube"
  const [blogTitle, setBlogTitle] = useState("");
  const [subtopics, setSubtopics] = useState([]);
  const [detailed, setDetailed] = useState(true); // Toggle for detailed vs concise blogs
  const blogContentRef = useRef(null);

  // Add CSS for animations and enhanced styling
  React.useEffect(() => {
    const style = document.createElement("style");
    style.textContent = `
      @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
      }
      
      @keyframes fadeIn {
        0% { opacity: 0; transform: translateY(20px); }
        100% { opacity: 1; transform: translateY(0); }
      }
      
      @keyframes slideInUp {
        0% { opacity: 0; transform: translateY(30px); }
        100% { opacity: 1; transform: translateY(0); }
      }
      
      @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.05); }
      }
      
      @keyframes glow {
        0%, 100% { box-shadow: 0 0 5px rgba(99, 102, 241, 0.5); }
        50% { box-shadow: 0 0 20px rgba(99, 102, 241, 0.8); }
      }
      
      .blog-card {
        transition: all 0.3s ease;
      }
      
      .blog-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 20px 50px rgba(0, 0, 0, 0.15) !important;
      }
      
      .gradient-text {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #ec4899 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
      }
      
      .shimmer {
        background: linear-gradient(90deg, #f0f2f5 25%, #e4e6ea 50%, #f0f2f5 75%);
        background-size: 200% 100%;
        animation: shimmer 1.5s infinite;
      }
      
      @keyframes shimmer {
        0% { background-position: -200% 0; }
        100% { background-position: 200% 0; }
      }
    `;
    document.head.appendChild(style);
    return () => document.head.removeChild(style);
  }, []);

  const startInterview = async () => {
    if (!topic.trim()) return alert("Please enter a topic!");
    setConversation([]);
    setBlogResult(null);
    setIsReadyToWrite(false);

    setLoading(true);
    try {
      const res = await axios.post(`${config.API_BASE_URL}/api/blog/plan`, {
        topic: topic
      });
      
      if (res.data.success) {
        setConversation([{ 
          role: "agent", 
          content: `I've planned your blog about "${topic}". Here's what I suggest to cover:\n\nTitle: ${res.data.title}\n\nSubtopics:\n${res.data.subtopics.map((subtopic, i) => `${i+1}. ${subtopic}`).join('\n')}\n\nWould you like to proceed with these topics or modify them?`
        }]);
        setBlogTitle(res.data.title);
        setSubtopics(res.data.subtopics);
        setIsReadyToWrite(true);
      } else {
        alert("Error planning blog: " + res.data.error);
      }
    } catch (error) {
      console.error("Error:", error);
      alert("Error connecting to server");
    }
    setLoading(false);
  };

  const sendAnswer = async () => {
    if (!userInput.trim()) return;

    const updatedConversation = [
      ...conversation,
      { role: "user", content: userInput }
    ];
    setConversation(updatedConversation);
    setUserInput("");

    setLoading(true);
    try {
      // For now, just add user feedback to conversation
      // In a full implementation, you might want to re-plan the blog based on feedback
      const agentReply = `Thank you for your feedback: "${userInput}". I'll keep that in mind when generating the blog. You can now proceed to generate the blog with the current topics, or provide more feedback.`;
      updatedConversation.push({ role: "agent", content: agentReply });
      setConversation([...updatedConversation]);
    } catch (error) {
      console.error("Error:", error);
    }
    setLoading(false);
    setIsReadyToWrite(true);
  };

  const generateBlog = async () => {
    setLoading(true);
    try {
      const res = await axios.post(`${config.API_BASE_URL}/api/blog/generate`, {
        mainTopic: topic,
        subtopics: subtopics,
        title: blogTitle
      });
      
      if (res.data.success) {
        setBlogResult(res.data);
      } else {
        alert("Error generating blog: " + res.data.error);
      }
    } catch (error) {
      console.error("Error:", error);
      alert("Error generating blog. Please try again.");
    }
    setLoading(false);
  };

  const quickGenerate = async () => {
    if (!topic.trim()) return alert("Please enter a topic!");
    
    setLoading(true);
    setBlogResult(null);
    setConversation([]);
    
    try {
      const res = await axios.post(`${config.API_BASE_URL}/quick-generate`, {
        topic: topic,
        detailed: detailed
      });
      
      if (res.data.success !== false) {
        setBlogResult({
          blogContent: res.data.blogContent,
          summary: res.data.summary,
          keywords: res.data.keywords || []
        });
      } else {
        alert("Error generating blog: " + (res.data.error || "Unknown error"));
      }
    } catch (error) {
      console.error("Error:", error);
      alert("Error generating blog. Please try again.");
    }
    setLoading(false);
  };

  const generateFromYoutube = async () => {
    if (!youtubeUrl.trim()) return alert("Please enter a YouTube URL!");
    
    // Basic YouTube URL validation
    const youtubeRegex = /^(https?:\/\/)?(www\.)?(youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)/;
    if (!youtubeRegex.test(youtubeUrl)) {
      return alert("Please enter a valid YouTube URL!");
    }
    
    setLoading(true);
    setBlogResult(null);
    setConversation([]);
    
    try {
      const res = await axios.post(`${config.API_BASE_URL}/youtube-generate`, {
        youtubeUrl: youtubeUrl,
        additionalContext: additionalContext,
        detailed: detailed
      });
      
      if (res.data.success !== false) {
        setBlogResult({
          blogContent: res.data.blogContent,
          summary: res.data.summary,
          keywords: res.data.keywords || [],
          source: res.data.source || null
        });
      } else {
        alert("Error generating blog: " + (res.data.error || "Unknown error"));
      }
    } catch (error) {
      console.error("Error:", error);
      const errorMessage = "Error generating blog from YouTube video. Please try again.";
      alert(errorMessage);
    }
    setLoading(false);
  };

  const resetAll = () => {
    setTopic("");
    setConversation([]);
    setUserInput("");
    setBlogResult(null);
    setIsReadyToWrite(false);
    setYoutubeUrl("");
    setAdditionalContext("");
    setActiveTab("topic");
    setBlogTitle("");
    setSubtopics([]);
    setDetailed(true); // Reset to default detailed mode
  };

  // Format blog content in simple, clean blog format like real-world blogs
  const formatBlogContent = (content) => {
    if (!content) return '';
    
    // Step 1: Clean up the content and handle \n properly
    let cleanContent = content
      .replace(/\\n/g, '\n') // Convert escaped \n to actual newlines
      .replace(/\n{3,}/g, '\n\n') // Normalize multiple line breaks
      .replace(/#{1,6}\s*/g, '') // Remove markdown # symbols
      .replace(/\*{2,}/g, '') // Remove ** and ***
      .replace(/`{1,3}[^`]*`{1,3}/g, '') // Remove code blocks
      .replace(/```[^`]*```/g, '') // Remove code fences
      .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1') // Convert links to text
      .trim();

    // Step 2: Split into sections based on double line breaks
    const sections = cleanContent.split(/\n\s*\n/).filter(section => section.trim());
    
    let formattedHTML = '';
    let titleFound = false;
    
    sections.forEach((section, index) => {
      section = section.trim();
      if (!section) return;
      
      // Step 3: Detect content type with better logic
      const words = section.split(' ').length;
      const endsWithPeriod = section.endsWith('.');
      const isShortLine = words <= 15;
      const isVeryShortLine = words <= 8;
      const startsWithNumber = /^\d+\./.test(section);
      const startsWithBullet = /^[-•*]/.test(section);
      const isQuestionOrTitle = section.includes('?') || (!titleFound && isVeryShortLine && !endsWithPeriod);
      
      // Determine content type
      if (!titleFound && (isQuestionOrTitle || (index === 0 && isShortLine))) {
        // Main blog title
        titleFound = true;
        formattedHTML += `
          <h1 style="
            font-size: 32px;
            font-weight: 700;
            margin: 30px 0 25px 0;
            text-align: center;
            color: #1a202c;
            border-bottom: 3px solid #667eea;
            padding-bottom: 15px;
            font-family: 'Georgia', serif;
            line-height: 1.3;
          ">${highlightImportantWords(section)}</h1>
        `;
      } else if (isShortLine && !endsWithPeriod && !startsWithBullet && !startsWithNumber) {
        // Section heading
        formattedHTML += `
          <h2 style="
            font-size: 24px;
            font-weight: 600;
            margin: 30px 0 15px 0;
            color: #2d3748;
            border-left: 5px solid #667eea;
            padding-left: 20px;
            font-family: 'Georgia', serif;
            line-height: 1.4;
            background: linear-gradient(90deg, #f7fafc 0%, transparent 100%);
            padding-top: 10px;
            padding-bottom: 10px;
          ">${highlightImportantWords(section)}</h2>
        `;
      } else if (startsWithBullet || startsWithNumber || section.includes('\n•') || section.includes('\n-')) {
        // Handle lists (bullet points or numbered)
        const lines = section.split('\n').filter(line => line.trim());
        formattedHTML += '<ul style="margin: 20px 0; padding-left: 0; list-style: none;">';
        
        lines.forEach(line => {
          line = line.trim();
          if (line && (line.startsWith('•') || line.startsWith('-') || line.startsWith('*') || /^\d+\./.test(line))) {
            // Remove bullet/number prefix
            const cleanLine = line.replace(/^[-•*]\s*/, '').replace(/^\d+\.\s*/, '');
            formattedHTML += `
              <li style="
                margin: 12px 0;
                padding: 12px 0 12px 25px;
                position: relative;
                line-height: 1.6;
                font-size: 16px;
                font-family: 'Georgia', serif;
                border-left: 2px solid #e2e8f0;
                padding-left: 20px;
              ">
                <span style="
                  position: absolute;
                  left: -8px;
                  top: 12px;
                  width: 8px;
                  height: 8px;
                  background: #667eea;
                  border-radius: 50%;
                "></span>
                ${highlightImportantWords(cleanLine)}
              </li>
            `;
          } else if (line) {
            // Regular line within a list context
            formattedHTML += `
              <li style="
                margin: 8px 0;
                padding-left: 20px;
                line-height: 1.6;
                font-size: 16px;
                font-family: 'Georgia', serif;
              ">${highlightImportantWords(line)}</li>
            `;
          }
        });
        formattedHTML += '</ul>';
      } else {
        // Regular paragraph - handle multi-line content properly
        const lines = section.split('\n').filter(line => line.trim());
        const paragraphContent = lines.join(' '); // Join lines with spaces
        
        formattedHTML += `
          <p style="
            margin: 20px 0;
            line-height: 1.8;
            font-size: 16px;
            text-align: justify;
            font-family: 'Georgia', serif;
            color: #2d3748;
            text-indent: 30px;
            background: #fafbfc;
            padding: 15px 20px;
            border-radius: 8px;
            border-left: 3px solid #e2e8f0;
          ">${highlightImportantWords(paragraphContent)}</p>
        `;
      }
    });
    
    // Add some final styling
    return `<div style="max-width: 800px; margin: 0 auto; padding: 20px;">${formattedHTML}</div>`;
  };

  // Simple function to make important words bold
  const highlightImportantWords = (text) => {
    if (!text) return '';
    
    // Clean important word patterns - only the most essential ones
    const patterns = [
      // Technical terms
      /\b(artificial intelligence|AI|machine learning|ML|deep learning|neural networks|blockchain|cryptocurrency|cybersecurity|automation|robotics|quantum computing|data science|big data|IoT|5G|cloud computing)\b/gi,
      
      // Key business terms
      /\b(research|study|analysis|innovation|development|strategy|solution|technology|performance|efficiency|results|findings|conclusion)\b/gi,
      
      // Numbers and statistics
      /\b\d+%|\b\d{4}|\$[\d,]+|\b\d+(?:,\d{3})*\b/g,
      
      // Important emphasis words
      /\b(important|significant|critical|essential|major|key|primary|fundamental|crucial|advanced|comprehensive)\b/gi
    ];
    
    let result = text;
    
    // Apply simple bold formatting
    patterns.forEach(pattern => {
      result = result.replace(pattern, '<strong>$&</strong>');
    });
    
    return result;
  };

  // Download as PDF with same formatting as UI
  const downloadPDF = () => {
    if (!blogResult || !blogResult.blogContent) return;
    
    // Create a new jsPDF instance
    const doc = new jsPDF({
      orientation: 'portrait',
      unit: 'mm',
      format: 'a4'
    });
    
    const pageWidth = doc.internal.pageSize.getWidth();
    const pageHeight = doc.internal.pageSize.getHeight();
    const margin = 20;
    let yPosition = margin;
    
    // Helper function to add text with word wrapping and proper spacing
    const addText = (text, fontSize, fontStyle = 'normal', color = [0, 0, 0], isTitle = false, isHeading = false) => {
      // Check if we need a new page
      const estimatedHeight = fontSize * 1.2;
      if (yPosition + estimatedHeight > pageHeight - margin) {
        doc.addPage();
        yPosition = margin;
      }
      
      doc.setFontSize(fontSize);
      doc.setFont(undefined, fontStyle);
      doc.setTextColor(...color);
      
      const lines = doc.splitTextToSize(text, pageWidth - 2 * margin);
      
      // Add title spacing and centering
      if (isTitle) {
        yPosition += 10; // Extra space before title
        lines.forEach(line => {
          const textWidth = doc.getTextWidth(line);
          const x = (pageWidth - textWidth) / 2; // Center the text
          doc.text(line, x, yPosition);
          yPosition += fontSize * 0.6;
        });
        // Add underline for title
        const titleWidth = doc.getTextWidth(lines[0]);
        const titleX = (pageWidth - titleWidth) / 2;
        doc.setLineWidth(0.5);
        doc.line(titleX, yPosition + 2, titleX + titleWidth, yPosition + 2);
        yPosition += 8;
      } else {
        lines.forEach(line => {
          if (yPosition > pageHeight - margin) {
            doc.addPage();
            yPosition = margin;
          }
          doc.text(line, margin, yPosition);
          yPosition += fontSize * 0.6;
        });
        
        // Add spacing after sections
        if (isHeading) {
          yPosition += 5;
        } else {
          yPosition += 4;
        }
      }
    };

    // Process content using same logic as UI formatBlogContent
    let cleanContent = blogResult.blogContent
      .replace(/\\n/g, '\n') // Convert escaped \n to actual newlines
      .replace(/\n{3,}/g, '\n\n') // Normalize multiple line breaks
      .replace(/#{1,6}\s*/g, '') // Remove markdown # symbols
      .replace(/\*{2,}/g, '') // Remove ** and ***
      .replace(/`{1,3}[^`]*`{1,3}/g, '') // Remove code blocks
      .replace(/```[^`]*```/g, '') // Remove code fences
      .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1') // Convert links to text
      .replace(/<[^>]*>/g, '') // Remove any HTML tags
      .trim();

    // Split into sections based on double line breaks
    const sections = cleanContent.split(/\n\s*\n/).filter(section => section.trim());
    
    let titleFound = false;
    
    sections.forEach((section, index) => {
      section = section.trim();
      if (!section) return;
      
      // Apply same logic as UI formatting
      const words = section.split(' ').length;
      const endsWithPeriod = section.endsWith('.');
      const isShortLine = words <= 15;
      const isVeryShortLine = words <= 8;
      const startsWithNumber = /^\d+\./.test(section);
      const startsWithBullet = /^[-•*]/.test(section);
      const isQuestionOrTitle = section.includes('?') || (!titleFound && isVeryShortLine && !endsWithPeriod);
      
      // Clean text for PDF (remove HTML tags that might be left)
      const cleanText = section.replace(/<[^>]*>/g, '').replace(/&[^;]+;/g, '');
      
      if (!titleFound && (isQuestionOrTitle || (index === 0 && isShortLine))) {
        // Main blog title
        titleFound = true;
        addText(cleanText, 18, 'bold', [26, 32, 44], true, false);
      } else if (isShortLine && !endsWithPeriod && !startsWithBullet && !startsWithNumber) {
        // Section heading
        addText(cleanText, 14, 'bold', [52, 73, 94], false, true);
      } else if (startsWithBullet || startsWithNumber || section.includes('\n•') || section.includes('\n-')) {
        // Handle lists
        const lines = section.split('\n').filter(line => line.trim());
        
        lines.forEach(line => {
          line = line.trim();
          if (line && (line.startsWith('•') || line.startsWith('-') || line.startsWith('*') || /^\d+\./.test(line))) {
            // Remove bullet/number prefix and add custom bullet
            const cleanLine = line.replace(/^[-•*]\s*/, '').replace(/^\d+\.\s*/, '');
            addText(`• ${cleanLine}`, 11, 'normal', [44, 62, 80]);
          } else if (line) {
            // Regular line within list context
            addText(`  ${line}`, 11, 'normal', [44, 62, 80]);
          }
        });
      } else {
        // Regular paragraph
        const lines = section.split('\n').filter(line => line.trim());
        const paragraphContent = lines.join(' ');
        addText(paragraphContent, 11, 'normal', [44, 62, 80]);
      }
    });
    
    // Add footer with generation info
    if (blogResult.summary || blogResult.keywords) {
      yPosition += 15;
      
      // Add a separator line
      doc.setLineWidth(0.3);
      doc.line(margin, yPosition, pageWidth - margin, yPosition);
      yPosition += 10;
      
      if (blogResult.summary) {
        addText('Summary', 13, 'bold', [41, 128, 185], false, true);
        addText(blogResult.summary, 10, 'normal', [127, 140, 141]);
      }
      
      if (blogResult.keywords && blogResult.keywords.length > 0) {
        addText('Keywords', 13, 'bold', [41, 128, 185], false, true);
        addText(blogResult.keywords.join(', '), 10, 'italic', [127, 140, 141]);
      }
    }
    
    // Add page numbers
    const pageCount = doc.internal.getNumberOfPages();
    for (let i = 1; i <= pageCount; i++) {
      doc.setPage(i);
      doc.setFontSize(8);
      doc.setTextColor(127, 140, 141);
      doc.text(`Page ${i} of ${pageCount}`, pageWidth - margin - 15, pageHeight - 10);
    }
    
    doc.save(`${topic.replace(/\s+/g, '-').toLowerCase()}.pdf`);
  };

  // Download as Markdown
  const downloadMarkdown = () => {
    if (!blogResult || !blogResult.blogContent) return;
    
    const markdownContent = `# ${topic}\n\n${blogResult.blogContent
      .replace(/<[^>]*>/g, '') // Remove HTML tags
      .replace(/\*{2,}/g, '') // Remove extra asterisks
    }\n\n## Summary\n${blogResult.summary}\n\n## Keywords\n${blogResult.keywords.join(', ')}`;
    
    const blob = new Blob([markdownContent], { type: 'text/markdown;charset=utf-8' });
    saveAs(blob, `blog-${topic.replace(/\s+/g, '-').toLowerCase()}.md`);
  };

  // Copy to clipboard
  const copyToClipboard = () => {
    if (!blogResult || !blogResult.blogContent) return;
    
    const plainText = blogResult.blogContent
      .replace(/<[^>]*>/g, '') // Remove HTML tags
      .replace(/\*{1,}/g, ''); // Remove asterisks
      
    navigator.clipboard.writeText(plainText).then(() => {
      alert('Blog content copied to clipboard!');
    });
  };

  return (
    <div style={{ 
      maxWidth: "1200px", 
      margin: "auto", 
      padding: "20px", 
      fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
      backgroundColor: "#0f172a",
      minHeight: "100vh"
    }}>
      {/* Enhanced Hero Section */}
      <div style={{
        textAlign: "center",
        marginBottom: "50px",
        padding: "50px 40px",
        background: "linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #ec4899 100%)",
        borderRadius: "24px",
        color: "white",
        boxShadow: "0 25px 50px -12px rgba(0, 0, 0, 0.25)",
        position: "relative",
        overflow: "hidden"
      }}>
        {/* Background Pattern */}
        <div style={{
          position: "absolute",
          top: "0",
          left: "0",
          right: "0",
          bottom: "0",
          backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.1'%3E%3Ccircle cx='30' cy='30' r='1'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`,
          opacity: "0.3"
        }}></div>
        
        <div style={{ position: "relative", zIndex: "2" }}>
          <div style={{
            display: "inline-flex",
            alignItems: "center",
            gap: "12px",
            marginBottom: "20px"
          }}>
            <div style={{
              width: "50px",
              height: "50px",
              background: "rgba(255, 255, 255, 0.2)",
              borderRadius: "12px",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontSize: "24px",
              backdropFilter: "blur(10px)"
            }}>
              ✨
            </div>
            <h1 style={{ 
              fontSize: "42px", 
              fontWeight: "800", 
              margin: "0",
              textShadow: "0 4px 8px rgba(0,0,0,0.3)",
              background: "linear-gradient(135deg, #ffffff 0%, #f1f5f9 100%)",
              WebkitBackgroundClip: "text",
              WebkitTextFillColor: "transparent",
              backgroundClip: "text"
            }}>
              AI Blog Generator
            </h1>
          </div>
          
          <p style={{ 
            fontSize: "18px", 
            margin: "0 0 30px 0", 
            opacity: "0.95",
            fontWeight: "400",
            letterSpacing: "0.5px"
          }}>
            Transform ideas into professional, SEO-optimized blog posts with AI-powered content generation
          </p>
          
          {/* Stats Section */}
          <div style={{
            display: "flex",
            justifyContent: "center",
            gap: "40px",
            marginTop: "30px",
            flexWrap: "wrap"
          }}>
            <div style={{ textAlign: "center" }}>
              <div style={{ fontSize: "24px", fontWeight: "700", marginBottom: "5px" }}>1000+</div>
              <div style={{ fontSize: "14px", opacity: "0.9" }}>Blogs Generated</div>
            </div>
            <div style={{ textAlign: "center" }}>
              <div style={{ fontSize: "24px", fontWeight: "700", marginBottom: "5px" }}>95%</div>
              <div style={{ fontSize: "14px", opacity: "0.9" }}>Quality Score</div>
            </div>
            <div style={{ textAlign: "center" }}>
              <div style={{ fontSize: "24px", fontWeight: "700", marginBottom: "5px" }}>60s</div>
              <div style={{ fontSize: "14px", opacity: "0.9" }}>Avg Generation</div>
            </div>
          </div>
        </div>
      </div>

      {!conversation.length && !blogResult && (
        <div style={{
          backgroundColor: "#1e293b",
          padding: "40px",
          borderRadius: "20px",
          boxShadow: "0 10px 40px rgba(0,0,0,0.2)",
          border: "1px solid #334155",
          marginBottom: "40px",
          position: "relative",
          overflow: "hidden"
        }}>
          {/* Background gradient overlay */}
          <div style={{
            position: "absolute",
            top: "0",
            left: "0",
            right: "0",
            height: "4px",
            background: "linear-gradient(90deg, #6366f1 0%, #8b5cf6 50%, #ec4899 100%)"
          }}></div>
          
          {/* Enhanced Tab Navigation */}
          <div style={{
            display: "flex",
            marginBottom: "35px",
            background: "#0f172a",
            borderRadius: "12px",
            padding: "6px",
            position: "relative"
          }}>
            <button
              onClick={() => setActiveTab("topic")}
              style={{
                flex: "1",
                padding: "16px 24px",
                border: "none",
                background: activeTab === "topic" 
                  ? "linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)" 
                  : "transparent",
                color: activeTab === "topic" ? "white" : "#94a3b8",
                fontSize: "16px",
                fontWeight: "600",
                borderRadius: "8px",
                cursor: "pointer",
                transition: "all 0.3s ease",
                position: "relative",
                zIndex: "2",
                boxShadow: activeTab === "topic" 
                  ? "0 4px 12px rgba(99, 102, 241, 0.4)" 
                  : "none"
              }}
            >
              <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: "8px" }}>
                <span style={{ fontSize: "20px" }}>📝</span>
                <span>Topic-Based Blog</span>
              </div>
            </button>
            <button
              onClick={() => setActiveTab("youtube")}
              style={{
                flex: "1",
                padding: "16px 24px",
                border: "none",
                background: activeTab === "youtube" 
                  ? "linear-gradient(135deg, #ef4444 0%, #f97316 100%)" 
                  : "transparent",
                color: activeTab === "youtube" ? "white" : "#94a3b8",
                fontSize: "16px",
                fontWeight: "600",
                borderRadius: "8px",
                cursor: "pointer",
                transition: "all 0.3s ease",
                position: "relative",
                zIndex: "2",
                boxShadow: activeTab === "youtube" 
                  ? "0 4px 12px rgba(239, 68, 68, 0.4)" 
                  : "none"
              }}
            >
              <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: "8px" }}>
                <span style={{ fontSize: "20px" }}>🎥</span>
                <span>YouTube-Based Blog</span>
              </div>
            </button>
          </div>

          {/* Detailed Toggle */}
          <div style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            margin: "20px 0",
            padding: "16px",
            background: "linear-gradient(135deg, #1e293b 0%, #334155 100%)",
            borderRadius: "12px",
            border: "1px solid #475569"
          }}>
            <div style={{ display: "flex", alignItems: "center", gap: "16px" }}>
              <span style={{
                fontSize: "16px",
                fontWeight: "600",
                color: "#e2e8f0"
              }}>
                Blog Style:
              </span>
              <div style={{ display: "flex", gap: "8px" }}>
                <button
                  onClick={() => setDetailed(true)}
                  style={{
                    padding: "8px 16px",
                    border: "none",
                    borderRadius: "8px",
                    fontSize: "14px",
                    fontWeight: "600",
                    cursor: "pointer",
                    transition: "all 0.3s ease",
                    background: detailed
                      ? "linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)"
                      : "#475569",
                    color: detailed ? "white" : "#cbd5e1",
                    boxShadow: detailed
                      ? "0 4px 12px rgba(99, 102, 241, 0.4)"
                      : "none"
                  }}
                >
                  📖 Detailed (1200+ words)
                </button>
                <button
                  onClick={() => setDetailed(false)}
                  style={{
                    padding: "8px 16px",
                    border: "none",
                    borderRadius: "8px",
                    fontSize: "14px",
                    fontWeight: "600",
                    cursor: "pointer",
                    transition: "all 0.3s ease",
                    background: !detailed
                      ? "linear-gradient(135deg, #10b981 0%, #059669 100%)"
                      : "#475569",
                    color: !detailed ? "white" : "#cbd5e1",
                    boxShadow: !detailed
                      ? "0 4px 12px rgba(16, 185, 129, 0.4)"
                      : "none"
                  }}
                >
                  📄 Concise (600 words)
                </button>
              </div>
            </div>
          </div>

          {/* Enhanced Topic Tab Content */}
          {activeTab === "topic" && (
            <div style={{ animation: "fadeIn 0.3s ease-in-out" }}>
              <div style={{
                background: "linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%)",
                padding: "25px",
                borderRadius: "16px",
                marginBottom: "25px",
                border: "1px solid #e2e8f0"
              }}>
                <h3 style={{ 
                  fontSize: "20px", 
                  fontWeight: "700", 
                  color: "#1e293b", 
                  marginTop: "0",
                  marginBottom: "15px",
                  display: "flex",
                  alignItems: "center",
                  gap: "10px"
                }}>
                  <div style={{
                    width: "32px",
                    height: "32px",
                    background: "linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)",
                    borderRadius: "8px",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    fontSize: "16px",
                    color: "white"
                  }}>
                    💡
                  </div>
                  What would you like to write about?
                </h3>
                <p style={{
                  color: "#64748b",
                  margin: "0 0 20px 0",
                  fontSize: "15px",
                  lineHeight: "1.6"
                }}>
                  Enter any topic and let our AI create a comprehensive, well-researched blog post for you.
                </p>
              </div>
              
              <div style={{ position: "relative", marginBottom: "25px" }}>
                <input
                  type="text"
                  placeholder="Enter your blog topic (e.g., Artificial Intelligence in Healthcare, Sustainable Energy Solutions...)"
                  value={topic}
                  onChange={(e) => setTopic(e.target.value)}
                  style={{ 
                    width: "100%", 
                    padding: "18px 24px", 
                    border: "2px solid #334155",
                    borderRadius: "12px",
                    fontSize: "16px",
                    fontFamily: "inherit",
                    outline: "none",
                    transition: "all 0.3s ease",
                    backgroundColor: "#0f172a",
                    color: "#e2e8f0",
                    boxShadow: "inset 0 2px 4px rgba(0, 0, 0, 0.1)"
                  }}
                  onFocus={(e) => {
                    e.target.style.borderColor = "#8b5cf6";
                    e.target.style.boxShadow = "inset 0 2px 4px rgba(0, 0, 0, 0.1), 0 0 0 3px rgba(139, 92, 246, 0.1)";
                  }}
                  onBlur={(e) => {
                    e.target.style.borderColor = "#334155";
                    e.target.style.boxShadow = "inset 0 2px 4px rgba(0, 0, 0, 0.1)";
                  }}
                />
              </div>
              
              <div style={{ display: "flex", gap: "16px", flexWrap: "wrap" }}>
                <button 
                  onClick={startInterview} 
                  disabled={loading || !topic.trim()}
                  style={{
                    flex: "1",
                    minWidth: "250px",
                    padding: "18px 24px",
                    background: topic.trim() && !loading 
                      ? "linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)" 
                      : "#94a3b8",
                    color: "white",
                    border: "none",
                    borderRadius: "12px",
                    fontSize: "16px",
                    fontWeight: "600",
                    cursor: topic.trim() && !loading ? "pointer" : "not-allowed",
                    transition: "all 0.3s ease",
                    boxShadow: topic.trim() && !loading 
                      ? "0 8px 25px rgba(99, 102, 241, 0.3)" 
                      : "none",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    gap: "10px",
                    position: "relative",
                    overflow: "hidden"
                  }}
                  onMouseOver={(e) => {
                    if (topic.trim() && !loading) {
                      e.target.style.transform = "translateY(-2px)";
                      e.target.style.boxShadow = "0 12px 35px rgba(99, 102, 241, 0.4)";
                    }
                  }}
                  onMouseOut={(e) => {
                    e.target.style.transform = "translateY(0)";
                    e.target.style.boxShadow = topic.trim() && !loading 
                      ? "0 8px 25px rgba(99, 102, 241, 0.3)" 
                      : "none";
                  }}
                >
                  {loading ? (
                    <>
                      <div style={{
                        width: "20px",
                        height: "20px",
                        border: "2px solid rgba(255,255,255,0.3)",
                        borderTopColor: "white",
                        borderRadius: "50%",
                        animation: "spin 1s linear infinite"
                      }}></div>
                      Planning Content...
                    </>
                  ) : (
                    <>
                      <span style={{ fontSize: "18px" }}>📝</span>
                      Get Overview & Customize
                    </>
                  )}
                </button>
                
                <button 
                  onClick={quickGenerate} 
                  disabled={loading || !topic.trim()}
                  style={{
                    flex: "1",
                    minWidth: "250px",
                    padding: "18px 24px",
                    background: topic.trim() && !loading 
                      ? "linear-gradient(135deg, #10b981 0%, #059669 100%)" 
                      : "#94a3b8",
                    color: "white",
                    border: "none",
                    borderRadius: "12px",
                    fontSize: "16px",
                    fontWeight: "600",
                    cursor: topic.trim() && !loading ? "pointer" : "not-allowed",
                    transition: "all 0.3s ease",
                    boxShadow: topic.trim() && !loading 
                      ? "0 8px 25px rgba(16, 185, 129, 0.3)" 
                      : "none",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    gap: "10px"
                  }}
                  onMouseOver={(e) => {
                    if (topic.trim() && !loading) {
                      e.target.style.transform = "translateY(-2px)";
                      e.target.style.boxShadow = "0 12px 35px rgba(16, 185, 129, 0.4)";
                    }
                  }}
                  onMouseOut={(e) => {
                    e.target.style.transform = "translateY(0)";
                    e.target.style.boxShadow = topic.trim() && !loading 
                      ? "0 8px 25px rgba(16, 185, 129, 0.3)" 
                      : "none";
                  }}
                >
                  {loading ? (
                    <>
                      <div style={{
                        width: "20px",
                        height: "20px",
                        border: "2px solid rgba(255,255,255,0.3)",
                        borderTopColor: "white",
                        borderRadius: "50%",
                        animation: "spin 1s linear infinite"
                      }}></div>
                      Generating...
                    </>
                  ) : (
                    <>
                      <span style={{ fontSize: "18px" }}>⚡</span>
                      Quick Generate
                    </>
                  )}
                </button>
              </div>
              
              {/* Enhanced Info Cards */}
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px", marginTop: "25px" }}>
                <div style={{ 
                  padding: "20px", 
                  backgroundColor: "#1e293b", 
                  borderRadius: "12px",
                  border: "1px solid #0ea5e9",
                  borderLeft: "4px solid #0ea5e9"
                }}>
                  <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "8px" }}>
                    <span style={{ fontSize: "20px" }}>📝</span>
                    <span style={{ fontWeight: "600", color: "#38bdf8", fontSize: "14px" }}>
                      Overview & Customize
                    </span>
                  </div>
                  <p style={{ 
                    margin: "0", 
                    fontSize: "13px", 
                    color: "#94a3b8", 
                    lineHeight: "1.5"
                  }}>
                    Review the planned content structure and add your specific requirements before generation
                  </p>
                </div>
                
                <div style={{ 
                  padding: "20px", 
                  backgroundColor: "#1e293b", 
                  borderRadius: "12px",
                  border: "1px solid #22c55e",
                  borderLeft: "4px solid #22c55e"
                }}>
                  <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "8px" }}>
                    <span style={{ fontSize: "20px" }}>⚡</span>
                    <span style={{ fontWeight: "600", color: "#4ade80", fontSize: "14px" }}>
                      Quick Generate
                    </span>
                  </div>
                  <p style={{ 
                    margin: "0", 
                    fontSize: "13px", 
                    color: "#94a3b8", 
                    lineHeight: "1.5"
                  }}>
                    Instantly create a comprehensive, well-structured blog post with AI-generated content
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Enhanced YouTube Tab Content */}
          {activeTab === "youtube" && (
            <div style={{ animation: "fadeIn 0.3s ease-in-out" }}>
              <div style={{
                background: "linear-gradient(135deg, #fef2f2 0%, #fdf2f8 100%)",
                padding: "25px",
                borderRadius: "16px",
                marginBottom: "25px",
                border: "1px solid #fecaca"
              }}>
                <h3 style={{ 
                  fontSize: "20px", 
                  fontWeight: "700", 
                  color: "#1e293b", 
                  marginTop: "0",
                  marginBottom: "15px",
                  display: "flex",
                  alignItems: "center",
                  gap: "10px"
                }}>
                  <div style={{
                    width: "32px",
                    height: "32px",
                    background: "linear-gradient(135deg, #ef4444 0%, #f97316 100%)",
                    borderRadius: "8px",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    fontSize: "16px",
                    color: "white"
                  }}>
                    🎥
                  </div>
                  Generate Blog from YouTube Video
                </h3>
                <p style={{
                  color: "#64748b",
                  margin: "0 0 20px 0",
                  fontSize: "15px",
                  lineHeight: "1.6"
                }}>
                  Transform YouTube video content into comprehensive blog posts with AI analysis.
                </p>
              </div>
              
              <div style={{ marginBottom: "20px" }}>
                <label style={{
                  display: "block",
                  marginBottom: "8px",
                  fontSize: "14px",
                  fontWeight: "600",
                  color: "#374151"
                }}>
                  YouTube Video URL *
                </label>
                <input
                  type="text"
                  placeholder="https://youtube.com/watch?v=... or https://youtu.be/..."
                  value={youtubeUrl}
                  onChange={(e) => setYoutubeUrl(e.target.value)}
                  style={{ 
                    width: "100%", 
                    padding: "18px 24px", 
                    border: "2px solid #334155",
                    borderRadius: "12px",
                    fontSize: "16px",
                    fontFamily: "inherit",
                    outline: "none",
                    transition: "all 0.3s ease",
                    backgroundColor: "#0f172a",
                    color: "#e2e8f0",
                    boxShadow: "inset 0 2px 4px rgba(0, 0, 0, 0.1)"
                  }}
                  onFocus={(e) => {
                    e.target.style.borderColor = "#ef4444";
                    e.target.style.boxShadow = "inset 0 2px 4px rgba(0, 0, 0, 0.1), 0 0 0 3px rgba(239, 68, 68, 0.1)";
                  }}
                  onBlur={(e) => {
                    e.target.style.borderColor = "#334155";
                    e.target.style.boxShadow = "inset 0 2px 4px rgba(0, 0, 0, 0.1)";
                  }}
                />
              </div>
              
              <div style={{ marginBottom: "25px" }}>
                <label style={{
                  display: "block",
                  marginBottom: "8px",
                  fontSize: "14px",
                  fontWeight: "600",
                  color: "#374151"
                }}>
                  Additional Context (Optional)
                </label>
                <textarea
                  placeholder="Any specific aspects you want the blog to focus on, target audience, or writing style preferences..."
                  value={additionalContext}
                  onChange={(e) => setAdditionalContext(e.target.value)}
                  style={{ 
                    width: "100%", 
                    padding: "18px 24px", 
                    border: "2px solid #334155",
                    borderRadius: "12px",
                    fontSize: "15px",
                    fontFamily: "inherit",
                    outline: "none",
                    transition: "all 0.3s ease",
                    backgroundColor: "#0f172a",
                    color: "#e2e8f0",
                    minHeight: "100px",
                    resize: "vertical",
                    boxShadow: "inset 0 2px 4px rgba(0, 0, 0, 0.1)"
                  }}
                  onFocus={(e) => {
                    e.target.style.borderColor = "#ef4444";
                    e.target.style.boxShadow = "inset 0 2px 4px rgba(0, 0, 0, 0.1), 0 0 0 3px rgba(239, 68, 68, 0.1)";
                  }}
                  onBlur={(e) => {
                    e.target.style.borderColor = "#e2e8f0";
                    e.target.style.boxShadow = "inset 0 2px 4px rgba(0, 0, 0, 0.05)";
                  }}
                />
              </div>
              
              <button 
                onClick={generateFromYoutube} 
                disabled={loading || !youtubeUrl.trim()}
                style={{
                  width: "100%",
                  padding: "18px 24px",
                  background: youtubeUrl.trim() && !loading 
                    ? "linear-gradient(135deg, #ef4444 0%, #f97316 100%)" 
                    : "#94a3b8",
                  color: "white",
                  border: "none",
                  borderRadius: "12px",
                  fontSize: "16px",
                  fontWeight: "600",
                  cursor: youtubeUrl.trim() && !loading ? "pointer" : "not-allowed",
                  transition: "all 0.3s ease",
                  boxShadow: youtubeUrl.trim() && !loading 
                    ? "0 8px 25px rgba(239, 68, 68, 0.3)" 
                    : "none",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  gap: "10px"
                }}
                onMouseOver={(e) => {
                  if (youtubeUrl.trim() && !loading) {
                    e.target.style.transform = "translateY(-2px)";
                    e.target.style.boxShadow = "0 12px 35px rgba(239, 68, 68, 0.4)";
                  }
                }}
                onMouseOut={(e) => {
                  e.target.style.transform = "translateY(0)";
                  e.target.style.boxShadow = youtubeUrl.trim() && !loading 
                    ? "0 8px 25px rgba(239, 68, 68, 0.3)" 
                    : "none";
                }}
              >
                {loading ? (
                  <>
                    <div style={{
                      width: "20px",
                      height: "20px",
                      border: "2px solid rgba(255,255,255,0.3)",
                      borderTopColor: "white",
                      borderRadius: "50%",
                      animation: "spin 1s linear infinite"
                    }}></div>
                    Processing Video...
                  </>
                ) : (
                  <>
                    <span style={{ fontSize: "18px" }}>🎬</span>
                    Generate Blog from Video
                  </>
                )}
              </button>
              
              {/* Enhanced YouTube Info Card */}
              <div style={{ 
                marginTop: "25px", 
                padding: "20px", 
                backgroundColor: "#fef7ff", 
                borderRadius: "12px",
                border: "1px solid #e879f9",
                borderLeft: "4px solid #d946ef"
              }}>
                <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "12px" }}>
                  <span style={{ fontSize: "20px" }}>🎥</span>
                  <span style={{ fontWeight: "600", color: "#581c87", fontSize: "16px" }}>
                    How YouTube Blog Generation Works
                  </span>
                </div>
                <ul style={{ 
                  margin: "0", 
                  paddingLeft: "20px", 
                  color: "#581c87", 
                  lineHeight: "1.6",
                  fontSize: "14px"
                }}>
                  <li style={{ marginBottom: "8px" }}>� AI analyzes video content and transcript</li>
                  <li style={{ marginBottom: "8px" }}>📝 Extracts key points and main topics</li>
                  <li style={{ marginBottom: "8px" }}>✍️ Creates structured, readable blog content</li>
                  <li>🎨 Formats with proper headings and sections</li>
                </ul>
                <div style={{
                  marginTop: "15px",
                  padding: "12px",
                  background: "rgba(168, 85, 247, 0.1)",
                  borderRadius: "8px",
                  fontSize: "13px",
                  color: "#581c87"
                }}>
                  <strong>Note:</strong> Videos with captions or subtitles will produce better results
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {!conversation.length && !blogResult && (
        <div style={{ display: 'none' }}>
          {/* Google Custom Search widget removed from UI as requested */}
        </div>
      )}

      {conversation.length > 0 && (
        <div style={{ 
          marginTop: "30px",
          animation: "slideInUp 0.5s ease-out"
        }}>
          <div style={{
            textAlign: "center",
            marginBottom: "30px",
            background: "linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%)",
            padding: "25px",
            borderRadius: "16px",
            border: "1px solid #e2e8f0"
          }}>
            <h3 style={{ 
              color: "#1e293b", 
              fontSize: "28px", 
              fontWeight: "700", 
              marginBottom: "10px",
              margin: "0",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              gap: "12px"
            }}>
              <span style={{
                width: "40px",
                height: "40px",
                background: "linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)",
                borderRadius: "10px",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontSize: "20px"
              }}>
                📋
              </span>
              Blog Content Overview
            </h3>
            <p style={{
              color: "#64748b",
              margin: "8px 0 0 0",
              fontSize: "15px"
            }}>
              Review and customize your blog structure before final generation
            </p>
          </div>
          
          <div style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
            {conversation.map((msg, idx) => (
              <div 
                key={idx} 
                className="blog-card"
                style={{ 
                  background: msg.role === "agent" 
                    ? "linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)" 
                    : "linear-gradient(135deg, #10b981 0%, #059669 100%)", 
                  padding: "30px", 
                  borderRadius: "20px",
                  boxShadow: "0 10px 30px rgba(0,0,0,0.1)",
                  color: "white",
                  position: "relative",
                  overflow: "hidden",
                  animation: `slideInUp 0.5s ease-out ${idx * 0.1}s both`
                }}
              >
                {/* Enhanced background effect */}
                <div style={{
                  position: "absolute",
                  top: "0",
                  left: "0",
                  right: "0",
                  bottom: "0",
                  background: msg.role === "agent"
                    ? "radial-gradient(circle at 20% 80%, rgba(255,255,255,0.1) 0%, transparent 50%), radial-gradient(circle at 80% 20%, rgba(255,255,255,0.1) 0%, transparent 50%)"
                    : "radial-gradient(circle at 30% 70%, rgba(255,255,255,0.1) 0%, transparent 50%), radial-gradient(circle at 70% 30%, rgba(255,255,255,0.1) 0%, transparent 50%)",
                  borderRadius: "20px"
                }}></div>
                
                <div style={{ position: "relative", zIndex: "2" }}>
                  <div style={{ 
                    display: "flex", 
                    alignItems: "center", 
                    marginBottom: "20px",
                    fontSize: "16px",
                    fontWeight: "600"
                  }}>
                    <div style={{ 
                      background: "rgba(255,255,255,0.2)", 
                      padding: "10px 20px", 
                      borderRadius: "25px",
                      display: "flex",
                      alignItems: "center",
                      gap: "8px",
                      fontSize: "14px",
                      backdropFilter: "blur(10px)",
                      border: "1px solid rgba(255,255,255,0.1)"
                    }}>
                      <span style={{ fontSize: "20px" }}>
                        {msg.role === "agent" ? "🤖" : "👤"}
                      </span>
                      {msg.role === "agent" ? "AI Content Planner" : "Your Requirements"}
                    </div>
                  </div>
                  
                  <div 
                    style={{ 
                      lineHeight: "1.8", 
                      fontSize: "16px",
                      background: "rgba(255,255,255,0.1)",
                      padding: "25px",
                      borderRadius: "15px",
                      backdropFilter: "blur(10px)",
                      border: "1px solid rgba(255,255,255,0.1)"
                    }}
                    dangerouslySetInnerHTML={{
                      __html: msg.content
                        .replace(/\*\*(.+?)\*\*/g, '<span style="font-weight: bold; color: #ffd700; text-shadow: 0 1px 2px rgba(0,0,0,0.3);">$1</span>')
                        .replace(/\*(.+?)\*/g, '<span style="font-style: italic; color: #e8f4fd;">$1</span>')
                        .replace(/^(\*\s.+$)/gm, '<li style="margin: 12px 0; padding-left: 15px; position: relative;">$1</li>')
                        .replace(/(<li.*?>.*?<\/li>)/gs, '<ul style="margin: 15px 0; padding-left: 0; list-style: none;">$1</ul>')
                        .replace(/<li([^>]*)>\*\s*/g, '<li$1><span style="position: absolute; left: 0; color: #ffd700;">•</span>')
                        .replace(/\n/g, '<br/>')
                    }}
                  />
                </div>
              </div>
            ))}
          </div>

          {isReadyToWrite && (
            <div style={{ 
              marginTop: "30px", 
              background: "linear-gradient(135deg, #fef3c7 0%, #fde68a 100%)", 
              padding: "30px", 
              borderRadius: "20px",
              boxShadow: "0 10px 30px rgba(0,0,0,0.1)",
              position: "relative",
              overflow: "hidden",
              animation: "slideInUp 0.5s ease-out"
            }}>
              {/* Enhanced background pattern */}
              <div style={{
                position: "absolute",
                top: "0",
                left: "0",
                right: "0",
                bottom: "0",
                backgroundImage: `url("data:image/svg+xml,%3Csvg width='40' height='40' viewBox='0 0 40 40' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23f59e0b' fill-opacity='0.1'%3E%3Cpath d='M20 20c0-5.5-4.5-10-10-10s-10 4.5-10 10 4.5 10 10 10 10-4.5 10-10zm10 0c0-5.5-4.5-10-10-10s-10 4.5-10 10 4.5 10 10 10 10-4.5 10-10z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`,
                opacity: "0.5"
              }}></div>
              
              <div style={{ position: "relative", zIndex: "2" }}>
                <div style={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  gap: "12px",
                  marginBottom: "20px"
                }}>
                  <div style={{
                    width: "40px",
                    height: "40px",
                    background: "linear-gradient(135deg, #f59e0b 0%, #d97706 100%)",
                    borderRadius: "10px",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    fontSize: "20px",
                    color: "white",
                    boxShadow: "0 4px 15px rgba(245, 158, 11, 0.4)"
                  }}>
                    ✨
                  </div>
                  <h4 style={{ 
                    margin: "0", 
                    color: "#92400e",
                    fontSize: "22px",
                    fontWeight: "700"
                  }}>
                    Customize Your Content
                  </h4>
                </div>
                
                <p style={{
                  textAlign: "center",
                  color: "#92400e",
                  margin: "0 0 25px 0",
                  fontSize: "15px",
                  lineHeight: "1.6"
                }}>
                  Add specific examples, focus areas, or any particular angle you want covered in your blog post
                </p>
                
                <div style={{
                  background: "rgba(255, 255, 255, 0.7)",
                  padding: "20px",
                  borderRadius: "15px",
                  backdropFilter: "blur(10px)",
                  border: "1px solid rgba(255, 255, 255, 0.2)"
                }}>
                  <textarea
                    placeholder="Example: 'Focus on practical applications for small businesses', 'Include recent case studies from 2024', 'Write for beginner-level audience'..."
                    value={userInput}
                    onChange={(e) => setUserInput(e.target.value)}
                    style={{ 
                      width: "100%", 
                      padding: "18px", 
                      border: "2px solid #e5e7eb",
                      borderRadius: "12px",
                      fontSize: "15px",
                      lineHeight: "1.6",
                      minHeight: "100px",
                      resize: "vertical",
                      background: "#0f172a",
                      color: "#e2e8f0",
                      boxShadow: "inset 0 2px 4px rgba(0, 0, 0, 0.05)",
                      fontFamily: "inherit",
                      outline: "none",
                      transition: "all 0.3s ease"
                    }}
                    onFocus={(e) => {
                      e.target.style.borderColor = "#f59e0b";
                      e.target.style.boxShadow = "inset 0 2px 4px rgba(0, 0, 0, 0.05), 0 0 0 3px rgba(245, 158, 11, 0.1)";
                    }}
                    onBlur={(e) => {
                      e.target.style.borderColor = "#e5e7eb";
                      e.target.style.boxShadow = "inset 0 2px 4px rgba(0, 0, 0, 0.05)";
                    }}
                  />
                  
                  <div style={{ display: "flex", gap: "15px", marginTop: "20px" }}>
                    <button 
                      onClick={sendAnswer} 
                      disabled={loading}
                      style={{
                        padding: "14px 24px",
                        background: loading 
                          ? "#94a3b8" 
                          : "linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%)",
                        color: "white",
                        border: "none",
                        borderRadius: "12px",
                        cursor: loading ? "not-allowed" : "pointer",
                        fontSize: "15px",
                        fontWeight: "600",
                        boxShadow: loading 
                          ? "none" 
                          : "0 4px 15px rgba(59, 130, 246, 0.3)",
                        transition: "all 0.3s ease",
                        display: "flex",
                        alignItems: "center",
                        gap: "8px"
                      }}
                      onMouseOver={(e) => {
                        if (!loading) {
                          e.target.style.transform = "translateY(-2px)";
                          e.target.style.boxShadow = "0 6px 20px rgba(59, 130, 246, 0.4)";
                        }
                      }}
                      onMouseOut={(e) => {
                        e.target.style.transform = "translateY(0)";
                        e.target.style.boxShadow = loading 
                          ? "none" 
                          : "0 4px 15px rgba(59, 130, 246, 0.3)";
                      }}
                    >
                      <span>➕</span>
                      {loading ? "Adding..." : "Add Requirements"}
                    </button>
                    
                    <button 
                      onClick={generateBlog} 
                      disabled={loading}
                      style={{
                        flex: "1",
                        padding: "14px 24px",
                        background: loading 
                          ? "#94a3b8" 
                          : "linear-gradient(135deg, #10b981 0%, #047857 100%)",
                        color: "white",
                        border: "none",
                        borderRadius: "12px",
                        cursor: loading ? "not-allowed" : "pointer",
                        fontSize: "16px",
                        fontWeight: "700",
                        boxShadow: loading 
                          ? "none" 
                          : "0 8px 25px rgba(16, 185, 129, 0.3)",
                        transition: "all 0.3s ease",
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        gap: "10px",
                        position: "relative",
                        overflow: "hidden"
                      }}
                      onMouseOver={(e) => {
                        if (!loading) {
                          e.target.style.transform = "translateY(-2px)";
                          e.target.style.boxShadow = "0 12px 35px rgba(16, 185, 129, 0.4)";
                        }
                      }}
                      onMouseOut={(e) => {
                        e.target.style.transform = "translateY(0)";
                        e.target.style.boxShadow = loading 
                          ? "none" 
                          : "0 8px 25px rgba(16, 185, 129, 0.3)";
                      }}
                    >
                      {loading && (
                        <div style={{
                          position: "absolute",
                          left: "0",
                          top: "0",
                          right: "0",
                          bottom: "0",
                          background: "rgba(255, 255, 255, 0.1)",
                          animation: "shimmer 1.5s infinite"
                        }}></div>
                      )}
                      <span style={{ fontSize: "18px" }}>
                        {loading ? "🔄" : "🚀"}
                      </span>
                      {loading ? "Generating..." : "Generate Detailed Blog"}
                    </button>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {blogResult && (
        <div style={{ 
          marginTop: "40px",
          animation: "slideInUp 0.6s ease-out"
        }}>
          {/* Enhanced Header with Action Buttons */}
          <div style={{ 
            background: "linear-gradient(135deg, #1e293b 0%, #334155 100%)",
            padding: "30px",
            borderRadius: "20px 20px 0 0",
            color: "white",
            position: "relative",
            overflow: "hidden"
          }}>
            {/* Background pattern */}
            <div style={{
              position: "absolute",
              top: "0",
              left: "0",
              right: "0",
              bottom: "0",
              backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.03'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`,
              opacity: "0.5"
            }}></div>
            
            <div style={{ position: "relative", zIndex: "2" }}>
              <div style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                flexWrap: "wrap",
                gap: "20px"
              }}>
                <div style={{ flex: "1", minWidth: "250px" }}>
                  <div style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "12px",
                    marginBottom: "8px"
                  }}>
                    <div style={{
                      width: "48px",
                      height: "48px",
                      background: "linear-gradient(135deg, #22c55e 0%, #16a34a 100%)",
                      borderRadius: "12px",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      fontSize: "24px",
                      boxShadow: "0 4px 15px rgba(34, 197, 94, 0.4)"
                    }}>
                      📄
                    </div>
                    <div>
                      <h3 style={{ 
                        margin: "0", 
                        fontSize: "28px", 
                        fontWeight: "800",
                        color: "white",
                        textShadow: "0 2px 4px rgba(194, 189, 189, 0.3)"
                      }}>
                        Your Expert Blog Post
                      </h3>
                      <p style={{
                        margin: "0",
                        fontSize: "14px",
                        color: "white",
                        opacity: "0.8"
                      }}>
                        Professional content ready for publication
                      </p>
                    </div>
                  </div>
                </div>
                
                {/* Action Buttons */}
                <div style={{ 
                  display: "flex", 
                  gap: "10px", 
                  flexWrap: "wrap",
                  alignItems: "center"
                }}>
                  <button 
                    onClick={copyToClipboard}
                    style={{
                      padding: "12px 18px",
                      background: "rgba(255,255,255,0.1)",
                      color: "white",
                      border: "1px solid rgba(255,255,255,0.2)",
                      borderRadius: "10px",
                      cursor: "pointer",
                      fontSize: "14px",
                      fontWeight: "600",
                      backdropFilter: "blur(10px)",
                      transition: "all 0.3s ease",
                      display: "flex",
                      alignItems: "center",
                      gap: "6px"
                    }}
                    onMouseOver={(e) => {
                      e.target.style.background = "rgba(255,255,255,0.2)";
                      e.target.style.transform = "translateY(-2px)";
                    }}
                    onMouseOut={(e) => {
                      e.target.style.background = "rgba(255,255,255,0.1)";
                      e.target.style.transform = "translateY(0)";
                    }}
                  >
                    <span>📋</span> Copy Text
                  </button>
                  
                  <button 
                    onClick={downloadMarkdown}
                    style={{
                      padding: "12px 18px",
                      background: "rgba(59, 130, 246, 0.9)",
                      color: "white",
                      border: "1px solid rgba(255,255,255,0.2)",
                      borderRadius: "10px",
                      cursor: "pointer",
                      fontSize: "14px",
                      fontWeight: "600",
                      transition: "all 0.3s ease",
                      display: "flex",
                      alignItems: "center",
                      gap: "6px"
                    }}
                    onMouseOver={(e) => {
                      e.target.style.background = "rgba(59, 130, 246, 1)";
                      e.target.style.transform = "translateY(-2px)";
                    }}
                    onMouseOut={(e) => {
                      e.target.style.background = "rgba(59, 130, 246, 0.9)";
                      e.target.style.transform = "translateY(0)";
                    }}
                  >
                    <span>📄</span> Markdown
                  </button>
                  
                  <button 
                    onClick={downloadPDF}
                    style={{
                      padding: "12px 18px",
                      background: "linear-gradient(135deg, #dc2626 0%, #b91c1c 100%)",
                      color: "white",
                      border: "1px solid rgba(255,255,255,0.2)",
                      borderRadius: "10px",
                      cursor: "pointer",
                      fontSize: "14px",
                      fontWeight: "700",
                      boxShadow: "0 4px 15px rgba(220, 38, 38, 0.4)",
                      transition: "all 0.3s ease",
                      display: "flex",
                      alignItems: "center",
                      gap: "6px"
                    }}
                    onMouseOver={(e) => {
                      e.target.style.transform = "translateY(-2px)";
                      e.target.style.boxShadow = "0 6px 20px rgba(220, 38, 38, 0.5)";
                    }}
                    onMouseOut={(e) => {
                      e.target.style.transform = "translateY(0)";
                      e.target.style.boxShadow = "0 4px 15px rgba(220, 38, 38, 0.4)";
                    }}
                  >
                    <span>📑</span> Download PDF
                  </button>
                  
                  <button 
                    onClick={resetAll}
                    style={{
                      padding: "12px 18px",
                      background: "rgba(107, 114, 128, 0.9)",
                      color: "white",
                      border: "1px solid rgba(255,255,255,0.2)",
                      borderRadius: "10px",
                      cursor: "pointer",
                      fontSize: "14px",
                      fontWeight: "600",
                      transition: "all 0.3s ease",
                      display: "flex",
                      alignItems: "center",
                      gap: "6px"
                    }}
                    onMouseOver={(e) => {
                      e.target.style.background = "rgba(107, 114, 128, 1)";
                      e.target.style.transform = "translateY(-2px)";
                    }}
                    onMouseOut={(e) => {
                      e.target.style.background = "rgba(107, 114, 128, 0.9)";
                      e.target.style.transform = "translateY(0)";
                    }}
                  >
                    <span>✨</span> New Blog
                  </button>
                </div>
              </div>
            </div>
          </div>
          
          {/* Enhanced Blog Content Display */}
          <div 
            ref={blogContentRef}
            className="blog-card"
            style={{ 
              background: "white", 
              padding: "50px", 
              borderRadius: "0 0 20px 20px", 
              border: "1px solid #e2e8f0",
              boxShadow: "0 10px 40px rgba(0,0,0,0.1)",
              fontFamily: "'Georgia', serif",
              position: "relative",
              overflow: "hidden"
            }}
          >
            {/* Content quality indicator */}
            <div style={{
              position: "absolute",
              top: "20px",
              right: "20px",
              background: "linear-gradient(135deg, #22c55e 0%, #16a34a 100%)",
              color: "white",
              padding: "8px 16px",
              borderRadius: "20px",
              fontSize: "12px",
              fontWeight: "600",
              display: "flex",
              alignItems: "center",
              gap: "4px",
              boxShadow: "0 4px 15px rgba(34, 197, 94, 0.3)"
            }}>
              <span>✓</span> AI Generated
            </div>
            
            <div 
              style={{ 
                fontSize: "16px",
                lineHeight: "1.8",
                color: "#1f2937"
              }}
              dangerouslySetInnerHTML={{ 
                __html: formatBlogContent(blogResult.blogContent)
              }} 
            />
          </div>
          
          {/* Enhanced Summary and Keywords Section */}
          <div style={{ 
            marginTop: "30px", 
            display: "grid", 
            gridTemplateColumns: "1fr 1fr",
            gap: "25px"
          }}>
            <div className="blog-card" style={{ 
              background: "linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%)", 
              padding: "25px", 
              borderRadius: "16px",
              border: "1px solid #bae6fd",
              position: "relative",
              overflow: "hidden"
            }}>
              <div style={{
                position: "absolute",
                top: "0",
                left: "0",
                width: "100%",
                height: "4px",
                background: "linear-gradient(90deg, #0ea5e9 0%, #0284c7 100%)"
              }}></div>
              
              <div style={{ 
                display: "flex", 
                alignItems: "center", 
                gap: "10px", 
                marginBottom: "15px" 
              }}>
                <div style={{
                  width: "32px",
                  height: "32px",
                  background: "linear-gradient(135deg, #0ea5e9 0%, #0284c7 100%)",
                  borderRadius: "8px",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  fontSize: "16px",
                  color: "white"
                }}>
                  🔍
                </div>
                <h4 style={{ 
                  margin: "0", 
                  color: "#0c4a6e", 
                  fontSize: "18px", 
                  fontWeight: "700" 
                }}>
                  Summary
                </h4>
              </div>
              <p style={{ 
                margin: "0", 
                lineHeight: "1.6", 
                color: "#0c4a6e",
                fontSize: "15px"
              }}>
                {blogResult.summary}
              </p>
            </div>
            
            <div className="blog-card" style={{ 
              background: "linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%)", 
              padding: "25px", 
              borderRadius: "16px",
              border: "1px solid #bbf7d0",
              position: "relative",
              overflow: "hidden"
            }}>
              <div style={{
                position: "absolute",
                top: "0",
                left: "0",
                width: "100%",
                height: "4px",
                background: "linear-gradient(90deg, #22c55e 0%, #16a34a 100%)"
              }}></div>
              
              <div style={{ 
                display: "flex", 
                alignItems: "center", 
                gap: "10px", 
                marginBottom: "15px" 
              }}>
                <div style={{
                  width: "32px",
                  height: "32px",
                  background: "linear-gradient(135deg, #22c55e 0%, #16a34a 100%)",
                  borderRadius: "8px",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  fontSize: "16px",
                  color: "white"
                }}>
                  🏷
                </div>
                <h4 style={{ 
                  margin: "0", 
                  color: "#14532d", 
                  fontSize: "18px", 
                  fontWeight: "700" 
                }}>
                  Keywords
                </h4>
              </div>
              <div style={{ display: "flex", flexWrap: "wrap", gap: "8px" }}>
                {blogResult.keywords.map((keyword, idx) => (
                  <span 
                    key={idx}
                    style={{
                      background: "linear-gradient(135deg, #22c55e 0%, #16a34a 100%)",
                      color: "white",
                      padding: "6px 12px",
                      borderRadius: "16px",
                      fontSize: "13px",
                      fontWeight: "600",
                      boxShadow: "0 2px 8px rgba(34, 197, 94, 0.2)",
                      transition: "all 0.2s ease"
                    }}
                    onMouseOver={(e) => {
                      e.target.style.transform = "translateY(-1px)";
                      e.target.style.boxShadow = "0 4px 12px rgba(34, 197, 94, 0.3)";
                    }}
                    onMouseOut={(e) => {
                      e.target.style.transform = "translateY(0)";
                      e.target.style.boxShadow = "0 2px 8px rgba(34, 197, 94, 0.2)";
                    }}
                  >
                    {keyword}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}