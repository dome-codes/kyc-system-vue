import type { KycReport } from '@/types/kyc'
import jsPDF from 'jspdf'

export const generateKycReportPDF = (report: KycReport): void => {
  const doc = new jsPDF()

  // Colors
  const primaryColor = '#1E3B64'
  const secondaryColor = '#6B7280'

  let yPosition = 20

  // Helper function to add text with word wrap
  const addText = (text: string, x: number, y: number, maxWidth: number, fontSize: number = 10, color: string = '#000000') => {
    doc.setFontSize(fontSize)
    doc.setTextColor(color)
    const lines = doc.splitTextToSize(text, maxWidth)
    doc.text(lines, x, y)
    return y + (lines.length * fontSize * 0.4) + 5
  }

  // Helper function to add a section header
  const addSectionHeader = (title: string, y: number) => {
    doc.setFontSize(14)
    doc.setTextColor(primaryColor)
    doc.setFont('helvetica', 'bold')
    doc.text(title, 20, y)
    doc.setFont('helvetica', 'normal')
    return y + 15
  }

  // Helper function to add a line
  const addLine = (y: number) => {
    doc.setDrawColor(200, 200, 200)
    doc.line(20, y, 190, y)
    return y + 10
  }

  // Header
  doc.setFillColor(30, 59, 100)
  doc.rect(0, 0, 210, 30, 'F')

  doc.setFontSize(20)
  doc.setTextColor(255, 255, 255)
  doc.setFont('helvetica', 'bold')
  doc.text('Mieter Recherche Bericht', 20, 20)

  yPosition = 50

  // Company Information
  yPosition = addSectionHeader('Unternehmensinformationen', yPosition)
  yPosition = addText(`Unternehmen: ${report.entity}`, 20, yPosition, 170)
  yPosition = addText(`Erstellt am: ${report.timestamp ? new Date(report.timestamp).toLocaleString('de-DE') : 'Unbekannt'}`, 20, yPosition, 170)
  yPosition = addText(`Status: ${report.status === 'confirmed' ? 'Bestätigt' : 'Ausstehend'}`, 20, yPosition, 170)
  if (report.id) {
    yPosition = addText(`Bericht-ID: ${report.id}`, 20, yPosition, 170)
  }
  yPosition = addLine(yPosition)

  // Summary
  if (report.summary) {
    yPosition = addSectionHeader('Zusammenfassung', yPosition)
    yPosition = addText(`Gesamtfragen: ${report.summary.totalQuestions}`, 20, yPosition, 170)
    yPosition = addText(`Beantwortet: ${report.summary.completedQuestions}`, 20, yPosition, 170)
    yPosition = addLine(yPosition)
  }

  // Questions and Answers
  yPosition = addSectionHeader('Fragen & Antworten', yPosition)

  let questionNumber = 1
  for (const [questionId, answer] of Object.entries(report.answers)) {
    // Check if we need a new page
    if (yPosition > 250) {
      doc.addPage()
      yPosition = 20
    }

    const questionText = report.questions?.find(q => q.schemaQuestionId === questionId || q.id === questionId)?.text || `Frage ${questionNumber}`

    // Extract source from answer object if available or fallback to sources mapping
    let source = '';
    let sourceLink = '';

    if (answer && typeof answer === 'object' && answer.quelle) {
      // Backend provides source in answer object
      source = answer.quelle;
    } else {
    // Fallback to original sources mapping
      source = report.sources?.[questionId] || '';
      sourceLink = report.sources?.[questionId + '_link'] || '';
    }

    // Question number and text
    yPosition = addText(`${questionNumber}. ${questionText}`, 20, yPosition, 170, 11, primaryColor)

    // Answer - Handle different answer types properly
    let answerText = '';
    if (typeof answer === 'string') {
      answerText = answer;
    } else if (answer && typeof answer === 'object') {
      // Handle answer object from backend - extract main answer text and clean up LLM formatting
      answerText = answer.answer || answer.text || String(answer);

      // Clean up LLM formatting for better PDF display
      if (answerText.includes('🤖 **KI-Analyse')) {
        // Replace emoji-formatted text with clean format
        answerText = answerText.replace(/📊 /g, 'INFORMATION: ').replace(/🤖 \*\*KI-Analyse.*?\*\*:/g, 'AI-Analyse:').replace(/📈 Vertrauen: /g, '\nVertrauen: ');
      }
    } else {
      answerText = String(answer || 'Keine Antwort verfügbar');
    }
    yPosition = addText(`Antwort: ${answerText}`, 30, yPosition, 160, 10)

    // Source information
    if (source) {
      yPosition = addText(`Quelle: ${source}`, 30, yPosition, 160, 9, secondaryColor)
    }
    if (sourceLink) {
      yPosition = addText(`Link: ${sourceLink}`, 30, yPosition, 160, 9, secondaryColor)
    }

    yPosition += 10
    questionNumber++
  }

  // Footer
  const pageCount = doc.getNumberOfPages()
  for (let i = 1; i <= pageCount; i++) {
    doc.setPage(i)
    doc.setFontSize(8)
    doc.setTextColor(secondaryColor)
    doc.text(`Seite ${i} von ${pageCount}`, 20, 290)
    doc.text(`Erstellt am ${new Date().toLocaleString('de-DE')}`, 150, 290)
  }

  // Save the PDF
  const fileName = `mieter-recherche-${report.entity.replace(/[^a-zA-Z0-9]/g, '-')}-${new Date().toISOString().split('T')[0]}.pdf`
  doc.save(fileName)
}
