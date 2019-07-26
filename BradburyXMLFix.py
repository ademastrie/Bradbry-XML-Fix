from tkinter import *
from tkinter import ttk
from tkinter.filedialog import askopenfilename
import os
import xml.etree.ElementTree as et

root = Tk()
xmlp = et.XMLParser(encoding="utf-8")


# This is where we launch the file manager bar.
def OpenFile():
    name = askopenfilename(initialdir="",
                           filetypes=(("xml File", "*.xml"), ("All Files", "*.*")),
                           title="Choose a file."
                           )
    print(name)
    # Using try in case user types in unknown file or closes without choosing a file.
    try:
        with open(name, encoding='utf-8') as UseFile:
            tree = et.parse(UseFile)
            root_element = tree.getroot()

            order_number = root_element.find('Order/OrderNumber').text
            print("Order Number: " + order_number)

            compare_x_offset = 0
            pos_offset = float(input("Positive Offset: "))
            neg_offset = float(input("Negative Offset: "))

            # look through the jobs individually and within those jobs look at each part and hole and evaluate
            for j in root_element.iterfind('.//Job'):
                for p in j.iterfind('.//Part'):
                    item_desc = (p.get('ItemDescription'))

                    for child in p.iterfind('.//Hole'):
                        # if its not a wall angle we don't need to worry about it.
                        if item_desc == 'Right Wall Angle' or item_desc == 'Left Wall Angle':

                            x_offset = float(child.get('XOffset'))
                            y_offset = float(child.get('YOffset'))
                            hole_type = (child.get('HoleType'))

                            # if we are looking at a round hole we know we are at the start of an angle.
                            # Set appropriate values
                            if hole_type == 'R916' or hole_type == 'R1116':
                                compare_x_offset = 0
                                first_half = True
                                if item_desc == 'Right Wall Angle':
                                    print(item_desc)
                                    if y_offset < 0:
                                        negative = True
                                    else:
                                        negative = False
                                else:
                                    print(item_desc)

                            # if our xOffset is bigger than our reference offset and y is still zero we know that we
                            # are in the middle of a angle and need to switch to the opposite offset
                            if x_offset < compare_x_offset and y_offset == 0:
                                    first_half = False
                                    compare_x_offset = x_offset

                            # if xOffset is bigger than the reference offset and y is zero
                            #  set the appropriate value to the y offset
                            if x_offset >= compare_x_offset and y_offset == 0:
                                # Right wall angle uses user input and Left will use the inverse
                                if item_desc == 'Right Wall Angle':
                                    posneg_correction = 1
                                elif item_desc == "Left Wall Angle":
                                    posneg_correction = -1

                                if negative and first_half:
                                    final_offset = str(neg_offset * posneg_correction)
                                    child.set('YOffset', final_offset)
                                    y_offset = float(child.get('YOffset'))
                                    print(' ["Hole Type" = {}] ["XOffset" = {}] ["YOffset" = {}]'.format
                                          (hole_type, x_offset, y_offset))
                                elif negative and not first_half:
                                    final_offset = str(pos_offset * posneg_correction)
                                    child.set('YOffset', final_offset)
                                    y_offset = float(child.get('YOffset'))
                                    print(' ["Hole Type" = {}] ["XOffset" = {}] ["YOffset" = {}]'.format
                                          (hole_type, x_offset, y_offset))

                                if not negative and first_half:
                                    final_offset = str(pos_offset * posneg_correction)
                                    child.set('YOffset', final_offset)
                                    y_offset = float(child.get('YOffset'))
                                    print(' ["Hole Type" = {}] ["XOffset" = {}] ["YOffset" = {}]'.format
                                          (hole_type, x_offset, y_offset))
                                elif not negative and not first_half:
                                    final_offset = str(neg_offset * posneg_correction)
                                    child.set('YOffset', final_offset)
                                    y_offset = float(child.get('YOffset'))
                                    print(' ["Hole Type" = {}] ["XOffset" = {}] ["YOffset" = {}]'.format
                                          (hole_type, x_offset, y_offset))

                        compare_x_offset = x_offset
                        tree.write('' + order_number + '.xml')



    except:
        print("No file exists")


Title = root.title("File Opener")
label = ttk.Label(root, text="Choose an xml", foreground="red", font=("Helvetica", 16))
label.pack()

# Menu Bar

menu = Menu(root)
root.config(menu=menu)

file = Menu(menu)

file.add_command(label='Open', command=OpenFile)
file.add_command(label='Exit', command=lambda: exit())

menu.add_cascade(label='File', menu=file)

root.mainloop()
