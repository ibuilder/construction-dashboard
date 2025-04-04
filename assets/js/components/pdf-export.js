// PDF export functionality
import { getProjectId } from '../app.js';

// Export data to PDF
function exportToPdf(data, columns, title, filename, isDetailView = false) {
  // Ensure jsPDF is available
  if (typeof jsPDF === 'undefined') {
    console.error('jsPDF is not loaded');
    alert('PDF export functionality is not available. Please try again later.');
    return;
  }
  
  try {
    // Create new PDF document
    const pdf = new jsPDF({
      orientation: 'portrait',
      unit: 'mm',
      format: 'a4'
    });
    
    // Add metadata
    pdf.setProperties({
      title: title,
      subject: 'Construction Project Management',
      author: 'Construction Dashboard',
      keywords: 'construction, project, management',
      creator: 'Construction Dashboard'
    });
    
    // Set up document
    const pageWidth = pdf.internal.pageSize.getWidth();
    const pageHeight = pdf.internal.pageSize.getHeight();
    const margin = 15;
    const contentWidth = pageWidth - (margin * 2);
    
    // Add header with logo and title
    addHeader(pdf, title, margin, contentWidth);
    
    // Add project info
    addProjectInfo(pdf, margin);
    
    // Add current date and time
    const dateText = `Generated on: ${new Date().toLocaleString()}`;
    pdf.setFontSize(9);
    pdf.setTextColor(100, 100, 100);
    pdf.text(dateText, pageWidth - margin - pdf.getTextWidth(dateText), 25);
    
    // Reset text properties
    pdf.setFontSize(10);
    pdf.setTextColor(0, 0, 0);
    
    // Position tracker
    let yPos = 45;
    
    // Add content based on view type
    if (isDetailView) {
      yPos = addDetailView(pdf, data[0], columns, margin, contentWidth, yPos);
    } else {
      yPos = addTableView(pdf, data, columns, margin, contentWidth, yPos);
    }
    
    // Add page number
    addPageNumbers(pdf);
    
    // Save PDF
    pdf.save(`${filename}.pdf`);
    
    return true;
  } catch (error) {
    console.error('Error generating PDF:', error);
    alert('An error occurred while generating the PDF. Please try again later.');
    return false;
  }
}

// Add header to PDF
function addHeader(pdf, title, margin, contentWidth) {
  // Add logo (placeholder)
  /*
  pdf.addImage(logoBase64, 'PNG', margin, 10, 30, 10);
  */
  
  // Add title
  pdf.setFontSize(16);
  pdf.setFont('helvetica', 'bold');
  pdf.text(title, margin, 20);
  
  // Add horizontal line
  pdf.setDrawColor(200, 200, 200);
  pdf.line(margin, 25, margin + contentWidth, 25);
}

// Add project info to PDF
function addProjectInfo(pdf, margin) {
  // Get project info from localStorage
  const projectId = getProjectId();
  const projectName = localStorage.getItem('projectName') || 'Project Name';
  const projectAddress = localStorage.getItem('projectAddress') || 'Project Address';
  const projectNumber = localStorage.getItem('projectNumber') || projectId.toString();
  
  // Add project details
  pdf.setFontSize(10);
  pdf.setTextColor(80, 80, 80);
  pdf.text(`Project: ${projectName}`, margin, 30);
  pdf.text(`Address: ${projectAddress}`, margin, 35);
  pdf.text(`Project #: ${projectNumber}`, margin, 40);
}

// Add page numbers to PDF
function addPageNumbers(pdf) {
  const pageCount = pdf.internal.getNumberOfPages();
  const pageWidth = pdf.internal.pageSize.getWidth();
  
  for (let i = 1; i <= pageCount; i++) {
    pdf.setPage(i);
    pdf.setFontSize(8);
    pdf.setTextColor(150, 150, 150);
    
    const text = `Page ${i} of ${pageCount}`;
    pdf.text(text, pageWidth - 25, pdf.internal.pageSize.getHeight() - 10);
  }
}

