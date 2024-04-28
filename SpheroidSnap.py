from matplotlib.backend_bases import MouseButton
from rich import box, print
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
import json
import matplotlib.pyplot as plt
import numpy as np
import scipy
import seaborn as sns
import shapely
import skimage as ski

main_console = Console(style="bold green")
second_console = Console(style="green")
error_console = Console(style="bold red")
info_console = Console(style="black on white")
table_console = Console()

points_to_keep = []
def on_click_keep(event):
    if event.button is MouseButton.RIGHT:
        points_to_keep.append(shapely.Point([event.xdata, event.ydata]))
    return

points_to_remove = []
def on_click_remove(event):
    if event.button is MouseButton.RIGHT:
        points_to_remove.append(shapely.Point([event.xdata, event.ydata]))
    return

def get_polygon_data(event):
    if event.button is MouseButton.RIGHT:
        click_point = shapely.Point([event.xdata, event.ydata])
        chosen_polygon = None
        polygon_number = -1
        for polygon in convex_hulls_polygons:
            if click_point.within(polygon):
                chosen_polygon = polygon
                polygon_number = convex_hulls_polygons.index(chosen_polygon)+1
                break
        if chosen_polygon == None:
            error_console.print("[!] Please pick a point INSIDE a shape.")
            return
        else:
            polygon_key = chosen_polygon.wkb
        
            table = Table(title="DATA [1/2]", style="black on white", box=box.DOUBLE_EDGE)
            table.add_column("Property", justify="center", style="black on white")
            table.add_column("Value", justify="center", style="black on white")
            
            table.add_row("Num. of sides", str(polygon_data_dict[polygon_key]['sides']))
            table.add_row("Perimeter", str(polygon_data_dict[polygon_key]['perimeter']))
            table.add_row("Area", str(polygon_data_dict[polygon_key]['area']))
            table.add_row("Polsby-Popper test", str(polygon_data_dict[polygon_key]['Polsby-Popper']))
            table_console.print(table, justify="center")
            
            table1 = Table(title="DATA[2/2]", style="black on white", box=box.DOUBLE_EDGE)
            table1.add_column("Regular n-gon", justify="center", style="black on white")
            table1.add_column("1-sample Wilcoxon signed rank statistic", justify="center", style="black on white")
            table1.add_column("p value", justify="center", style="black on white")
            
            similarity_vector = polygon_data_dict[polygon_key]['similarity_vector']
            for i in range(len(similarity_vector)):
                table1.add_row(str(i+3), str(similarity_vector[i][0]), str(similarity_vector[i][1]))
            table_console.print(table1, justify="center")
            
            fig1, ax1 = plt.subplots(3,1)
            plt.subplots_adjust(top=0.938, bottom=0.057, hspace=0.355)
            fig1.canvas.manager.set_window_title("Polygon #{n}".format(n=polygon_number))
            ax1[0].set_title("Right triangle area distribution")
            sns.histplot(sub_areas, ax=ax1[0], kde=True)
            ax1[1].set_title("Wilcoxon statistic")
            ax1[1].plot(np.arange(3, len(similarity_vector)+3), similarity_vector[:,0]) #+3 because we want to count from 3 on the x-axis
            ax1[2].set_title("Wilcoxon p-value")
            ax1[2].plot(np.arange(3, len(similarity_vector)+3), similarity_vector[:,1])
            plt.show()

sub_text = Text("v1.0", style="dim green on black")
title_text = Text("https://github.com/thepadguy/SpheroidSnap", style="dim green on black")
print(Panel(Text("SpheroidSnap", justify="center"), style="bold green on black", box=box.DOUBLE_EDGE, subtitle=sub_text, subtitle_align="center", title=title_text, title_align="center"))

main_console.print("[WELCOME] Please use only png images and follow instructions.")
path = input("[INPUT] image path and press Enter: ")
image = ski.io.imread(path)
main_console.print("[+] Read image.")
channels = image.shape[2]
if channels > 3:
    error_console.print("\t[-] Image has {c} channels, reducing them to 3".format(c=channels))
    image = image[:,:,:3]
fig, ax = plt.subplots()
fig.canvas.manager.set_window_title("Original image")
ski.io.imshow(image)
ax.axis('off')
plt.show()

#STEP 1 - Image to hsv
main_console.print("[+] Transforming RGB --> HSV")
hsv_image = ski.color.rgb2hsv(image)
saturation_channel = hsv_image[:,:,1]
fig, ax = plt.subplots()
fig.canvas.manager.set_window_title("Saturation channel")
ax.imshow(saturation_channel, cmap=plt.cm.gray)
ax.axis('off')
plt.show()

