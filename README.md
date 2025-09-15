# Lead Intent Scorer API

## Setup Steps

1. **Clone the repository**
	 ```bash
	 git clone https://github.com/<your-username>/leadintentscorer.git
	 cd leadintentscorer
	 ```

2. **Install dependencies**
	 ```bash
	 pip install -r requirements.txt
	 ```

3. **Set your OpenAI API key**
	 ```bash
	 export OPENAI_API_KEY=your-openai-key
	 ```

4. **Run the server**
	 ```bash
	 uvicorn main:app --reload
	 ```

## API Usage Examples (cURL/Postman)

### Add Offer
```bash
curl -X POST "http://localhost:8000/offer" \
	-H "Content-Type: application/json" \
	-d '{
		"name": "AI Outreach Automation",
		"value_props": ["24/7 outreach", "6x more meetings"],
		"ideal_use_cases": ["B2B SaaS mid-market"]
	}'
```

### Upload Leads CSV
```bash
curl -X POST "http://localhost:8000/leads/upload" \
	-F "file=@leads.csv"
```

### Run Scoring
```bash
curl -X POST "http://localhost:8000/score"
```

### Get Results (JSON)
```bash
curl "http://localhost:8000/results"
```

### Export Results (CSV)
```bash
curl "http://localhost:8000/results/csv" -o results.csv
```

## Explanation of Rule Logic & Prompts Used

### Rule Layer (max 50 points)
- **Role relevance:** decision maker (+20), influencer (+10), else 0
- **Industry match:** exact ICP (+20), adjacent (+10), else 0
- **Data completeness:** all fields present (+10)

### AI Layer (max 50 points)
- Each lead and offer is sent to OpenAI with the prompt:
	```
	Product/Offer: <name>
	Value Props: <value_props>
	Ideal Use Cases: <ideal_use_cases>
	Lead: <lead details>
	Classify intent (High/Medium/Low) and explain in 1–2 sentences.
	```
- AI response is mapped: High = 50, Medium = 30, Low = 10

### Final Score
`final_score = rule_score + ai_points`