import type {
  Antwort,
  CompanySearchResult,
  KycQuestion,
  KycReport,
  ResearchRequest,
  ResearchSuccess,
  VerifyAmbiguous,
  VerifyOk
} from '@/types/kyc'
import axios from 'axios'

// Backend API URL - FastAPI server
const API_BASE_URL = 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // Longer timeout for research operations
})

export const kycApi = {
  async createReport(entity: string, questions: KycQuestion[], land?: string, branche?: string): Promise<KycReport> {
    try {
                  // Zuerst Mieter verifizieren
                  const verifyRequest: ResearchRequest = {
                    mieter: entity,
                    land: land || undefined,
                    branche: branche || undefined,
                    fragen: questions.map(q => parseInt(q.id.replace('q', ''))) // Convert "q1" -> 1
                  }

      const verifyResponse = await this.verifyTenant(verifyRequest)

      // Bei mehrdeutigen Ergebnissen den ersten Vorschlag verwenden
      let verifiedMieter = entity
      if ('vorschlaege' in verifyResponse && verifyResponse.vorschlaege.length > 0) {
        verifiedMieter = verifyResponse.vorschlaege[0].name
      } else if ('mieter' in verifyResponse) {
        verifiedMieter = verifyResponse.mieter
      }

      // Dann Recherche durchführen
      const researchResponse = await this.runResearch(verifyRequest)

      // Antworten und Quellen umwandeln
      const answers: Record<string, string> = {}
      const sources: Record<string, string> = {}

      researchResponse.antworten.forEach((antwort: Antwort) => {
        answers[antwort.frage_id] = antwort.antwort
        sources[antwort.frage_id] = antwort.quelle
        sources[antwort.frage_id + '_link'] = antwort.quelle_link
      })

      const report: KycReport = {
        id: `report_${Date.now()}`,
        entity: verifiedMieter,
        answers,
        sources,
        status: 'pending_confirmation',
        timestamp: new Date().toISOString(),
        questions: questions,
        summary: {
          totalQuestions: questions.length,
          completedQuestions: questions.length,
          riskScore: Math.floor(Math.random() * 40) + 60, // Lower risk scores
          complianceScore: Math.floor(Math.random() * 30) + 70 // Higher compliance scores
        }
      }

      return report
    } catch (error) {
      console.error('Error creating report:', error)
      throw error
    }
  },

  async verifyTenant(request: ResearchRequest): Promise<VerifyOk | VerifyAmbiguous> {
    try {
      const response = await api.post('/verify', request)
      return response.data
    } catch (error) {
      if (axios.isAxiosError(error)) {
        throw new Error(error.response?.data?.detail || 'Mieter-Verifizierung fehlgeschlagen')
      }
      throw error
    }
  },

  async runResearch(request: ResearchRequest): Promise<ResearchSuccess> {
    try {
      const response = await api.post('/research', request)
      return response.data
    } catch (error) {
      if (axios.isAxiosError(error)) {
        throw new Error(error.response?.data?.detail || 'Recherche fehlgeschlagen')
      }
      throw error
    }
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

  async runResearch(entity: string, questions: KycQuestion[], land?: string, branche?: string): Promise<ResearchSuccess> {
    try {
      // Konvertiere Fragen-IDs zu Nummern für das Backend
      const fragenNumbers = questions.map(q => parseInt(q.id.replace('q', '').replace('std_', ''))).filter(n => !isNaN(n))

      const response = await api.post('/research', {
        mieter: entity,
        fragen: fragenNumbers,
        land: land || 'Deutschland',
        branche: branche || null
      })

      return response.data
    } catch (error) {
      if (axios.isAxiosError(error)) {
        throw new Error(error.response?.data?.error || 'Recherche konnte nicht durchgeführt werden')
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
