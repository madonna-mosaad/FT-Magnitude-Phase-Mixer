# Images Mixing

### **Overview**

The Images Viewer is a Python-based desktop application designed for viewing and manipulating four grayscale images simultaneously. Leveraging advanced image
processing techniques, the application provides users with intuitive controls to convert colored images to grayscale, unify image sizes, and explore Fourier
Transform (FT) components. The application is tailored for both casual users and professionals who require a sophisticated tool for image analysis and processing.

---

### **Video Demo**

https://github.com/user-attachments/assets/bcd43fdb-c188-4896-ae0c-0ced645d7ce7
   
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
    - The application features progress bars to indicate ongoing operations, with the ability to cancel an operation if a new mixing request is made while a previous
      one is still processing.

---

### **Application Interface**

Below are illustrative screenshots of the application showcasing its key features (replace the placeholders with actual images):

1. **Main Interface with Four Image Viewports**

   ![Screenshot 2025-01-07 005022](https://github.com/user-attachments/assets/ad4227fe-94de-49d4-b67d-933e2159e7ef)

2. **Fourier Transform Component Selection**

   ![Screenshot 2025-01-06 230255](https://github.com/user-attachments/assets/6dab3dc0-1eb7-4817-b60c-b965105dfcef)

3. **Brightness/Contrast Adjustment**

   ![Screenshot 2025-01-07 000339](https://github.com/user-attachments/assets/b65d1fe5-7ff8-4648-ac90-9015cc1300a7)

4. **Region Selection for FT Components**
   a-Inner Region

   ![Screenshot 2025-01-06 230117](https://github.com/user-attachments/assets/5469e2ae-6caa-4e11-882c-b36fb72628ae)
   b-Outer Region

   ![Screenshot 2025-01-06 230033](https://github.com/user-attachments/assets/00268d84-ff44-4d3e-b4be-91b603477dd1)

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

### **Shout out to the team**

- [Madonna Mosaad](https://github.com/madonna-mosaad)
- [Nancy Mahmoud](https://github.com/nancymahmoud1)
- [Yassien Tawfik](https://github.com/YassienTawfikk)
- [Youssef Taha](https://github.com/yousseftaha167)

---

### **Contact**

For any inquiries or feedback, please contact:

- **Name**: Madonna Mosaad
- **Email**: [Madonna.Mosaad03@eng-st.cu.edu.eg](mailto:Madonna.Mosaad03@eng-st.cu.edu.eg)
