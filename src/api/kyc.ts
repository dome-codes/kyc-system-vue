import axios from 'axios'
import type { KycQuestion, KycReport, CompanySearchResult } from '@/types/kyc'

// Mock API - später durch echte API ersetzen
const API_BASE_URL = 'http://localhost:3001/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
})

export const kycApi = {
  async createReport(entity: string, questions: KycQuestion[]): Promise<KycReport> {
    // Mock implementation - simuliert API-Aufruf
    return new Promise((resolve) => {
      setTimeout(() => {
        const mockAnswers: Record<string, string> = {}
        questions.forEach((question, index) => {
          mockAnswers[question.id] = `Mock-Antwort für: ${question.text}`
        })

        const mockReport: KycReport = {
          id: `report_${Date.now()}`,
          entity,
          answers: mockAnswers,
          status: 'pending_confirmation',
          timestamp: new Date().toISOString(),
          questions: questions,
          summary: {
            totalQuestions: questions.length,
            completedQuestions: questions.length,
            riskScore: Math.floor(Math.random() * 100),
            complianceScore: Math.floor(Math.random() * 100)
          }
        }
        resolve(mockReport)
      }, 2000) // 2 Sekunden Verzögerung für realistische UX
    })
  },

  async searchCompanies(query: string): Promise<CompanySearchResult[]> {
    // Mock implementation - später durch echte API ersetzen
    return new Promise((resolve) => {
      setTimeout(() => {
        const mockResults: CompanySearchResult[] = [
          {
            id: '1',
            name: `${query} GmbH`,
            address: 'Musterstraße 123, 12345 Musterstadt',
            industry: 'Technologie',
            country: 'Deutschland'
          },
          {
            id: '2',
            name: `${query} AG`,
            address: 'Beispielweg 456, 54321 Beispielstadt',
            industry: 'Finanzdienstleistungen',
            country: 'Deutschland'
          },
          {
            id: '3',
            name: `${query} UG`,
            address: 'Testplatz 789, 98765 Teststadt',
            industry: 'Beratung',
            country: 'Deutschland'
          }
        ]
        resolve(mockResults)
      }, 1000)
    })
  },

  async getReport(id: string): Promise<KycReport> {
    try {
      const response = await api.get(`/kyc/${id}`)
      return response.data
    } catch (error) {
      if (axios.isAxiosError(error)) {
        throw new Error(error.response?.data?.error || 'Bericht konnte nicht geladen werden')
      }
      throw error
    }
  },

  async getReports(): Promise<KycReport[]> {
    try {
      const response = await api.get('/kyc')
      return response.data
    } catch (error) {
      if (axios.isAxiosError(error)) {
        throw new Error(error.response?.data?.error || 'Berichte konnten nicht geladen werden')
      }
      throw error
    }
  }
}