// Add table view to PDF
function addTableView(pdf, data, columns, margin, contentWidth, startY) {
  // Filter columns to only visible ones
  const visibleColumns = columns.filter(col => col.visible !== false);
  
  // Set up table configuration
  const colWidths = calculateColumnWidths(visibleColumns, contentWidth);
  const rowHeight = 10;
  let yPos = startY;
  
  // Add table header
  pdf.setFillColor(240, 240, 240);
  pdf.setDrawColor(200, 200, 200);
  pdf.rect(margin, yPos, contentWidth, rowHeight, 'F');
  
  pdf.setFont('helvetica', 'bold');
  pdf.setTextColor(60, 60, 60);
  pdf.setFontSize(9);
  
  let xPos = margin + 2;
  visibleColumns.forEach((column, index) => {
    const title = column.title || formatColumnName(column.data);
    pdf.text(title, xPos, yPos + 7);
    xPos += colWidths[index];
  });
  
  // Add table rows
  pdf.setFont('helvetica', 'normal');
  pdf.setTextColor(0, 0, 0);
  
  data.forEach((row, rowIndex) => {
    yPos += rowHeight;
    
    // Check if we need a new page
    if (yPos > pdf.internal.pageSize.getHeight() - 20) {
      pdf.addPage();
      yPos = margin + 10;
      
      // Repeat header on new page
      pdf.setFillColor(240, 240, 240);
      pdf.rect(margin, yPos, contentWidth, rowHeight, 'F');
      
      pdf.setFont('helvetica', 'bold');
      pdf.setTextColor(60, 60, 60);
      
      let headerX = margin + 2;
      visibleColumns.forEach((column, index) => {
        const title = column.title || formatColumnName(column.data);
        pdf.text(title, headerX, yPos + 7);
        headerX += colWidths[index];
      });
      
      pdf.setFont('helvetica', 'normal');
      pdf.setTextColor(0, 0, 0);
      
      yPos += rowHeight;
    }
    
    // Add row background (alternating)
    if (rowIndex % 2 === 1) {
      pdf.setFillColor(248, 248, 248);
      pdf.rect(margin, yPos, contentWidth, rowHeight, 'F');
    }
    
    // Add row data
    xPos = margin + 2;
    visibleColumns.forEach((column, index) => {
      let text = '';
      
      if (column.render && typeof column.render === 'function') {
        // Use custom renderer if available
        try {
          text = column.render(row[column.data], 'export', row);
          // Remove HTML
          text = text.replace(/<[^>]*>/g, '');
        } catch (error) {
          text = row[column.data] || '';
        }
      } else {
        text = row[column.data] || '';
      }
      
      // Convert to string and truncate if necessary
      text = String(text);
      const maxWidth = colWidths[index] - 4;
      text = truncateText(pdf, text, maxWidth);
      
      pdf.text(text, xPos, yPos + 7);
      xPos += colWidths[index];
    });
    
    // Add row border
    pdf.setDrawColor(240, 240, 240);
    pdf.line(margin, yPos + rowHeight, margin + contentWidth, yPos + rowHeight);
  });
  
  return yPos + rowHeight + 10;
}