#STEP 2 - Triangle threshold
main_console.print("[+] Thresholding")
thresh = ski.filters.threshold_triangle(saturation_channel)
binary_image = saturation_channel >= thresh
masked_image = np.stack((image[:,:,0]*binary_image, image[:,:,1]*binary_image, image[:,:,2]*binary_image), axis=-1)
fig, ax = plt.subplots()
fig.canvas.manager.set_window_title("Thresholded image")
ax.imshow(masked_image)
ax.axis('off')
plt.show()

#STEP 3 - Find contours
main_console.print("[+] Finding contours")
contours = ski.measure.find_contours(binary_image)
contour_polygons = [shapely.Polygon(np.array([i[:,1], i[:,0]]).T) for i in contours] #here they are in format (x,y) and not in (y,x) anymore

second_console.print("[1/2] Right click inside the contour that you want to keep.", style="green")
second_console.print("\tPlease try to click in the center of said contour and preferably not in a point that is 'nested' in an unwanted contour.")
fig, ax = plt.subplots()
fig.canvas.manager.set_window_title("All contours")
ax.imshow(masked_image)
ax.axis('off')
for contour in contours:
    #contours are in form y,x
    ax.plot(contour[:,1], contour[:,0], linewidth=2)
binding_id = plt.connect('button_press_event', on_click_keep)
plt.show()

main_console.print("\t[+] Filtering contours.")
contour_polygons_to_keep = []
contours_to_keep = []
for point in points_to_keep:
    for i in range(len(contour_polygons)):
        polygon = contour_polygons[i]
        if not(polygon in contour_polygons_to_keep) and (point.within(polygon)):
            contour_polygons_to_keep.append(polygon)
            contours_to_keep.append(contours[i])    #for plotting reasons only
second_console.print("[2/2] Right click inside ONLY of the contours that you want to discard.")
fig, ax = plt.subplots()
fig.canvas.manager.set_window_title("Contour selection")
ax.imshow(masked_image)
ax.axis('off')
for contour in contours_to_keep:
    ax.plot(contour[:,1], contour[:,0], linewidth=2)
binding_id = plt.connect('button_press_event', on_click_remove)
plt.show()

main_console.print("\t[+] Filtering contours.")
limit = len(contour_polygons_to_keep)
for point in points_to_remove:
    i = 0
    while i < limit:
        polygon = contour_polygons_to_keep[i]
        if (point.within(polygon)):
            del(contour_polygons_to_keep[i])
            del(contours_to_keep[i])   #for plotting reasons only
            i -= 1
            limit -= 1
        i += 1
main_console.print("[+] You have selected {a} contours.".format(a=len(contours_to_keep)))
fig, ax = plt.subplots()
fig.canvas.manager.set_window_title("Final selected contour(s)")
ax.imshow(image)
ax.axis('off')
for contour in contours_to_keep:
    ax.plot(contour[:,1], contour[:,0], linewidth=2)
plt.show()

#STEP 4 - Convex hull of contours
#made using scipy and then passed to shapely for ease of use
main_console.print("[+] Calculating convex hulls")

#attempting calculation via shapely
convex_hulls_polygons = []
convex_hulls_vertices = []
for polygon in contour_polygons_to_keep:
    hull = polygon.convex_hull
    boundary_xy = hull.boundary.xy
    vertices = np.array(list(zip(boundary_xy[0], boundary_xy[1])))  #keep in mind that boundary.xy has the starting point twice (beggining and end)
    convex_hulls_polygons.append(hull)
    convex_hulls_vertices.append(vertices)   #they are in x,y format

fig, ax = plt.subplots()
fig.canvas.manager.set_window_title("Convex hulls")
ax.imshow(image)
ax.axis('off')
for hull in convex_hulls_vertices:
    ax.plot(hull[:,0], hull[:,1], linewidth=2)
plt.show()

#STEP 5 - Statistical analysis
#for each convex hull polygon create dictionary with key the wkb and as elements
#another dict with the following elements in this exact order:
#perimeter, area, number of sides, centroid, Polsby-Popper test, sub_areas, similarity vector (will be explained later)

main_console.print("[+] Analyzing data...")
polygon_data_dict = {}
for polygon in convex_hulls_polygons:
    polygon_key = polygon.wkb
    centroid = polygon.centroid
    #-1 on number of sides, because boundary has the starting point twice
    polygon_data_dict[polygon_key] = {'perimeter': polygon.length, 'area': polygon.area, 'sides': len(polygon.boundary.xy[0])-1 ,'centroid': np.array([centroid.x, centroid.y]), 'Polsby-Popper': (polygon.area*4*np.pi)/(polygon.length**2)}
