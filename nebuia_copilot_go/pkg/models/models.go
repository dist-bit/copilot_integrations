// File: pkg/models/models.go

package models

import (
	"time"
)

// BatchType represents the type of batch
type BatchType string

const (
	BatchTypeExecution BatchType = "execution"
	BatchTypeTesting   BatchType = "testing"
)

// StatusDocument represents the status of a document
type StatusDocument string

const (
	StatusWaitingProcess    StatusDocument = "waiting_process"
	StatusWorkingOCR        StatusDocument = "working_extractor"
	StatusProcessed         StatusDocument = "processed"
	StatusComplete          StatusDocument = "complete"
	StatusErrorLink         StatusDocument = "error_download_link"
	StatusErrorOCR          StatusDocument = "error_on_extraction"
	StatusAssigned          StatusDocument = "assigned"
	StatusWaitingQA         StatusDocument = "waiting_qa"
	StatusWorkingQA         StatusDocument = "working_qa"
	StatusQAComplete        StatusDocument = "complete_qa"
	StatusNoPipelineDefined StatusDocument = "no_pipeline_defined"
	StatusRejected          StatusDocument = "rejected"
	StatusInReview          StatusDocument = "in_review"
	StatusReviewed          StatusDocument = "reviewed"
	StatusWithErrorOnAssign StatusDocument = "with_error_on_assign"
)

// Response represents a generic API response
type Response struct {
	Payload interface{} `json:"payload"`
	Status  bool        `json:"status"`
}

// File represents a file that can be either a local file path, a URL, or binary data
type File struct {
	File         interface{} `json:"file"`
	TypeDocument string      `json:"type_document"`
	Filename     string      `json:"filename"`
}

// Search represents search parameters
type Search struct {
	Matches    string `json:"matches"`
	UUID       string `json:"uuid"`
	MaxResults int    `json:"max_results"`
}

// EntityTextExtractor represents parameters for text extraction
type EntityTextExtractor struct {
	Text   string      `json:"text"`
	Schema interface{} `json:"schema"` // Can be string or map[string]interface{}
}

// EntityDocumentExtractor represents parameters for document extraction
type EntityDocumentExtractor struct {
	Matches string      `json:"matches"`
	Schema  interface{} `json:"schema"` // Can be string or map[string]interface{}
}

// Job represents a job containing multiple files
type Job struct {
	Files []File `json:"files"`
}

// UploadResult represents the result of a file upload
type UploadResult struct {
	Success      bool   `json:"success"`
	Filename     string `json:"file_name"`
	UUID         string `json:"uuid,omitempty"`
	ErrorMessage string `json:"error_message,omitempty"`
}

// DocumentType represents a type of document
type DocumentType struct {
	ID             string `json:"id"`
	User           string `json:"user"`
	Key            string `json:"key"`
	IDTypeDocument string `json:"id_type_document"`
	Created        string `json:"created"`
}

// Entity represents an entity identified within a document
type Entity struct {
	ID      string `json:"id"`
	Key     string `json:"key"`
	Value   string `json:"value"`
	Page    int    `json:"page"`
	IDCore  string `json:"id_core"`
	IsValid bool   `json:"is_valid"`
}

// Document represents a document with its associated metadata and entities
type Document struct {
	ID             string    `json:"id"`
	BatchID        string    `json:"batch_id"`
	User           string    `json:"user"`
	UUID           string    `json:"uuid"`
	URL            string    `json:"url"`
	FileName       string    `json:"file_name"`
	TypeDocument   string    `json:"type_document"`
	StatusDocument string    `json:"status_document"`
	Uploaded       time.Time `json:"uploaded"`
	ReviewedAt     time.Time `json:"reviewed_at"`
	SourceType     string    `json:"source_type"`
	Entities       []Entity  `json:"entities,omitempty"`
}

// BatchDocumentsResponse represents a response containing a list of documents and their total count
type BatchDocumentsResponse struct {
	Documents []Document `json:"documents"`
	Total     int        `json:"total"`
}

// SearchParameters represents the parameters for a search operation
type SearchParameters struct {
	Batch      string `json:"batch"`
	Param      string `json:"param"`
	K          int    `json:"k"`
	TypeSearch string `json:"type_search"` // 'semantic' or 'literal'
}

// Result represents a result item from a search or query
type Result struct {
	UUID         string      `json:"uuid"`
	Content      string      `json:"content"`
	Name         string      `json:"name,omitempty"`
	Source       interface{} `json:"source"` // Can be int or string
	Coincidences int         `json:"coincidences"`
	Score        float64     `json:"score"`
}

// ResultsSearch represents a response containing a list of results
type ResultsSearch struct {
	Results []Result `json:"results"`
}

// Meta represents metadata for a search hit
type Meta struct {
	Name   string `json:"name"`
	Source int    `json:"source"`
}

// FormattedContent represents formatted content in a search hit
type FormattedContent struct {
	Content string `json:"content"`
}

// Formatted represents formatted data in a search hit
type Formatted struct {
	Content string `json:"content"`
	ID      string `json:"id"`
	Meta    Meta   `json:"meta"`
}

// Hit represents a single hit in a search result
type Hit struct {
	Formatted Formatted `json:"_formatted"`
	Content   string    `json:"content"`
	ID        int       `json:"id"`
	Meta      Meta      `json:"meta"`
}

// SearchDocument represents the result of a document search
type SearchDocument struct {
	Hits               []Hit  `json:"hits"`
	EstimatedTotalHits int    `json:"estimatedTotalHits"`
	Limit              int    `json:"limit"`
	ProcessingTimeMs   int    `json:"processingTimeMs"`
	Query              string `json:"query"`
}