// Add detail view to PDF
function addDetailView(pdf, data, columns, margin, contentWidth, startY) {
  let yPos = startY;
  
  // Add section for general info
  pdf.setFillColor(240, 240, 240);
  pdf.setDrawColor(200, 200, 200);
  pdf.rect(margin, yPos, contentWidth, 10, 'F');
  
  pdf.setFont('helvetica', 'bold');
  pdf.setTextColor(60, 60, 60);
  pdf.setFontSize(11);
  pdf.text('General Information', margin + 5, yPos + 7);
  
  yPos += 15;
  
  // Add data fields
  pdf.setFont('helvetica', 'normal');
  pdf.setTextColor(0, 0, 0);
  pdf.setFontSize(10);
  
  // Determine fields to show based on visible columns
  const fieldsToShow = columns
    .filter(col => col.visible !== false)
    .map(col => ({
      label: col.title || formatColumnName(col.data),
      key: col.data
    }));
  
  // Add fields in two columns if there are many
  if (fieldsToShow.length > 6) {
    const leftFields = fieldsToShow.slice(0, Math.ceil(fieldsToShow.length / 2));
    const rightFields = fieldsToShow.slice(Math.ceil(fieldsToShow.length / 2));
    
    const leftColWidth = contentWidth / 2 - 10;
    const rightColStart = margin + contentWidth / 2;
    
    let leftYPos = yPos;
    let rightYPos = yPos;
    
    // Left column
    leftFields.forEach(field => {
      // Label
      pdf.setFont('helvetica', 'bold');
      pdf.text(`${field.label}:`, margin, leftYPos);
      
      // Value
      pdf.setFont('helvetica', 'normal');
      let value = data[field.key] || 'N/A';
      value = String(value);
      
      // Handle long text
      if (pdf.getTextWidth(value) > leftColWidth) {
        const lines = pdf.splitTextToSize(value, leftColWidth);
        pdf.text(lines, margin, leftYPos + 5);
        leftYPos += 5 + (lines.length * 5);
      } else {
        pdf.text(value, margin, leftYPos + 5);
        leftYPos += 10;
      }
    });
    
    // Right column
    rightFields.forEach(field => {
      // Label
      pdf.setFont('helvetica', 'bold');
      pdf.text(`${field.label}:`, rightColStart, rightYPos);
      
      // Value
      pdf.setFont('helvetica', 'normal');
      let value = data[field.key] || 'N/A';
      value = String(value);
      
      // Handle long text
      if (pdf.getTextWidth(value) > leftColWidth) {
        const lines = pdf.splitTextToSize(value, leftColWidth);
        pdf.text(lines, rightColStart, rightYPos + 5);
        rightYPos += 5 + (lines.length * 5);
      } else {
        pdf.text(value, rightColStart, rightYPos + 5);
        rightYPos += 10;
      }
    });
    
    yPos = Math.max(leftYPos, rightYPos) + 5;
  } else {
    // Simple single column layout
    fieldsToShow.forEach(field => {
      // Check if we need a new page
      if (yPos > pdf.internal.pageSize.getHeight() - 30) {
        pdf.addPage();
        yPos = margin + 10;
      }
      
      // Label
      pdf.setFont('helvetica', 'bold');
      pdf.text(`${field.label}:`, margin, yPos);
      
      // Value
      pdf.setFont('helvetica', 'normal');
      let value = data[field.key] || 'N/A';
      value = String(value);
      
      // Handle long text
      if (pdf.getTextWidth(value) > contentWidth - 20) {
        const lines = pdf.splitTextToSize(value, contentWidth - 20);
        pdf.text(lines, margin + 20, yPos);
        yPos += lines.length * 5;
      } else {
        pdf.text(value, margin + 80, yPos);
      }
      
      yPos += 8;
    });
  }
  
  // Add space
  yPos += 10;
  
  // If there are comments, add them
  if (data.comments && data.comments.length > 0) {
    // Check if we need a new page
    if (yPos > pdf.internal.pageSize.getHeight() - 50) {
      pdf.addPage();
      yPos = margin + 10;
    }
    
    // Add comments section
    pdf.setFillColor(240, 240, 240);
    pdf.setDrawColor(200, 200, 200);
    pdf.rect(margin, yPos, contentWidth, 10, 'F');
    
    pdf.setFont('helvetica', 'bold');
    pdf.setTextColor(60, 60, 60);
    pdf.setFontSize(11);
    pdf.text('Comments', margin + 5, yPos + 7);
    
    yPos += 15;
    
    // Add comments
    pdf.setFont('helvetica', 'normal');
    pdf.setTextColor(0, 0, 0);
    pdf.setFontSize(9);
    
    data.comments.forEach(comment => {
      // Check if we need a new page
      if (yPos > pdf.internal.pageSize.getHeight() - 30) {
        pdf.addPage();
        yPos = margin + 10;
      }
      
      // Comment author and date
      pdf.setFont('helvetica', 'bold');
      const headerText = `${comment.user_name} on ${new Date(comment.created_at).toLocaleString()}:`;
      pdf.text(headerText, margin, yPos);
      
      yPos += 5;
      
      // Comment content
      pdf.setFont('helvetica', 'normal');
      const commentLines = pdf.splitTextToSize(comment.content, contentWidth - 10);
      pdf.text(commentLines, margin, yPos);
      
      yPos += commentLines.length * 5 + 5;
    });
  }
  
  return yPos;
}

// Helper function to calculate column widths
function calculateColumnWidths(columns, totalWidth) {
  // Calculate total weight based on column definitions
  let totalWeight = 0;
  columns.forEach(column => {
    // Use specified width or default to weight 1
    totalWeight += column.pdfWidth || 1;
  });
  
  // Calculate width per weight unit
  const widthPerUnit = totalWidth / totalWeight;
  
  // Calculate width for each column
  return columns.map(column => {
    return (column.pdfWidth || 1) * widthPerUnit;
  });
}

// Helper function to format column name
function formatColumnName(name) {
  return name
    .replace(/_/g, ' ')
    .replace(/\b\w/g, char => char.toUpperCase());
}

// Helper function to truncate text if it's too long
function truncateText(pdf, text, maxWidth) {
  if (pdf.getTextWidth(text) <= maxWidth) {
    return text;
  }
  
  // Truncate character by character
  let truncated = text;
  while (pdf.getTextWidth(truncated + '...') > maxWidth && truncated.length > 0) {
    truncated = truncated.slice(0, -1);
  }
  
  return truncated + '...';
}

// Export functions
export {
  exportToPdf
};