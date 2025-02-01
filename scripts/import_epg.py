import xml.etree.ElementTree as ET
import requests
import os
import base64

GITHUB_REPO_API = 'https://api.github.com/repos/zeknewbe/porong/contents/merged_epg.xml'

def fetch_xml(url):
    response = requests.get(url)
    return ET.ElementTree(ET.fromstring(response.text))

def merge_trees(tree1, tree2):
    root1 = tree1.getroot()
    root2 = tree2.getroot()

    for child in root2:
        root1.append(child)

    return tree1

def write_to_github(content, token):
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json',
        'Content-Type': 'application/json'
    }

    # Try to fetch the SHA of the existing file
    try:
        response = requests.get(GITHUB_REPO_API, headers=headers)
        response.raise_for_status()
        sha = response.json().get('sha', '')
    except requests.RequestException as e:
        # If the file doesn't exist (404 error), create it
        if e.response.status_code == 404:
            print("File not found. Creating a new one...")
            sha = None
        else:
            print(f"Error fetching SHA for file: {e}")
            exit(1)

    encoded_content = base64.b64encode(content.encode('utf-8')).decode('utf-8')
    data = {
        "message": "Updated merged EPG file",
        "content": encoded_content
    }

    if sha:  # If SHA is present, include it in the data (means we're updating the file)
        data["sha"] = sha

    try:
        response = requests.put(GITHUB_REPO_API, headers=headers, json=data)
        if response.status_code in [200, 201]:  # 200 for update, 201 for creation
            print("File successfully updated!")
        else:
            print(f"Failed to update. Status Code: {response.status_code}. Response: {response.text}")
    except requests.RequestException as e:
        print(f"Error writing to GitHub: {e}")
        exit(1)

if __name__ == "__main__":
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("ERROR: GITHUB_TOKEN not set!")
        exit(1)

    tree1 = fetch_xml('https://raw.githubusercontent.com/AqFad2811/epg/main/epg.xml')
    tree2 = fetch_xml('https://raw.githubusercontent.com/azimabid00/epg/refs/heads/main/astro_epg.xml')
    tree3 = fetch_xml('https://raw.githubusercontent.com/AqFad2811/epg/main/astro.xml')
    tree4 = fetch_xml('https://raw.githubusercontent.com/AqFad2811/epg/main/indonesia.xml')
    tree5 = fetch_xml('https://raw.githubusercontent.com/AqFad2811/epg/main/rtmklik.xml')
    tree6 = fetch_xml('https://raw.githubusercontent.com/AqFad2811/epg/main/singapore.xml')
    tree7 = fetch_xml('https://raw.githubusercontent.com/AqFad2811/epg/main/unifitv.xml')
    tree8 = fetch_xml('https://www.bevy.be/bevyfiles/singaporepremium.xml.gz')
    tree9 = fetch_xml('https://www.bevy.be/bevyfiles/indonesiapremium3.xml.gz')
    tree10 = fetch_xml('https://raw.githubusercontent.com/mitthu786/tvepg/main/tataplay/epg.xml.gz')
    tree11 = fetch_xml('https://raw.githubusercontent.com/matthuisman/i.mjh.nz/refs/heads/master/all/epg.xml')
    tree12 = fetch_xml('https://raw.githubusercontent.com/azimabid00/epg/refs/heads/main/unifi_epg.xml')

    

    merged_tree = merge_trees(tree1, tree2, tree3, tree4, tree5, tree6, tree7, tree8, tree9, tree10, tree11, tree12)
    merged_xml = ET.tostring(merged_tree.getroot(), encoding='utf-8').decode('utf-8')

    write_to_github(merged_xml, token)
