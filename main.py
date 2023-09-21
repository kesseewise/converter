import json
import os
import xml.etree.ElementTree as ET


coco_data = {
    "info": {
        "description": "Your dataset description",
        "url": "Your dataset URL",
        "version": "1.0",
        "year": 2023,
        "contributor": "Your name",
        "date_created": "2023-09-21"
    },
    "licenses": [],
    "images": [],
    "annotations": [],
    "categories": []
}


xml_dir = "/content/drive/MyDrive/testing/degreasing/xml"
image_dir = "/content/drive/MyDrive/testing/degreasing/Image"


def parse_xml(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()

    image_info = {
        "id": None,
        "file_name": None,
        "width": None,
        "height": None
    }

    objects = []

    for elem in root:
        if elem.tag == "filename":
            image_info["file_name"] = os.path.join(image_dir, elem.text)
        elif elem.tag == "size":
            for sub_elem in elem:
                if sub_elem.tag == "width":
                    image_info["width"] = int(sub_elem.text)
                elif sub_elem.tag == "height":
                    image_info["height"] = int(sub_elem.text)
        elif elem.tag == "object":
            obj_info = {
                "category_id": None,  # Initialize category_id
                "bbox": [],
                "area": None,
                "iscrowd": 0
            }
            for sub_elem in elem:
                if sub_elem.tag == "name":
                    
                    category_name = sub_elem.text
                    obj_info["category_id"] = get_category_id(category_name)
                elif sub_elem.tag == "bndbox":
                    for bb_elem in sub_elem:
                        obj_info["bbox"].append(float(bb_elem.text))
            obj_info["area"] = obj_info["bbox"][2] * obj_info["bbox"][3]  # Width * Height
            objects.append(obj_info)

    return image_info, objects


category_id_map = {}  
def get_category_id(category_name):
    if category_name not in category_id_map:
       
        new_id = len(category_id_map) + 1
        category_id_map[category_name] = new_id
    return category_id_map[category_name]


image_id = 1
annotation_id = 1

for filename in os.listdir(xml_dir):
    if filename.endswith(".xml"):
        xml_file = os.path.join(xml_dir, filename)
        image_info, objects = parse_xml(xml_file)

        # Set image ID
        image_info["id"] = image_id
        image_id += 1

      
        for obj in objects:
            obj["id"] = annotation_id
            annotation_id += 1
            obj["image_id"] = image_info["id"]
            coco_data["annotations"].append(obj)

       
        coco_data["images"].append(image_info)


for category_name, category_id in category_id_map.items():
    category_info = {
        "id": category_id,
        "name": category_name,
        "supercategory": "object"
    }
    coco_data["categories"].append(category_info)

output_path = "/content/dump/output_coco.json"
with open(output_path, "w") as json_file:
    json.dump(coco_data, json_file, indent=4)
