from util import *

def deactivate_communications():
    if len(sys.argv) != 4:
        print("Usage: python deactivate_communications.py <school> <date YYYY-MM-DD> <communication type>")
        return
    school = sys.argv[1].strip().upper()
    if school not in school_info:
        print(f"Unknown school '{school}'. Available: {', '.join(school_info.keys())}")
        return
    date_str = sys.argv[2].strip()
    comm_name = sys.argv[3].strip().lower()

    # Lookup communication type
    comm_methods = sr_api_pull('communication-methods', {})
    comm_method = next((cm for cm in comm_methods if cm.get('name', '').lower() == comm_name), None)
    if not comm_method:
        print(f"Communication type '{comm_name}' not found.")
        return
    comm_type_id = comm_method.get('communication_method_id')

    # Fetch communications for given school, date, and type
    school_id = school_info[school]['sr_id']
    parameters = {
        'school_ids': school_id,
        'min_date': date_str,
        'max_date': date_str,
        'expand': 'staff_member,communication_method'
    }

    communications = sr_api_pull('communications', parameters)

    if not communications:
        print("No communications found to deactivate.")
        return

    # Filter communications by method and staff email
    filtered_comms = [
        comm for comm in communications
        if str(comm.get('communication_method_id')) == str(comm_type_id)
        and comm.get('staff_member', {}).get('email', '').lower() == 'data@collegiateacademies.org'
    ]

    if not filtered_comms:
        print("No communications found matching method and staff email filter.")
        return

    print(f"{len(filtered_comms)} communications will be deactivated:")
    for comm in filtered_comms:
        print(f"ID: {comm.get('communication_id')}, Date: {comm.get('date')}, Staff: {comm.get('staff_member', {}).get('display_name', '')}, Email: {comm.get('staff_member', {}).get('email', '')}, Method: {comm.get('communication_method', {}).get('name', '')}, Comments: {comm.get('comments', '')}")

    # Deactivate each filtered communication
    auth_header = 'Basic ' + base64.b64encode(bytes(f"{credentials['sr_email']}:{credentials['sr_pass']}", "UTF-8")).decode("ascii")
    for comm in filtered_comms:
        comm_id = comm.get('communication_id')
        url = f"https://ca.schoolrunner.org/api/v1/communications/{comm_id}"
        resp = requests.delete(url, headers={'Authorization': auth_header})
        if resp.status_code in (200, 204):
            print(f"Deactivated communication ID {comm_id}")
        else:
            print(f"Failed to deactivate ID {comm_id}: {resp.status_code} {resp.text}")

if __name__ == "__main__":
    deactivate_communications()
