import os, glob
import json
from tqdm import tqdm
from collections import OrderedDict
import cv2
import xmltodict
import argparse


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-r', '--input_dir', type=str, required=True)
    parser.add_argument('-o', '--output_filename', type=str, default='annotations.json')
    return parser.parse_args()


def VOC2Json(xml_dir, output_filename):
    
    if not os.path.isdir(xml_dir):
        raise ValueError(f'the argment must be a directory')
        
    num_files = len(os.listdir(xml_dir))
    xml_files = glob.glob(f'{xml_dir}/*.xml')
    xml_files.sort()
    
    attrDict = {}
    attrDict["categories"]=[{"supercategory":"none","id":1,"name":"date"},
                            {"supercategory":"none","id":2,"name":"price"},
                            {"supercategory":"none","id":3,"name":"company"}
                           ]
    
    
    images = []
    annotations = []

    # for idx, xml_file in tqdm(enumerate(xml_files), total=num_files):
    for image_id, xml_file in enumerate(xml_files):
        image = {}
        doc = xmltodict.parse(open(xml_file).read())

        image["file_name"] = str(doc['annotation']['filename'])
        image["image_id"] = image_id
        image["height"] = int(doc['annotation']['size']['height'])
        image["width"] = int(doc['annotation']['size']['width'])

        print(f"File Name: {xml_file} and image_id: {image_id}")
        images.append(image)

        id1 = 1
        if 'object' in doc['annotation']:
            for obj in doc['annotation']['object']:
                for value in attrDict["categories"]:
                    annotation = {}
                    if str(obj['name']) == value["name"]:
                        annotation["iscrowd"] = 0
                        annotation["image_id"] = image_id
                        x1 = int(obj["bndbox"]["xmin"])  - 1
                        y1 = int(obj["bndbox"]["ymin"]) - 1
                        x2 = int(obj["bndbox"]["xmax"]) - x1
                        y2 = int(obj["bndbox"]["ymax"]) - y1
                        annotation["bbox"] = [x1, y1, x2, y2]
                        annotation["area"] = float(x2 * y2)
                        annotation["category_id"] = value["id"]
                        annotation["ignore"] = 0
                        annotation["id"] = id1
                        annotation["segmentation"] = [[x1,y1,x1,(y1 + y2), (x1 + x2), (y1 + y2), (x1 + x2), y1]]
                        id1 +=1

                        annotations.append(annotation)

        else:
            print("File: {} doesn't have any object".format(file))

    attrDict["images"] = images	
    attrDict["annotations"] = annotations
    attrDict["type"] = "instances"

    
    # save attrDict
    jsonString = json.dumps(attrDict)
    with open(output_filename, "w") as f:
        f.write(jsonString)


if __name__ == "__main__":
    args = parse_args()
    XML_DIR = args.input_dir
    OUTPUT_FILENAME = args.output_filename
    VOC2Json(XML_DIR, OUTPUT_FILENAME)