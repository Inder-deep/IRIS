# IRIS
IRIS is a pyTesseract based OCR program. It takes an image as an input and then outputs the text into a txt file.

pyTesseract works best on images that have black text on a white background. The preprocessing function attempts to turn any image into this ideal scenario. 

The main control parameters are the last two inputs of the thresholding function. By changing these parameters the resulting image will have larger or smaller area of black pixels. This can be fine tuned to the type of images that are being processed. A 15% crop-in is applied to the input images but it can be disabled. 
