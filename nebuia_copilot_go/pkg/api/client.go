// File: pkg/api/client.go

package api

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"mime/multipart"
	"nebuia_copilot/pkg/models"
	"net/http"
	"time"
)

// APIClient represents the client for interacting with the API
type APIClient struct {
	Key     string
	Secret  string
	BaseURL string
	Client  *http.Client
}

// NewAPIClient creates a new instance of APIClient
func NewAPIClient(key, secret, baseURL string) *APIClient {
	return &APIClient{
		Key:     key,
		Secret:  secret,
		BaseURL: baseURL,
		Client:  &http.Client{},
	}
}

// ExtractorFromText extracts information from text using an external API
func (c *APIClient) ExtractorFromText(data *models.EntityTextExtractor) (map[string]interface{}, error) {
	url := fmt.Sprintf("%s/integrator/extractor/from/text", c.BaseURL)
	payload, err := json.Marshal(data)
	if err != nil {
		return nil, err
	}

	resp, err := c.sendRequest("POST", url, bytes.NewBuffer(payload))
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	var result map[string]interface{}
	err = json.NewDecoder(resp.Body).Decode(&result)
	if err != nil {
		return nil, err
	}

	return result["payload"].(map[string]interface{}), nil
}

// ExtractorFromDocumentUUID extracts information from a document identified by UUID
func (c *APIClient) ExtractorFromDocumentUUID(uuid string, data *models.EntityDocumentExtractor) (map[string]interface{}, error) {
	url := fmt.Sprintf("%s/integrator/extractor/from/document/%s", c.BaseURL, uuid)
	payload, err := json.Marshal(data)
	if err != nil {
		return nil, err
	}

	resp, err := c.sendRequest("POST", url, bytes.NewBuffer(payload))
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	var result map[string]interface{}
	err = json.NewDecoder(resp.Body).Decode(&result)
	if err != nil {
		return nil, err
	}

	return result["payload"].(map[string]interface{}), nil
}

// SearchInDocument performs a document search using the provided search parameters
func (c *APIClient) SearchInDocument(search *models.Search) (*models.SearchDocument, error) {
	url := fmt.Sprintf("%s/integrator/document/search", c.BaseURL)
	payload, err := json.Marshal(search)
	if err != nil {
		return nil, err
	}

	resp, err := c.sendRequest("POST", url, bytes.NewBuffer(payload))
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	var result struct {
		Payload models.SearchDocument `json:"payload"`
	}
	err = json.NewDecoder(resp.Body).Decode(&result)
	if err != nil {
		return nil, err
	}

	return &result.Payload, nil
}

// SetDocumentStatus sets the status of a document identified by its UUID
func (c *APIClient) SetDocumentStatus(uuid string, status models.StatusDocument) (bool, error) {
	url := fmt.Sprintf("%s/integrator/documents/set/status/%s/%s", c.BaseURL, uuid, status)

	resp, err := c.sendRequest("GET", url, nil)
	if err != nil {
		return false, err
	}
	defer resp.Body.Close()

	var result struct {
		Status bool `json:"status"`
	}
	err = json.NewDecoder(resp.Body).Decode(&result)
	if err != nil {
		return false, err
	}

	return result.Status, nil
}

// GetDocumentByUUID retrieves a document by its UUID
func (c *APIClient) GetDocumentByUUID(uuid string) (*models.Document, error) {
	url := fmt.Sprintf("%s/integrator/document/get/by/uuid/%s", c.BaseURL, uuid)

	resp, err := c.sendRequest("GET", url, nil)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	var result struct {
		Payload models.Document `json:"payload"`
	}
	err = json.NewDecoder(resp.Body).Decode(&result)
	if err != nil {
		return nil, err
	}

	return &result.Payload, nil
}

// GetDocumentsByStatus fetches a batch of documents based on their status
func (c *APIClient) GetDocumentsByStatus(status models.StatusDocument, page, limit int) (*models.BatchDocumentsResponse, error) {
	url := fmt.Sprintf("%s/integrator/documents/by/status/%s?page=%d&limit=%d", c.BaseURL, status, page, limit)

	resp, err := c.sendRequest("GET", url, nil)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	var result struct {
		Payload models.BatchDocumentsResponse `json:"payload"`
	}
	err = json.NewDecoder(resp.Body).Decode(&result)
	if err != nil {
		return nil, err
	}

	return &result.Payload, nil
}

