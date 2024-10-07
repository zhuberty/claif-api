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
