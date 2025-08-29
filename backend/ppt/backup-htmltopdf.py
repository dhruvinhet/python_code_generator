from weasyprint import HTML, CSS
from weasyprint.formatting_structure import boxes

# Hardcoded paths
INPUT_HTML = "/home/sanvict/Documents/ppt_generator/backend/temp/html_outputs/20250827_005000_slide1.html"
OUTPUT_PDF = "backend/temp/asdf.pdf"

# 16:9 aspect ratio PowerPoint dimensions
css = CSS(string='''
    @page {
        size: 1920px 1080px;
        margin: 0;
        padding: 0;
    }
    
    @font-face {
        font-family: 'Arial';
        font-weight: normal;
        font-style: normal;
    }
    
    body {
        margin: 0;
        padding: 0;
        width: 1920px;
        height: 1080px;
        position: relative;
        overflow: hidden;
        font-family: Arial, sans-serif;
    }
    
    .slide {
        width: 100%;
        height: 100%;
        position: relative;
        box-sizing: border-box;
        padding: 60px;
    }
    
    .slide-content {
        width: 100%;
        height: 100%;
        position: relative;
        display: flex;
        flex-direction: column;
    }
    
    .slide-title {
        font-size: 60px;
        line-height: 1.2;
        margin-bottom: 40px;
        flex-shrink: 0;
    }
    
    .slide-body {
        flex-grow: 1;
        overflow: hidden;
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
    }
    
    .bullet-points {
        font-size: 36px;
        line-height: 1.4;
        margin: 0;
        padding-left: 40px;
    }
    
    .bullet-points li {
        margin-bottom: 20px;
    }
    
    .paragraph {
        font-size: 32px;
        line-height: 1.5;
        margin: 0;
    }
    
    .two-column {
        display: flex;
        justify-content: space-between;
        gap: 40px;
    }
    
    .column {
        flex: 1;
        display: flex;
        flex-direction: column;
    }
    
    .numbered-list {
        font-size: 36px;
        line-height: 1.4;
        margin: 0;
        padding-left: 40px;
    }
    
    .numbered-list li {
        margin-bottom: 20px;
    }
    
    .quote {
        font-size: 42px;
        line-height: 1.4;
        font-style: italic;
        text-align: center;
        margin: 40px 0;
    }
    
    .source-citation {
        font-size: 24px;
        color: #666;
        margin-top: 20px;
    }
    
    /* Auto-scaling for content overflow */
    @media print {
        .slide-body {
            transform-origin: top left;
            transform: scale(var(--scale, 1));
        }
    }
''')

try:
    HTML(filename=INPUT_HTML).write_pdf(OUTPUT_PDF, stylesheets=[css])
    print(f"PDF created at: {OUTPUT_PDF}")
except Exception as e:
    print(f"Error while converting: {e}")