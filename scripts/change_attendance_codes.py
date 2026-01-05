import sys
sys.path.append("..")
from src.util import *

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

def pull_absences_to_csv(school_id: str, min_date: str, max_date: str, absence_type: str = None, name: str = None, output_path: str = None) -> Path:
	"""Pull absences via `sr_api_pull` and export to CSV.

	Parameters expected to be accepted by `sr_api_pull` are passed in `parameters`.
	"""
	params = {
		'active': '1',
		'school_ids': school_id,
		'min_date': min_date,
		'max_date': max_date,
		'absence_type_ids': absence_type
	}
		
	logging.info(f"Querying SR API for absences with: {params}")
	records = sr_api_pull('absences', parameters=params)

	# Determine output file path (use `name` if provided)
	default_dir = Path(__file__).parent
	if output_path:
		out_path = Path(output_path)
		if out_path.is_dir():
			if name:
				filename = name if name.lower().endswith('.csv') else f"{name}.csv"
			else:
				filename = f"absences_{school_id}_{min_date}_{max_date}.csv"
			out_file = out_path / filename
		else:
			out_file = out_path
	else:
		if name:
			filename = name if name.lower().endswith('.csv') else f"{name}.csv"
		else:
			filename = f"absences_{school_id}_{min_date}_{max_date}.csv"
		out_file = default_dir / filename

	# Write CSV
	out_file.parent.mkdir(parents=True, exist_ok=True)
	with out_file.open('w', newline='', encoding='utf-8') as f:
		if records:
			# Collect all keys across records to ensure consistent columns
			keys = sorted({k for r in records for k in (r.keys() if isinstance(r, dict) else [])})
			writer = csv.DictWriter(f, fieldnames=keys)
			writer.writeheader()
			for r in records:
				if isinstance(r, dict):
					writer.writerow({k: r.get(k, '') for k in keys})
				else:
					# If the record is not a dict, write its string representation
					writer.writerow({keys[0]: str(r)})
		else:
			# create an empty file with no rows
			pass

	logging.info(f"Wrote {len(records) if records else 0} records to {out_file}")
	return out_file


def _valid_date(s: str) -> str:
	try:
		datetime.datetime.strptime(s, '%Y-%m-%d')
		return s
	except ValueError:
		raise argparse.ArgumentTypeError("Date must be YYYY-MM-DD")


def main():
	parser = argparse.ArgumentParser(description="Tools for pulling and updating absences.")
	subparsers = parser.add_subparsers(dest='command')

	# pull subcommand
	pull_p = subparsers.add_parser('pull', help='Pull absences via sr_api_pull and export to CSV')
	pull_p.add_argument('--school-id', required=True, help='School id to filter by')
	pull_p.add_argument('--min-date', required=True, type=_valid_date, help='Start date YYYY-MM-DD')
	pull_p.add_argument('--max-date', required=True, type=_valid_date, help='End date YYYY-MM-DD')
	pull_p.add_argument('--absence-type', default=None, help='Absence type to filter (optional)')
	pull_p.add_argument('--name', default=None, help='Name to use for output CSV (optional)')
	pull_p.add_argument('--output', default=None, help='Output file path or directory (default: this folder)')

	# apply subcommand
	apply_p = subparsers.add_parser('apply', help='Apply changes from a CSV of absences')
	apply_p.add_argument('--csv', required=True, help='Path to CSV file produced by pull')
	apply_p.add_argument('--staff-member-id', required=False, help='Staff member id to include in payload (overrides CSV column)')
	apply_p.add_argument('--staff-member-column', default='staff_member_id', help='CSV column name to use for staff member id (if present)')
	apply_p.add_argument('--comments', default=None, help='Static comments to include (overrides CSV column)')
	apply_p.add_argument('--comments-column', default=None, help='CSV column name to use for comments (if present)')
	apply_p.add_argument('--absence-type-id', '--absence_type_id', required=True, help='Absence type id to set (required)')
	apply_p.add_argument('--dry-run', action='store_true', help='Do not send HTTP requests, only print what would be sent')

	args = parser.parse_args()

	if args.command == 'pull':
		pull_absences_to_csv(args.school_id, args.min_date, args.max_date, args.absence_type, args.name, args.output)
	elif args.command == 'apply':
		apply_changes_from_csv(args.csv, args.staff_member_id, args.comments, args.comments_column, args.absence_type_id, args.dry_run, staff_member_column=args.staff_member_column)
	else:
		parser.print_help()


def _find_absence_id_in_row(row: dict) -> Optional[str]:
	# common candidates
	for key in ['absence_id', 'absenceid', 'id', 'absenceId', 'Absence ID']:
		if key in row and row[key]:
			return row[key]
	# try lowercase keys
	for k, v in row.items():
		if k.lower().replace(' ', '_') in ('absence_id', 'id') and v:
			return v
	return None