// GetDocumentsByStatusAndBatch fetches a batch of documents based on their status and batch type
func (c *APIClient) GetDocumentsByStatusAndBatch(status models.StatusDocument, batchType models.BatchType, page, limit int) (*models.BatchDocumentsResponse, error) {
	url := fmt.Sprintf("%s/integrator/documents/by/%s/status/%s?page=%d&limit=%d", c.BaseURL, batchType, status, page, limit)

	resp, err := c.sendRequest("GET", url, nil)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	var result struct {
		Payload models.BatchDocumentsResponse `json:"payload"`
	}
	err = json.NewDecoder(resp.Body).Decode(&result)
	if err != nil {
		return nil, err
	}

	return &result.Payload, nil
}

// GetDocumentsByBatch retrieves documents associated with a specific batch ID
func (c *APIClient) GetDocumentsByBatch(idBatch string, page, limit int) (*models.BatchDocumentsResponse, error) {
	url := fmt.Sprintf("%s/integrator/documents/by/id/batch/%s?page=%d&limit=%d", c.BaseURL, idBatch, page, limit)

	resp, err := c.sendRequest("GET", url, nil)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	var result struct {
		Payload models.BatchDocumentsResponse `json:"payload"`
	}
	err = json.NewDecoder(resp.Body).Decode(&result)
	if err != nil {
		return nil, err
	}

	return &result.Payload, nil
}

// ClearDocumentByUUID clears a document from the system using its unique identifier (UUID)
func (c *APIClient) ClearDocumentByUUID(uuid string) (bool, error) {
	url := fmt.Sprintf("%s/integrator/clear/document/%s", c.BaseURL, uuid)

	resp, err := c.sendRequest("GET", url, nil)
	if err != nil {
		return false, err
	}
	defer resp.Body.Close()

	var result struct {
		Status bool `json:"status"`
	}
	err = json.NewDecoder(resp.Body).Decode(&result)
	if err != nil {
		return false, err
	}

	return result.Status, nil
}

// DeleteBatch deletes a batch with the specified batch ID
func (c *APIClient) DeleteBatch(batchID string) (bool, error) {
	url := fmt.Sprintf("%s/integrator/delete/batch/%s", c.BaseURL, batchID)

	resp, err := c.sendRequest("DELETE", url, nil)
	if err != nil {
		return false, err
	}
	defer resp.Body.Close()

	var result struct {
		Status bool `json:"status"`
	}
	err = json.NewDecoder(resp.Body).Decode(&result)
	if err != nil {
		return false, err
	}

	return result.Status, nil
}

// DeleteDocumentFromBatch deletes a document from a batch using its unique identifier (UUID)
func (c *APIClient) DeleteDocumentFromBatch(uuid string) (bool, error) {
	url := fmt.Sprintf("%s/integrator/delete/by/uuid/%s", c.BaseURL, uuid)

	resp, err := c.sendRequest("DELETE", url, nil)
	if err != nil {
		return false, err
	}
	defer resp.Body.Close()

	var result struct {
		Status bool `json:"status"`
	}
	err = json.NewDecoder(resp.Body).Decode(&result)
	if err != nil {
		return false, err
	}

	return result.Status, nil
}

// GetDocumentTypes retrieves all document types for the user
func (c *APIClient) GetDocumentTypes() ([]models.DocumentType, error) {
	url := fmt.Sprintf("%s/integrator/documents/type/all/user", c.BaseURL)

	resp, err := c.sendRequest("GET", url, nil)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	var result struct {
		Payload []models.DocumentType `json:"payload"`
	}
	err = json.NewDecoder(resp.Body).Decode(&result)
	if err != nil {
		return nil, err
	}

	return result.Payload, nil
}

// CreateBatch creates a new batch with the specified name and type
func (c *APIClient) CreateBatch(name string, batchType models.BatchType) (*models.Response, error) {
	url := fmt.Sprintf("%s/integrator/create/batch", c.BaseURL)

	data := struct {
		BatchName string `json:"batch_name"`
		BatchType string `json:"batch_type"`
	}{
		BatchName: name,
		BatchType: string(batchType),
	}

	payload, err := json.Marshal(data)
	if err != nil {
		return nil, err
	}

	resp, err := c.sendRequest("POST", url, bytes.NewBuffer(payload))
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	var result models.Response
	err = json.NewDecoder(resp.Body).Decode(&result)
	if err != nil {
		return nil, err
	}

	return &result, nil
}

