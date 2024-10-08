import requests
from auth_utils import get_auth_headers, handle_unauthorized


def create_annotation_review(base_url, annotation):
    print(f"Annotation text: {annotation['annotation_text']}")

    # Prompt the user for answers
    q_does_anno_match_content = input("Does the annotation match the content? (yes/no): ").strip().lower() == 'yes'
    q_can_anno_be_halved = input("Can the annotation be halved? (yes/no): ").strip().lower() == 'yes'
    q_how_well_anno_matches_content = int(input("How well does the annotation match the content (1-5): ").strip())
    q_can_you_improve_anno = input("Can you improve the annotation? (yes/no): ").strip().lower() == 'yes'
    q_can_you_provide_markdown = input("Can you provide markdown? (yes/no): ").strip().lower() == 'yes'

    payload = {
        "annotation_id": annotation['id'],
        "q_does_anno_match_content": q_does_anno_match_content,
        "q_can_anno_be_halved": q_can_anno_be_halved,
        "q_how_well_anno_matches_content": q_how_well_anno_matches_content,
        "q_can_you_improve_anno": q_can_you_improve_anno,
        "q_can_you_provide_markdown": q_can_you_provide_markdown,
    }

    url = f"{base_url}/annotation_reviews/create"
    headers = get_auth_headers()
    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        print("Annotation review created successfully!")
    elif response.status_code == 401:
        new_token = handle_unauthorized(base_url)
        if new_token:
            headers = {"Authorization": f"Bearer {new_token}"}
            response = requests.post(url, json=payload, headers=headers)
            if response.status_code == 200:
                print("Annotation review created successfully!")
            else:
                print(f"Error creating annotation review: {response.status_code}")
    else:
        print(f"Error creating annotation review: {response.status_code}")