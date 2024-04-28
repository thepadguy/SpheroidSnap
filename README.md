# SpheroidSnap
Analysis in Python of photographs of spheroids from the optical microscope.

## About
**SpheroidSnap** is a script written in Python that analyzes the geometry of spheroids from photographs taken from an optical microscope (even with a regular smartphone through the lens!).

Utilizing publicly available python libraries such as [_scikit-image_](https://scikit-image.org/), [_numpy_](https://numpy.org), [_scipy_](https://scipy.org/), [_shapely_](https://github.com/shapely/shapely), etc. **SpheroidSnap** detects spheroids in your photos and calculates their **perimeter**, **area**, **circularity** and **quantifies** their likeness to a regular polygon in a quick and efficient way, while also giving you the option to output computed data to _.json_ file for further processing.

## Workings
Having [_scikit-image_](https://scikit-image.org/) as its main processing unit, **SpheroidSnap** reads the image specified by the user and turns it to **HSV colorspace**, where it applies a **triangle threshold** to the **saturation** channel, thus creating a mask that removes the white background from the spheroids. Afterwards, it detects **closed contours** on the masked image and guides the user on how to select only those that need to be studied and aren't noise.

In the next step, the **convex hull** of each selected **contour** is generated and analyzed with both [_scipy_](https://scipy.org/) and [_shapely_](https://github.com/shapely/shapely) modules. The analysis contains the calculation of the **perimeter**, **area**, **number of sides**, **centroid coordinates** and **circularity** via the **Polsby-Popper algorithm**.

Assuming that one of the forementioned **convex hulls** is an _irregular polygon_ with _n_ sides, then, if it was a _regular n-gon_, the area of all the triangles formed by joining the centroid to the vertices of each edge, would be equal with one another and with the total area divided by the number of sides. Thus, the mean and median of the distribution of those _fractional_ areas would be equal to _total area / n_. Based on this fact, **SpheroidSnap** computes the _"area distribution"_ for each **convex hull** and performs a **One sample Wilcoxon Signed Rank test** for the null hypothesis that the median of the difference of the _computed "area distribution"_ and the _"area distribution" of a regular n-gon_ (with _n_ less than or equal to the number of sides of the hull) is zero.

Finally, using [_matplotlib_](https://matplotlib.org) and [_seaborn_](https://seaborn.pydata.org/), **SpheroidSnap** presents the results to the user, in a concise and friendly interface, while also providing the option to save all generated results to a _.json_ file, using the eponymous Python module.

## Credits
**SpheroidSnap** was developed by undergraduates at the **University of Thessaly's Department of Veterinary Medicine** and is **free** to use in any way that promotes science and learning, as long as you cite the [github repository](https://github.com/thepadguy/SpheroidSnap) it resides in.

## The program
You can always download and run **SpheroidSnap** localy, however that requires that you have installed Python along with all the dependencies on your local computer. Since this may not always be something that an average non-programmer has, we provide another option.

You can run **SpheroidSnap** on the go! _How ?_ You can download the .ipunb file and run it on **Google Colab** (there are instruction on Google on how to do this). Along with uploading said file, upload the image you want to analyze in the same folder. Keep in mind that you might need to erase old analyzed images if the **Google Colab** space is full. Afterwards, run every cell consecutively and follow the instructions it shows. Keep in mind that you may need to manually install some packages using the command "%pip install packagename".