main_console.print("[+] Computing shape data...")
for i in range(len(convex_hulls_polygons)):
    polygon_key = convex_hulls_polygons[i].wkb
    sides = polygon_data_dict[polygon_key]['sides']
    centroid = polygon_data_dict[polygon_key]['centroid']
    area = polygon_data_dict[polygon_key]['area']
    vertices = convex_hulls_vertices[i]
    
    sub_areas = []
    j = 1
    k = 0   #this works because vertices is generated from the boundary.xy function that starts and ends with the same point
    while j < len(vertices):
        sub_areas.append(shapely.Polygon([vertices[j], vertices[k], centroid]).area/area)
        j += 1
        k += 1
    sub_areas = np.array(sub_areas)
    polygon_data_dict[polygon_key]['sub_areas'] = sub_areas
    
    statistics = []
    for m in range(3, sides+1):
        #one sample wilcoxon signed rank test, that checks whether the median is
        #equal to the median of a regular polygon's sub_areas distr, with m sides
        temp = scipy.stats.wilcoxon(sub_areas-1/m)
        statistics.append(np.array([temp.statistic, temp.pvalue]))
    polygon_data_dict[polygon_key]['similarity_vector'] = np.array(statistics)

#STEP 6 - Presenting the data
#the user can click on a contour to get this contour's data
main_console.print("[+] Right click inside a shape to get data about it. You can close the image to get cumulative data about all the shapes.")

fig, ax = plt.subplots()
fig.canvas.manager.set_window_title("Pick a shape")
ax.imshow(image)
ax.axis('off')
for hull in convex_hulls_vertices:
    ax.plot(hull[:,0], hull[:,1], linewidth=2)
binding_id = plt.connect('button_press_event', get_polygon_data)
plt.show()

main_console.print("[+] Computing cumulative statistics...")
perimeters = []
areas = []
statistics = []
pvalues = []
for dictionary in list(polygon_data_dict.values()):
    perimeters.append(dictionary['perimeter'])
    areas.append(dictionary['area'])
    statistics.append(dictionary['similarity_vector'][:,0])
    pvalues.append(dictionary['similarity_vector'][:,1])

fig, ax = plt.subplots(2,2)
plt.subplots_adjust(top=0.924, bottom=0.074, hspace=0.25)
fig.canvas.manager.set_window_title("Cumulative stats")
ax[0][0].set_title("Perimeters (n={c})".format(c=len(perimeters)))
sns.histplot(perimeters, ax=ax[0][0], kde=True)
ax[0][1].set_title("Areas (n={c})".format(c=len(areas)))
sns.histplot(areas, ax=ax[0][1], kde=True)
ax[1][0].set_title("Wilcoxon stat.")
for stat in statistics:
    ax[1][0].plot(np.arange(3, len(stat)+3), stat)
ax[1][1].set_title("Wilcoxon p-val.")
for pval in pvalues:
    ax[1][1].plot(np.arange(3, len(pval)+3), pval)
colormap = plt.cm.jet
colors = [colormap(i) for i in np.linspace(0,1,len(ax[1][0].lines))]
for i, j in enumerate(ax[1][0].lines):
    j.set_color(colors[i])
for i, j in enumerate(ax[1][1].lines):
    j.set_color(colors[i])
plt.show()

confirmation = input("[Y/N] save stats to file? ")
if confirmation.strip().lower() == 'y':
    main_console.print("[+] Writing polygon data to file (out_polygons.json)...")
    filename = "out_polygons.json"
    keys = []
    values = []
    for idx, val in enumerate(list(polygon_data_dict.keys())):
        keys.append("POLYGON #{n}".format(n=idx+1))
        temp_dict = polygon_data_dict[val]
        values.append({'Perimeter':temp_dict['perimeter'], 'Area':temp_dict['area'], 'Sides':temp_dict['sides'], 'Centroid':temp_dict['centroid'].tolist(), 'Polsby-Popper':temp_dict['Polsby-Popper'], 'sub_areas':temp_dict['sub_areas'].tolist(), 'similarity_vector':temp_dict['similarity_vector'].tolist()})
    out_dict = dict(zip(keys, values))
    obj = json.dumps(out_dict, indent=4)
    with open(filename, 'w+') as f:
        f.write(obj)
        f.close()
    
    main_console.print("[+] Writing cumulative data to file (out_cumulative.json)...")
    filename = "out_cumulative.json"
    keys = ['Perimeters', 'Areas', 'Statistics', 'P-values']
    values = [perimeters, areas, [i.tolist() for i in statistics], [i.tolist() for i in pvalues]]
    out_dict = dict(zip(keys, values))
    obj = json.dumps(out_dict, indent=4)
    with open(filename, 'w+') as f:
        f.write(obj)
        f.close()
    main_console.print("[+] Written data to appropriate files.")