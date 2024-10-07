from tabulate import tabulate

def display_annotations(annotations):
    table_data = []
    for anno in annotations:
        truncated_text = anno['annotation_text'][:20] + '...' if len(anno['annotation_text']) > 20 else anno['annotation_text']
        row = [anno['id'], truncated_text, anno['reviews_count']]
        table_data.append(row)
    
    headers = ["ID", "Annotation Text", "Review Count"]
    print(tabulate(table_data, headers, tablefmt="grid"))
