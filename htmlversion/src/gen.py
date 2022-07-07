import json
import random
import os


class Generator:
    types = [
        "button", "checkbox", "image", "file", "password",
        "radio", "text", "color", "date", "range"
    ]

    def __init__(self, args):
        if len(args) not in (3, 4) and args[1] != "multiple":
            print("Too many or no input file provided. Please provide one JSON"
                  "date file for the generation (and optionally one destination file).")
            raise SystemExit("Aborting")

        # Single file generation
        if (args[1] == "single"):
            try:
                with open(args[2], "r") as file:
                    content = file.read()
                    self.data = json.loads(content)["data"]
            except Exception:
                print(f"File {args[1]} was not found, has wrong data format or"
                       "is corrupted. Please check your input file. Aborting.")
                raise SystemExit("Aborting")

        # Multiple file generation
        elif (args[1] == "multiple"):
            self.data = []
            try:
                for file in args[2:]:
                    with open(file, "r") as f:
                        content = f.read()
                        self.data.append(json.loads(content))
            except Exception:
                print(f"File {file} was not found, has wrong data format or is"
                       "corrupted. Please check your input file.")
                raise SystemExit("Aborting")

        # Setting img file destination with custom/default
        # Trimming the destination file name to remove the extension
        self.dest = args[3].split('.')[0] if (len(args) == 4 and args[1] == "single") else "./image"


    @staticmethod
    def generate_html(data, filename=None):
        """Generate the HTML/CSS for JSON-like data"""
        document = "<!DOCTYPE html><head></head><body>"

        for i, element in enumerate(data):
            elem_type = element.get("type")
            content = element.get("content")
            name = element.get("name")
            value = element.get("value")

            # Coordinates and size are required arguments. If they do not
            # exist, the program will crash.
            try:
                coord = element["coordinates"]["x"], element["coordinates"]["y"]
            except KeyError:
                print(f"No coordinates found in file {filename if filename else ''}")
                raise SystemExit("Aborting")

            height, width = (
                element["coordinates"]["height"],  # x
                element["coordinates"]["width"]    # y
            )


            # We start filling the document from there
            document += f"<div style='position:absolute;left:{coord[0]}px;"  \
                        f"top:{coord[1]}px'><input id='{chr(65 + i)}' style='"

            if elem_type.lower() == "image":
                document += f"transform:scale({width},{height});transform-origin:top left' src='./src/cross.svg'"
            elif elem_type not in ("radio", "checkbox"):
                document += f"width:{width}px;height:{height}px' "
            else:
                document += "'"

            document += f" type='{elem_type}' name='{name}'"

            # If 'value' exists add field
            document += f" value='{value}'" if value else ""

            # If 'content' exists add field
            document += f" content='{content}'" if content else ""

            if elem_type.lower() in ("radio", "checkbox"):
                document += f"><label for='{chr(65 + i)}' style='font-family:sans-serif'>{content}</label"

            document += "></div>"

        document += "</body></html>"

        return document


    @staticmethod
    def generate_json(amount, lower_elem_bound=1, upper_elem_bound=10, xmax=1920, ymax=1080, dimmin=10, dimmax=400):
        for i in range(1, amount + 1):
            print(f"Generated {i}/{amount} files.")
            elements = {"data": []}
            nbelem = random.randint(1, 10)

            for j in range(nbelem):
                # Generating valid, non-overlapping dimensions for each element
                width = random.randint(dimmin, dimmax)
                height = random.randint(dimmin, dimmax)
                posx = random.randint(0, xmax)
                posy = random.randint(0, ymax)

                while has_collision(((posx, posy), (posx + width, posy + height)), elements["data"]):
                    width = random.randint(dimmin, dimmax)
                    height = random.randint(dimmin, dimmax)
                    posx = random.randint(0, xmax)
                    posy = random.randint(0, ymax)

                elements["data"].append({
                    "type": random.choice(Generator.types),
                    "value": "value",
                    "name": "name",
                    "content": "content",
                    "coordinates": {"x": posx, "y": posy, "width": width, "height": height}
                })

            with open(f"./jsons/{str(i).zfill(len(str(amount)))}.json", "w") as file:
                json.dump(elements, file, indent=2)


    def generate_image(self, page=None, dest=None):
        html = Generator.generate_html(page if (page is not None) else self.data)
        with open(f"./htmls/{dest}.html", "w") as file: file.write(html)
        os.system("wkhtmltoimage --height 1080 --width 1920 --allow"
                 f"./src/cross.svg ./htmls/{dest}.html ./images/{self.dest if dest is None else dest}.jpg")


    def generate_multiple_images(self, dest=None):
        """
        Calls the `generate_image` func on each element of the data list.
        Does not allow to set a destination file.
        """
        for i, page in enumerate(self.data):
            self.generate_image(page=page, dest=i)


def has_collision(obj, elem_list):
    for elem in elem_list:
        dim = elem["coordinates"]["width"], elem["coordinates"]["height"]
        pos = elem["coordinates"]["x"], elem["coordinates"]["y"]

        if (obj[0][0] < (pos[0] + dim[0]) and obj[1][0] > pos[0] and obj[0][1] < (pos[1] + dim[1]) and obj[1][1] > pos[1]):
            return True

    return False