// UploadFile uploads a file to a specified batch on a remote server
func (c *APIClient) UploadFile(file *models.File, batchID string, maxRetries int, retryDelay time.Duration) (*models.UploadResult, error) {
	url := fmt.Sprintf("%s/integrator/append/to/batch/%s", c.BaseURL, batchID)

	for attempt := 0; attempt < maxRetries; attempt++ {
		body := &bytes.Buffer{}
		writer := multipart.NewWriter(body)

		if fileData, ok := file.File.([]byte); ok {
			part, err := writer.CreateFormFile("file", file.Filename)
			if err != nil {
				return nil, err
			}
			_, err = part.Write(fileData)
			if err != nil {
				return nil, err
			}
		} else if fileURL, ok := file.File.(string); ok {
			writer.WriteField("file_url", fileURL)
			writer.WriteField("file_name", file.Filename)
		} else {
			return nil, fmt.Errorf("unsupported file type")
		}

		writer.WriteField("type_document", file.TypeDocument)

		err := writer.Close()
		if err != nil {
			return nil, err
		}

		req, err := http.NewRequest("POST", url, body)
		if err != nil {
			return nil, err
		}

		req.Header.Set("Content-Type", writer.FormDataContentType())
		req.Header.Set("key", c.Key)
		req.Header.Set("secret", c.Secret)

		resp, err := c.Client.Do(req)
		if err != nil {
			if attempt == maxRetries-1 {
				return &models.UploadResult{
					Success:      false,
					Filename:     file.Filename,
					ErrorMessage: err.Error(),
				}, nil
			}
			time.Sleep(retryDelay)
			continue
		}
		defer resp.Body.Close()

		var result struct {
			Status  bool     `json:"status"`
			Payload []string `json:"payload"`
		}
		err = json.NewDecoder(resp.Body).Decode(&result)
		if err != nil {
			return nil, err
		}

		if result.Status {
			return &models.UploadResult{
				Success:  true,
				Filename: file.Filename,
				UUID:     result.Payload[0],
			}, nil
		}

		if attempt == maxRetries-1 {
			return &models.UploadResult{
				Success:      false,
				Filename:     file.Filename,
				ErrorMessage: "max retries reached",
			}, nil
		}

		time.Sleep(retryDelay)
	}

	return &models.UploadResult{
		Success:      false,
		Filename:     file.Filename,
		ErrorMessage: "max retries reached",
	}, nil
}

// AppendJob processes a job by uploading all files associated with it to a specified batch
func (c *APIClient) AppendJob(job *models.Job, batchID string, maxRetries int, retryDelay time.Duration) (map[string][]models.UploadResult, error) {
	results := map[string][]models.UploadResult{
		"successful": {},
		"failed":     {},
	}

	for _, file := range job.Files {
		result, err := c.UploadFile(&file, batchID, maxRetries, retryDelay)
		if err != nil {
			return nil, err
		}
		if result.Success {
			results["successful"] = append(results["successful"], *result)
		} else {
			results["failed"] = append(results["failed"], *result)
		}
	}

	return results, nil
}

// SearchInBrain performs a search operation using the provided search parameters
func (c *APIClient) SearchInBrain(searchParams *models.SearchParameters) (*models.ResultsSearch, error) {
	url := fmt.Sprintf("%s/integrator/search/brain", c.BaseURL)

	payload, err := json.Marshal(searchParams)
	if err != nil {
		return nil, err
	}

	resp, err := c.sendRequest("POST", url, bytes.NewBuffer(payload))
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	var result struct {
		Status  bool                 `json:"status"`
		Payload models.ResultsSearch `json:"payload"`
	}
	err = json.NewDecoder(resp.Body).Decode(&result)
	if err != nil {
		return nil, err
	}

	if !result.Status {
		return &models.ResultsSearch{Results: []models.Result{}}, nil
	}

	return &result.Payload, nil
}

// ProcessItem processes an item within a specified batch
func (c *APIClient) ProcessItem(batchID string) (bool, error) {
	url := fmt.Sprintf("%s/integrator/run/qa/batch/all/%s", c.BaseURL, batchID)

	resp, err := c.sendRequest("POST", url, nil)
	if err != nil {
		return false, err
	}
	defer resp.Body.Close()

	var result struct {
		Status bool `json:"status"`
	}
	err = json.NewDecoder(resp.Body).Decode(&result)
	if err != nil {
		return false, err
	}

	return result.Status, nil
}

// sendRequest is a helper function to send HTTP requests
func (c *APIClient) sendRequest(method, url string, body io.Reader) (*http.Response, error) {
	req, err := http.NewRequest(method, url, body)
	if err != nil {
		return nil, err
	}

	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("key", c.Key)
	req.Header.Set("secret", c.Secret)

	resp, err := c.Client.Do(req)
	if err != nil {
		return nil, err
	}

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("API request failed with status code: %d", resp.StatusCode)
	}

	return resp, nil
}
