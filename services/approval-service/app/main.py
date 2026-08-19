

from fastapi import FastAPI, HTTPException


from pydantic import BaseModel


from typing import List


app = FastAPI(
    title="Approval Microservice API",
    description="Handles Data Steward review queues, approvals, and rejection reasons.",
    version="1.0.0"
)

# --- PYDANTIC MODELS (Data Contracts) ---

# Schema for item in Data Steward review queue
class PendingSubmission(BaseModel):
    submissionId: str  
    productId: str      
    productName: str    
    supplierId: str    
    status: str         
    createdAt: str    

# Schema for rejection request body
class RejectRequest(BaseModel):
    reason: str         # Steward's explicit reason for rejection

# --- MOCK DATABASE ---

submissions_db = [
    {
        "submissionId": "sub-202",
        "productId": "prod-101",
        "productName": "Organic Apples",
        "supplierId": "sup-88",
        "status": "PENDING",
        "createdAt": "2026-06-01T12:00:00Z"
    },
    {
        "submissionId": "sub-203",
        "productId": "prod-103",
        "productName": "Artisanal Cheese",
        "supplierId": "sup-45",
        "status": "PENDING",
        "createdAt": "2026-06-02T14:30:00Z"
    }
]

# --- API ENDPOINTS ---


@app.get("/api/v1/approvals/pending", response_model=List[PendingSubmission])
def get_pending_submissions():
    """
    Fetch all product submissions currently waiting in PENDING state for Data Steward review.
    """
    
    pending_items = [s for s in submissions_db if s["status"] == "PENDING"]
    return pending_items


@app.post("/api/v1/approvals/{submissionId}/approve")
def approve_submission(submissionId: str):
    """
    Approve a pending submission, changing its status to APPROVED.
    """
   
    for sub in submissions_db:
        if sub["submissionId"] == submissionId:
            sub["status"] = "APPROVED" 
            return {"message": "Submission approved successfully."}
            
    
    raise HTTPException(status_code=404, detail="Submission not found.")


@app.post("/api/v1/approvals/{submissionId}/reject")
def reject_submission(submissionId: str, request: RejectRequest):
    """
    Reject a pending submission, updating status to REJECTED and capturing the reason.
    """
   
    for sub in submissions_db:
        if sub["submissionId"] == submissionId:
            sub["status"] = "REJECTED"            
            sub["rejectionReason"] = request.reason 
            return {"message": "Submission rejected successfully."}
            
   
    raise HTTPException(status_code=404, detail="Submission not found.")