import argparse
import time
from datetime import datetime, timedelta

from scrapers.aiims_scraper import scrape as scrape_aiims
from scrapers.drdo_scraper import scrape as scrape_drdo
from scrapers.icmr_scraper import scrape as scrape_icmr
from scrapers.isro_scraper import scrape as scrape_isro
from scrapers.nic_scraper import scrape as scrape_nic
from scrapers.rbi_scraper import scrape as scrape_rbi


def run_all_scrapers():
	scrapers = [
		("AIIMS", scrape_aiims),
		("DRDO", scrape_drdo),
		("ICMR", scrape_icmr),
		("ISRO", scrape_isro),
		("NIC", scrape_nic),
		("RBI", scrape_rbi),
	]

	for label, scraper in scrapers:
		try:
			print(f"Starting {label} scraper")
			scraper()
			print(f"Finished {label} scraper")
		except Exception as exc:
			print(f"{label} scraper failed: {exc}")


def _seconds_until_next_midnight(now=None):
	if now is None:
		now = datetime.now()

	next_midnight = (now + timedelta(days=1)).replace(
		hour=0, minute=0, second=0, microsecond=0
	)

	return max(1, int((next_midnight - now).total_seconds()))


def run_daily_at_midnight():
	while True:
		run_all_scrapers()
		sleep_seconds = _seconds_until_next_midnight()
		print(f"Sleeping for {sleep_seconds} seconds until next midnight")
		time.sleep(sleep_seconds)


def main():
	parser = argparse.ArgumentParser(description="Run job scrapers")
	parser.add_argument(
		"--daemon",
		action="store_true",
		help="Run all scrapers once per day at midnight (local time)",
	)

	args = parser.parse_args()

	if args.daemon:
		run_daily_at_midnight()
	else:
		run_all_scrapers()


if __name__ == "__main__":
	main()