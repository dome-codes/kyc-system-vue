export interface KycQuestion {
  id: string
  text: string
  source?: string
}

export interface KycReport {
  id?: string
  entity: string
  answers: Record<string, string>
  sources: Record<string, string>
  status: "pending_confirmation" | "confirmed"
  timestamp?: string
  questions?: KycQuestion[]
  summary?: {
    totalQuestions: number
    completedQuestions: number
    riskScore: number
    complianceScore: number
  }
}

// Backend API Types
export interface ResearchRequest {
  mieter: string
  fragen: string[]
  land?: string
  branche?: string
}

export interface TenantSuggestion {
  id: string
  name: string
  land?: string
  branche?: string
}

export interface VerifyOk {
  mieter: string
}

export interface VerifyAmbiguous {
  mieter_eingabe: string
  vorschlaege: TenantSuggestion[]
}

export interface Antwort {
  frage_id: string
  frage_text: string
  antwort: string
  quelle: string
  quelle_link: string
  kategorie: string
}

export interface ResearchSuccess {
  mieter: string
  branche?: string
  land?: string
  antworten: Antwort[]
}

export interface CompanySearchResult {
  id: string
  name: string
  address: string
  industry: string
  country: string
}

export interface QuestionnaireData {
  standardQuestions: KycQuestion[]
  groups: QuestionGroup[]
  answers: Record<string, any>
}

export interface QuestionGroup {
  id: string
  title: string
  description: string
  questions: KycQuestion[]
  isVisible: boolean
}
