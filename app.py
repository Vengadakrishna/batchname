import os
from dotenv import load_dotenv
from fastapi import FastAPI
from pymongo import MongoClient
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Load environment variables
load_dotenv()

# load env
mongo_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
database_name = os.getenv("DATABASE_NAME")
collection_name = os.getenv("COLLECTION_NAME")

# mongo
mongo_client = MongoClient(mongo_uri)
db = mongo_client[database_name]
collection = db[collection_name]

# initialize fastAPI
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class BatchRequest(BaseModel):
    batchnames: list[str]
    status: str

@app.get("/")
def read_root():
    return JSONResponse(content={"status": "success"}, status_code=200)


@app.post("/process_again")
async def update_status(request: BatchRequest):
    batchnames = request.batchnames
    status = request.status
    modified_count = 0
    for batchname in batchnames:
        result = collection.update_many(
            {"batchname": batchname, "status": status},
            {"$set": {"status": "notprocessed"}}
        )
        modified_count += result.modified_count
    if modified_count > 0:
        return JSONResponse(content={"message": f"{modified_count} images updated successfully."}, status_code=200)
    else:
        return JSONResponse(content={"message": "No images found to update."}, status_code=404)



if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)