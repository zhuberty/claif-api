from tabulate import tabulate

def display_annotations(annotations):
    table_data = []
    for anno in annotations:
        # Truncate annotation text if it's longer than 20 characters
        truncated_text = anno["annotation_text"][:20] + "..." if len(anno["annotation_text"]) > 20 else anno["annotation_text"]
        
        # Convert milliseconds to seconds for start and end times
        start_seconds = anno["start_time_milliseconds"] / 1000
        end_seconds = anno["end_time_milliseconds"] / 1000
        
        # Prepare row data
        row = [anno["id"], truncated_text, anno["reviews_count"], f"{start_seconds:.2f}", f"{end_seconds:.2f}", anno["level"]]
        table_data.append(row)
    
    headers = ["ID", "Annotation Text", "Reviews", "Start", "End", "Level"]
    print(tabulate(table_data, headers, tablefmt="grid"))


def display_recordings_list(recordings):
    table_data = []
    for recording in recordings:
        # Truncate description if it's longer than 20 characters
        truncated_title = recording["title"][:30] + "..." if len(recording["title"]) > 30 else recording["title"]
        
        # Prepare row data
        row = [
            recording["id"],
            truncated_title,
            recording["revision_number"], 
            recording["annotations_count"],
            f"{int(recording['size_bytes'] / 1024)}KB", 
            f"{int(recording['duration_milliseconds'] / 1000)}s",
            recording["creator_username"],
        ]
        table_data.append(row)
    
    headers = ["ID", "Title", "Revision", "Annos", "Size", "Duration", "Creator"]
    print(tabulate(table_data, headers, tablefmt="grid"))