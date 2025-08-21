import { useState, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import { Box, Paper, Typography, Button, Stack, Chip, Divider } from '@mui/material';
import { saveAs } from 'file-saver';
import jsPDF from 'jspdf';
import ContentCopyIcon from '@mui/icons-material/ContentCopy';
import CheckCircleOutlineIcon from '@mui/icons-material/CheckCircleOutline';

export default function BlogOutput({ data }) {
  const [copied, setCopied] = useState(false);
  const pdfContentRef = useRef(null);

  const { blogContent = '', summary = '', keywords = [] } = data || {};

  const handleDownloadMarkdown = () => {
    const blob = new Blob([blogContent], { type: 'text/markdown;charset=utf-8' });
    saveAs(blob, 'blog-post.md');
  };

  const handleDownloadPdf = () => {
    const content = pdfContentRef.current;
    if (!content) return;

    const doc = new jsPDF({
      orientation: 'p',
      unit: 'pt',
      format: 'a4'
    });

    const pdfStyles = `
      #pdf-export-container {
        background-color: white !important;
        font-family: 'Georgia', serif !important;
      }
      #pdf-export-container h1 { font-size: 26pt !important; text-align: center !important; margin-bottom: 20pt; font-weight: bold; }
      #pdf-export-container h2 { font-size: 20pt !important; margin-top: 18pt; margin-bottom: 12pt; font-weight: bold; }
      #pdf-export-container h3 { font-size: 16pt !important; margin-top: 14pt; margin-bottom: 10pt; font-weight: bold; }
      #pdf-export-container p, #pdf-export-container li { font-size: 12pt !important; line-height: 1.6 !important; margin-bottom: 10pt; }
    `;

    const styleTag = document.createElement('style');
    styleTag.innerHTML = pdfStyles;
    document.head.appendChild(styleTag);

    content.id = 'pdf-export-container';

    doc.html(content, {
      callback: function (doc) {
        document.head.removeChild(styleTag);
        content.removeAttribute('id');
        doc.save('blog-post.pdf');
      },
      margin: [40, 40, 40, 40],
      autoPaging: 'text',
      width: 515,
      windowWidth: 1000,
    });
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(blogContent).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  };

  if (!data) {
    return (
      <Paper elevation={0} sx={{ p: 4, height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', bgcolor: 'transparent', border: '2px dashed', borderColor: 'divider' }}>
        <Typography variant="h6" color="text.secondary">Your generated blog will appear here...</Typography>
      </Paper>
    );
  }

  return (
    <Paper elevation={3} sx={{ p: 4, height: '100%', display: 'flex', flexDirection: 'column', position: 'relative' }}>
      <Box sx={{ position: 'absolute', top: 16, right: 16 }}>
        <Button
          variant="text"
          startIcon={copied ? <CheckCircleOutlineIcon /> : <ContentCopyIcon />}
          onClick={handleCopy}
          color={copied ? 'success' : 'primary'}
          sx={{ transition: 'all 0.3s ease' }}
        >
          {copied ? 'Copied!' : 'Copy'}
        </Button>
      </Box>

      <Box sx={{ mb: 3, flexShrink: 0 }}>
        <Typography variant="h6" component="h2" gutterBottom>Summary</Typography>
        <Typography variant="body2" color="text.secondary" sx={{ fontStyle: 'italic' }}>{summary}</Typography>

        <Box sx={{ mt: 2, display: 'flex', flexWrap: 'wrap', gap: 1 }}>
          {keywords.map((keyword) => (
            <Chip key={keyword} label={keyword} variant="outlined" size="small" />
          ))}
        </Box>
      </Box>

      <Divider sx={{ my: 2 }} />

      <Box ref={pdfContentRef} className="markdown-content" sx={{ flexGrow: 1, overflowY: 'auto', pr: 2 }}>
        <ReactMarkdown
          components={{
            h1: ({node, ...props}) => (
              <Typography variant="h3" gutterBottom sx={{ fontWeight: 'bold', textAlign: 'center', mb: 3 }} {...props} />
            ),
            h2: ({node, ...props}) => (
              <Typography variant="h4" gutterBottom sx={{ fontWeight: 'bold', mt: 4, mb: 2 }} {...props} />
            ),
            h3: ({node, ...props}) => (
              <Typography variant="h5" gutterBottom sx={{ fontWeight: 'medium', mt: 3, mb: 1 }} {...props} />
            ),
            p: ({node, ...props}) => <Typography paragraph sx={{ mb: 2 }} {...props} />,
            li: ({node, ...props}) => <li style={{ marginBottom: '8px' }}><Typography component="span" {...props} /></li>,
          }}
        >
          {blogContent}
        </ReactMarkdown>
      </Box>

      <Stack direction="row" spacing={2} sx={{ mt: 4, flexShrink: 0 }}>
        <Button variant="outlined" onClick={handleDownloadMarkdown}>
          Download .MD
        </Button>
        <Button variant="outlined" onClick={handleDownloadPdf}>
          Download .PDF
        </Button>
      </Stack>
    </Paper>
  );
}