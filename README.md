# Images Mixing

### **Overview**
The Images Viewer is a Python-based desktop application designed for viewing and manipulating four grayscale images simultaneously. Leveraging advanced image processing techniques, the application provides users with intuitive controls to convert colored images to grayscale, unify image sizes, and explore Fourier Transform (FT) components. The application is tailored for both casual users and professionals who require a sophisticated tool for image analysis and processing.

![Project Overview](https://github.com/user-attachments/assets/431774f2-e1e2-4d62-b236-d05fdd59bbe0)

---
### **Video Demo**
   https://github.com/user-attachments/assets/a3f56a98-2a61-4528-80b4-d45b0698c641

---

### **Features**

1. **Multi-Image Viewing**:
   - Open and view four grayscale images in separate viewports.
   - Colored images are automatically converted to grayscale upon loading.

2. **Unified Sizing**:
   - All displayed images maintain the size of the smallest opened image, ensuring a coherent viewing experience.

3. **Fourier Transform Components**:
   - Each image viewport includes two displays:
     - A fixed display for the original image.
     - An interactive display that shows selectable FT components: 
       - FT Magnitude
       - FT Phase
       - FT Real
       - FT Imaginary

4. **Easy Image Browsing**:
   - Change any of the images by double-clicking on its viewport to open a file dialog for selection.

5. **Output Ports**:
   - Two output viewports are available to display the results of image mixing. Users can choose which viewport displays the resulting image.

6. **Brightness and Contrast Adjustment**:
   - Users can adjust the brightness and contrast of images using mouse dragging directly within any viewport.

7. **Components Mixer**:
   - Users can customize the weights of each image's Fourier Transform components via sliders, facilitating intuitive control over mixing processes.

8. **Regions Mixer**:
   - Select and highlight specific regions of interest within FT components, with options for inner (low frequencies) or outer (high frequencies) regions.
   - Adjustable region size through a slider or resize handles.

9. **Real-Time Mixing**:
   - The application features progress bars to indicate ongoing operations, with the ability to cancel an operation if a new mixing request is made while a previous one is still processing.

---

### **Application Interface**
Below are illustrative screenshots of the application showcasing its key features (replace the placeholders with actual images):

1. **Main Interface with Four Image Viewports**
   
   ![UI Interface](https://github.com/user-attachments/assets/63501866-b537-4a49-9997-77fe253a7de6)

2. **Fourier Transform Component Selection**
   
   ![FT Componenet Selection](https://github.com/user-attachments/assets/16980abe-bdcb-4e87-8d42-0061cd346183)

3. **Brightness/Contrast Adjustment**
   
   ![Brightness & Contrast](https://github.com/user-attachments/assets/b7d3ea2a-4185-4c65-977d-9a76b23bd9a3)
   
4. **Region Selection for FT Components**
   a-Inner Region
   ![Inner Region](https://github.com/user-attachments/assets/8c17a8a3-d8d8-435d-87ad-c41ed7559ba5)

   b-Outer Region
   ![Outer Region](https://github.com/user-attachments/assets/9f1d72fd-7241-449d-807b-0391c13a0e9a)

---

### **Setup and Installation**
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/madonna-mosaad/FT-Magnitude-Phase-Mixer.git
   ```
2. **Navigate to the Project Directory**:
   ```bash
   cd FT-Magnitude-Phase-Mixer
   ```
3. **Install Required Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Run the Application**:
   ```bash
   python Main.py
   ```

---

### **Usage Instructions**
1. Launch the application and use the browse function by double-clicking a viewport to load image files.
2. Adjust the viewing size and customize image brightness and contrast as desired.
3. Select Fourier Transform components for analysis and perform mixing using the components mixer.
4. Use the regions mixer to pick areas of interest for low or high-frequency analysis.

---

## Contributors
<div>
<table align="center">
  <tr>
        <td align="center">
      <a href="https://github.com/YassienTawfikk" target="_blank">
        <img src="https://avatars.githubusercontent.com/u/126521373?v=4" width="150px;" alt="Yassien Tawfik"/>
        <br />
        <sub><b>Yassien Tawfik</b></sub>
      </a>
    </td>
    <td align="center">
      <a href="https://github.com/madonna-mosaad" target="_blank">
        <img src="https://avatars.githubusercontent.com/u/127048836?v=4" width="150px;" alt="Madonna Mosaad"/>
        <br />
        <sub><b>Madonna Mosaad</b></sub>
      </a>
    </td>
        <td align="center">
      <a href="https://github.com/nancymahmoud1" target="_blank">
        <img src="https://avatars.githubusercontent.com/u/125357872?v=4" width="150px;" alt="Nancy Mahmoud"/>
        <br />
        <sub><b>Nancy Mahmoud</b></sub>
      </a>
    </td>
    </td>
        <td align="center">
      <a href="https://github.com/yousseftaha167" target="_blank">
        <img src="https://avatars.githubusercontent.com/u/128304243?v=4" width="150px;" alt="Youssef Taha"/>
        <br />
        <sub><b>Youssef Taha</b></sub>
      </a>
    </td>    
  </tr>
</table>
</div>