def _find_field_in_row(row: dict, candidates: list) -> Optional[str]:
	for key in candidates:
		if key in row and row[key]:
			return row[key]
	# try lowercase/underscore variants
	lowermap = {k.lower().replace(' ', '_'): v for k, v in row.items()}
	for c in candidates:
		key = c.lower().replace(' ', '_')
		if key in lowermap and lowermap[key]:
			return lowermap[key]
	return None


def apply_changes_from_csv(csv_path: str, staff_member_id: Optional[str] = None, comments: Optional[str] = None, comments_column: Optional[str] = None, absence_type_id: str = '75', dry_run: bool = False, staff_member_column: str = 'staff_member_id') -> None:
	"""Read CSV and for each absence send a PUT and then a POST request.

	- PUT https://ca.schoolrunner.org/api/v1/absences/{absence_id} with JSON payload
	- POST https://ca.schoolrunner.org/absences/data?absence_filter=absence_id={absence_id}

	Prints and logs responses for debugging.
	"""
	csv_file = Path(csv_path)
	if not csv_file.exists():
		logging.error(f"CSV file not found: {csv_file}")
		return

	session = requests.Session()
	# attach Basic auth header using credentials from src.util (creds.json)
	try:
		auth_value = base64.b64encode(bytes(f"{credentials['sr_email']}:{credentials['sr_pass']}", "UTF-8")).decode("ascii")
		headers = {'Authorization': 'Basic ' + auth_value}
		session.headers.update(headers)
		logging.info("Attached Basic auth header to session from creds.json")
	except Exception as e:
		logging.warning(f"Could not attach auth header from credentials: {e}")

	with csv_file.open('r', newline='', encoding='utf-8') as f:
		reader = csv.DictReader(f)
		row_count = 0
		for row in reader:
			row_count += 1
			absence_id = _find_absence_id_in_row(row)
			if not absence_id:
				logging.error(f"Row {row_count}: no absence id found, skipping: {row}")
				print(f"Row {row_count}: no absence id found, skipping")
				continue

			# determine staff member id (CSV preferred unless CLI override provided)
			if staff_member_id:
				staff_id_val = staff_member_id
			else:
				# look for the specified column, then common alternatives
				staff_id_val = None
				if staff_member_column and staff_member_column in row and row[staff_member_column]:
					staff_id_val = row[staff_member_column]
				else:
					staff_id_val = _find_field_in_row(row, ['staff_member_id', 'staff_member', 'staff_id', 'staff member', 'staffMemberId', 'staffMember'])

			# determine comments (CSV preferred unless CLI override provided)
			if comments is not None:
				comment_val = comments
			elif comments_column and comments_column in row and row[comments_column]:
				comment_val = row[comments_column]
			else:
				# try common comment columns
				comment_val = row.get('comments', '') or row.get('comment', '') or ''

			if not staff_id_val:
				logging.warning(f"Row {row_count}: no staff member id found; proceeding with empty staff_member_id")
				print(f"Row {row_count}: no staff member id found; proceeding with empty staff_member_id")

			put_url = f"https://ca.schoolrunner.org/api/v1/absences/{absence_id}"
			payload = {
				"absence_id": str(absence_id),
				"staff_member_id": str(staff_id_val) if staff_id_val is not None else "",
				"comments": comment_val,
				"absence_type_id": str(absence_type_id),
				"active": "1",
			}

			logging.info(f"Row {row_count}: PUT {put_url} payload={payload}")
			print(f"Row {row_count}: PUT {put_url} payload={payload}")
			if not dry_run:
				try:
					put_resp = session.put(put_url, json=payload, timeout=30)
					logging.info(f"Row {row_count}: PUT status={put_resp.status_code} response={put_resp.text}")
					print(f"Row {row_count}: PUT status={put_resp.status_code}")
				except Exception as e:
					logging.exception(f"Row {row_count}: PUT request failed: {e}")
					print(f"Row {row_count}: PUT request failed: {e}")
					continue

			post_url = f"https://ca.schoolrunner.org/absences/data?absence_filter=absence_id={absence_id}"
			logging.info(f"Row {row_count}: POST {post_url}")
			print(f"Row {row_count}: POST {post_url}")
			if not dry_run:
				try:
					post_resp = session.post(post_url, timeout=30)
					logging.info(f"Row {row_count}: POST status={post_resp.status_code} response={post_resp.text}")
					print(f"Row {row_count}: POST status={post_resp.status_code}")
				except Exception as e:
					logging.exception(f"Row {row_count}: POST request failed: {e}")
					print(f"Row {row_count}: POST request failed: {e}")

	logging.info(f"Processed {row_count} rows from {csv_file}")
	print(f"Processed {row_count} rows from {csv_file}")


if __name__ == '__main__':
	main()

