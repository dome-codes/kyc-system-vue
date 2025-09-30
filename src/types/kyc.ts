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
