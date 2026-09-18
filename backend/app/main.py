from fastapi import FastAPI


app = FastAPI(
	title="Warband HQ API",
	description="Backend API for Warband HQ",
	version="0.1.0"
)


@app.get("/")
def root():
	return {"message": "Warband HQ API is runing"}
