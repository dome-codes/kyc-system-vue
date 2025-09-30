import type { CompanySearchResult, KycQuestion, KycReport } from '@/types/kyc'
import axios from 'axios'

// Mock API - später durch echte API ersetzen
const API_BASE_URL = 'http://localhost:3001/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
})

export const kycApi = {
  async createReport(entity: string, questions: KycQuestion[]): Promise<KycReport> {
    return new Promise((resolve) => {
      setTimeout(() => {
        const mockAnswers: Record<string, string> = {}
        const mockSources: Record<string, string> = {}
        questions.forEach((question) => {
          mockAnswers[question.id] = `Mock-Antwort für: ${question.text}`
          mockSources[question.id] = `Handelsregister`
          mockSources[question.id + '_link'] = `https://handelsregister.de/example/${question.id}`
        })

        const mockReport: KycReport = {
          id: `report_${Date.now()}`,
          entity,
          answers: mockAnswers,
          sources: mockSources,
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
      }, 2000)
    })
  },

  async searchCompanies(query: string): Promise<CompanySearchResult[]> {
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
