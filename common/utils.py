from datetime import timezone
from dateutil import parser



def parse_timestamp(value):
	if not value:
		return None

	cleaned = value.strip().strip(".")

	if not cleaned or cleaned.lower() in {"na", "n/a", "-"}:
		return None

	if "/" in cleaned and any(char.isalpha() for char in cleaned):
		return None

	try:
		parsed = parser.parse(cleaned, dayfirst=True)
		return parsed.isoformat()
	
	except Exception:
		return None


