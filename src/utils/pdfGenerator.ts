import type { KycReport } from '@/types/kyc'
import jsPDF from 'jspdf'

export const generateKycReportPDF = (report: KycReport): void => {
  const doc = new jsPDF()

  // Colors
  const primaryColor = '#1E3B64'
  const secondaryColor = '#6B7280'
  const successColor = '#10B981'
  const warningColor = '#F59E0B'
  const dangerColor = '#EF4444'

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
  doc.text('KYC Compliance Bericht', 20, 20)

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
    yPosition = addText(`Risiko-Score: ${report.summary.riskScore}%`, 20, yPosition, 170, 10, getRiskColor(report.summary.riskScore))
    yPosition = addText(`Compliance-Score: ${report.summary.complianceScore}%`, 20, yPosition, 170, 10, getComplianceColor(report.summary.complianceScore))
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

    const questionText = report.questions?.find(q => q.id === questionId)?.text || questionId
    const riskLevel = getRiskLevel(answer)

    // Question number and text
    yPosition = addText(`${questionNumber}. ${questionText}`, 20, yPosition, 170, 11, primaryColor)

    // Answer with risk indicator
    const riskColor = getRiskColorFromLevel(riskLevel)
    yPosition = addText(`Antwort: ${answer}`, 30, yPosition, 160, 10)
    yPosition = addText(`Risiko: ${getRiskLabel(riskLevel)}`, 30, yPosition, 160, 9, riskColor)

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
  const fileName = `kyc-report-${report.entity.replace(/[^a-zA-Z0-9]/g, '-')}-${new Date().toISOString().split('T')[0]}.pdf`
  doc.save(fileName)
}

const getRiskLevel = (answer: string): 'low' | 'medium' | 'high' => {
  const lowerAnswer = answer.toLowerCase()
  if (lowerAnswer.includes('nicht') || lowerAnswer.includes('keine') || lowerAnswer.includes('unbekannt')) {
    return 'high'
  }
  if (lowerAnswer.includes('teilweise') || lowerAnswer.includes('begrenzt')) {
    return 'medium'
  }
  return 'low'
}

const getRiskLabel = (level: 'low' | 'medium' | 'high'): string => {
  switch (level) {
    case 'low':
      return 'Niedrig'
    case 'medium':
      return 'Mittel'
    case 'high':
      return 'Hoch'
  }
}

const getRiskColor = (score: number): string => {
  if (score >= 80) return '#EF4444'
  if (score >= 60) return '#F59E0B'
  if (score >= 40) return '#F59E0B'
  return '#10B981'
}

const getComplianceColor = (score: number): string => {
  if (score >= 80) return '#10B981'
  if (score >= 60) return '#F59E0B'
  if (score >= 40) return '#F59E0B'
  return '#EF4444'
}

const getRiskColorFromLevel = (level: 'low' | 'medium' | 'high'): string => {
  switch (level) {
    case 'low':
      return '#10B981'
    case 'medium':
      return '#F59E0B'
    case 'high':
      return '#EF4444'
  }
}

