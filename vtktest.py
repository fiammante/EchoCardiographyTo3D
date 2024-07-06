import vtk
import numpy as np
from vtk.util import numpy_support,vtkImageImportFromArray
from vtkmodules.vtkCommonDataModel import vtkImageData
from vtkmodules.vtkFiltersCore import (
    vtkFlyingEdges3D,
    vtkMarchingCubes
)
from vtkmodules.vtkFiltersSources import vtkSphereSource
from vtkmodules.vtkIOImage import vtkDICOMImageReader
from vtkmodules.vtkImagingHybrid import vtkVoxelModeller
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkPolyDataMapper,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer
)
from vtkmodules.vtkCommonColor import vtkNamedColors
import vtkmodules.all as vtk
import cv2
# read video file
# Sample anonymized echocardiography data (replace with your actual data)
videofile="./Anonymized_EchoCardiography06.mp4"
print("Read",videofile)
video = cv2.VideoCapture(videofile)
anonframes=[]
print("video opened",video.isOpened())
while(video.isOpened()):
    ret, frame = video.read()
    if ret == True:       
        anonframe= cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  
        anonframes.append(anonframe)
    else:
        break

image_data=np.stack(anonframes)
# Create a VTK image importer
image_importer = vtkImageImportFromArray.vtkImageImportFromArray()

# Set the array data to the importer
image_importer.SetArray(image_data)

colors = vtkNamedColors()

# Update the importer
image_importer.Update()

#  
surface = vtkMarchingCubes()
surface.SetInputData(image_importer.GetOutput()) 
surface.ComputeNormalsOn()
surface.SetValue(0,127)

renderer = vtkRenderer()
renderer.SetBackground(colors.GetColor3d('DarkSlateGray'))

render_window = vtkRenderWindow()
render_window.AddRenderer(renderer)
render_window.SetWindowName('MarchingCubes')

interactor = vtkRenderWindowInteractor()
interactor.SetRenderWindow(render_window)

mapper = vtkPolyDataMapper()
mapper.SetInputConnection(surface.GetOutputPort())
mapper.ScalarVisibilityOff()

actor = vtkActor()
actor.SetMapper(mapper)
actor.GetProperty().SetColor(colors.GetColor3d('MistyRose'))

renderer.AddActor(actor)

render_window.Render()
interactor.Start()